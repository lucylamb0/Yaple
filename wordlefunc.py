import logging

import requests
import os
import json
import datetime
import csv
from __init_logging__ import *

usablewords = []
with open("UsableGuesses.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        for word in row:
            usablewords.append(word.strip().upper())

logger.info(f"Loaded {len(usablewords)} usable words.")

class Board:
    def __init__(self):
        self.rows = [self.Row() for _ in range(6)]
        self.current_row : int = 0
        self.is_complete = False
        self.date = datetime.date.today().isoformat()

    def from_dict(data):
        board = Board()
        board.current_row = data.get("current_row", 0)
        board.is_complete = data.get("is_complete", False)
        board.date = data.get("date", datetime.date.today().isoformat())
        rows_data = data.get("rows", [])
        for i in range(min(len(rows_data), 6)):
            row_data = rows_data[i]
            row = Board.Row()
            row.correct = row_data.get("correct", 0)
            row.present = row_data.get("present", 0)
            row.absent = row_data.get("absent", 0)
            letters_data = row_data.get("state", [])
            for j in range(min(len(letters_data), 5)):
                letter_data = letters_data[j]
                letter = Board.Row.Letter()
                letter.char = letter_data.get("char", "")
                letter.status = letter_data.get("status", None)
                row.state[j] = letter
            board.rows[i] = row
        return board

    def to_dict(self):
        return {
            "current_row": self.current_row,
            "is_complete": self.is_complete,
            "date": self.date,
            "rows": [
                {
                    "correct": row.correct,
                    "present": row.present,
                    "absent": row.absent,
                    "state": [
                        {
                            "char": letter.char,
                            "status": letter.status
                        } for letter in row.state
                    ]
                } for row in self.rows
            ]
        }

    def userGuess(self, guess):
        global usablewords
        global wordOfTheDay

        result = ""
        if wordOfTheDay is None:
            wordOfTheDay = getWordOfTheDay()
        if wordOfTheDay is None:
            result = "Error fetching the word of the day."
            return result

        guess = guess.upper()
        if len(guess) != 5 or not guess.isalpha():
            result = "Please enter a valid 5-letter word."
            return result

        if self.is_complete:
            result = "The game is already complete. Please start a new game."
            return result

        current_row_no = self.current_row
        if current_row_no >= 6:
            result = "No more attempts left. The game is over."
            self.is_complete = True
            return result

        if guess not in usablewords:
            result = f"Your guess is not in the list of usable words. Please try again."
            return result

        self.__guess(guess)
        result = self.display()
        if self.is_complete:
            result = result + "\nCongratulations! You've guessed the word correctly!"
            logging.debug(f"A user guessed the word {wordOfTheDay} correctly.")
            return result
        return result


    def __guess(self, word : str):
        global wordOfTheDay
        # Validate input
        if len(wordOfTheDay) != 5 or not wordOfTheDay.isalpha():
            return
        if self.is_complete or self.current_row >= 6:
            return
        if len(word) != 5 or not word.isalpha():
            return

        word = word.upper()
        wordOfTheDay = wordOfTheDay.upper()

        for i in range(5):
            # Set the character and determine its status
            self.rows[self.current_row].state[i].char = word[i]
            if word[i] == wordOfTheDay[i]:
                self.rows[self.current_row].state[i].status = self.Row.Letter.Status.CORRECT
                self.rows[self.current_row].correct += 1
            elif word[i] in wordOfTheDay:
                self.rows[self.current_row].state[i].status = self.Row.Letter.Status.PRESENT
                self.rows[self.current_row].present += 1
            else:
                self.rows[self.current_row].state[i].status = self.Row.Letter.Status.ABSENT
                self.rows[self.current_row].absent += 1
        if self.rows[self.current_row].correct == 5:
            self.is_complete = True
        self.current_row += 1


    def display(self):
        display_str = ""
        for row in self.rows:
            for letter in row.state:
                if letter.status == self.Row.Letter.Status.CORRECT:
                    display_str += "🟩"
                elif letter.status == self.Row.Letter.Status.PRESENT:
                    display_str += "🟨"
                elif letter.status == self.Row.Letter.Status.ABSENT:
                    display_str += "⬛"
                else:
                    display_str += "     "
            display_str += "\n"
        return display_str

    class Row:
        def __init__(self):
            self.correct = 0
            self.present = 0
            self.absent = 0
            self.state = [self.Letter() for _ in range(5)]

        class Letter:
            def __init__(self):
                self.char = ""
                self.status = None

            class Status:
                CORRECT = "correct"
                PRESENT = "present"
                ABSENT = "absent"


global wordOfTheDay
wordOfTheDay = None
def getWordOfTheDay():
    url = "https://www.nytimes.com/svc/wordle/v2/"+ str(datetime.date.today()) +".json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['solution'].upper()
    logging.error(f"Failed to fetch the word of the day. Status code: {response.status_code}")
    return None
