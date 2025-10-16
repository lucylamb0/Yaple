import unittest
from main import YappleUser, Board, getWordOfTheDay
import datetime


class TestTimePassing(unittest.TestCase):
    def setUp(self):
        self.user1 = YappleUser("test_user")
        self.user1.board.current_row = 3
        self.user1.board.is_complete = True
        self.user1.board.started = True
        self.user1.board.date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        self.user1.stats = {
            "games_played": 5,
            "current_streak": 2,
            "max_streak": 4,
            "guess_distribution": [0, 1, 1, 1, 1, 0, 1]
        }

        self.user2 = YappleUser("test_user2")
        self.user2.board.current_row = 4
        self.user2.board.is_complete = False
        self.user2.board.date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        self.user2.board.started = True
        self.user2.stats = {
            "games_played": 5,
            "current_streak": 2,
            "max_streak": 4,
            "guess_distribution": [0, 1, 1, 1, 1, 0, 1]
        }

        self.user3 = YappleUser("test_user3")
        self.user3.board.current_row = 2
        self.user3.board.is_complete = True
        self.user3.board.date = datetime.date.today().isoformat()
        self.user3.board.started = True
        self.user3.stats = {
            "games_played": 5,
            "current_streak": 2,
            "max_streak": 4,
            "guess_distribution": [0, 1, 1, 1, 1, 0, 1]
        }

        self.user4 = YappleUser("test_user4")
        self.user4.board.current_row = 0
        self.user4.board.is_complete = False
        self.user4.board.date = datetime.date.today().isoformat()
        self.user4.board.started = False
        self.user4.stats = {
            "games_played": 2,
            "current_streak": 2,
            "max_streak": 2,
            "guess_distribution": [0, 2, 0, 0, 0, 0, 0]
        }

    def test_check_date_resets_board_and_streak(self):
        self.user1.check_date()
        self.assertEqual(self.user1.board.current_row, 0)
        self.assertFalse(self.user1.board.is_complete)
        self.assertEqual(self.user1.stats["current_streak"], 2)
        self.assertEqual(self.user1.stats["games_played"], 5)
        self.assertEqual(self.user1.stats["guess_distribution"][2], 1)
        self.assertEqual(self.user1.board.date, datetime.date.today().isoformat())

        self.user2.check_date()
        self.assertEqual(self.user2.board.current_row, 0)
        self.assertFalse(self.user2.board.is_complete)
        self.assertEqual(self.user2.stats["current_streak"], 0)
        self.assertEqual(self.user2.stats["games_played"], 6)
        self.assertEqual(self.user2.stats["guess_distribution"][6], 2)
        self.assertEqual(self.user2.board.date, datetime.date.today().isoformat())

        self.user3.check_date()
        self.assertEqual(self.user3.board.current_row, 2)
        self.assertTrue(self.user3.board.is_complete)
        self.assertEqual(self.user3.stats["current_streak"], 2)
        self.assertEqual(self.user3.stats["games_played"], 5)
        self.assertEqual(self.user3.stats["guess_distribution"][2], 1)
        self.assertEqual(self.user3.board.date, datetime.date.today().isoformat())

        self.user4.check_date()
        self.assertEqual(self.user4.board.current_row, 0)
        self.assertFalse(self.user4.board.is_complete)
        self.assertEqual(self.user4.stats["current_streak"], 2)
        self.assertEqual(self.user4.stats["games_played"], 2)
        self.assertEqual(self.user4.stats["guess_distribution"][1], 2)
        self.assertEqual(self.user4.board.date, datetime.date.today().isoformat())


    def check_word_of_the_day_changes(self):
        word_today = getWordOfTheDay()
        word_yesterday = "TESTY"  # Mock previous word
        self.assertNotEqual(word_today, word_yesterday)
        self.assertEqual(word_today, self.user3.board.solution)


class TestStatsDisplay(unittest.TestCase):
    def test_display_stats(self):
        user = YappleUser("stat_user")
        user.stats = {
            "games_played": 10,
            "current_streak": 3,
            "max_streak": 7,
            "guess_distribution": [0, 2, 3, 1, 2, 1, 1]
        }
        stats_message = user.display_stats()
        self.assertIn("Games Played: 10", stats_message)
        self.assertIn("Current Streak: 3 🔥", stats_message)
        self.assertIn("Max Streak: 7", stats_message)
        self.assertIn("1/6: 0", stats_message)
        self.assertIn("2/6: 2", stats_message)
        self.assertIn("3/6: 3", stats_message)
        self.assertIn("4/6: 1", stats_message)
        self.assertIn("5/6: 2", stats_message)
        self.assertIn("6/6: 1", stats_message)
        self.assertIn("X/6: 1", stats_message)


class TestBoardSerialization(unittest.TestCase):
    def test_board_serialization(self):
        board = Board()
        board.current_row = 2
        board.is_complete = True
        board.date = "2024-06-01"
        board.rows[0].state[0].char = 'H'
        board.rows[0].state[0].status = 'correct'
        board.rows[0].state[1].char = 'E'
        board.rows[0].state[1].status = 'present'
        board.rows[0].state[2].char = 'L'
        board.rows[0].state[2].status = 'absent'
        board.absent_letters = ['A', 'B']
        board.present_letters = ['C', 'D']
        board.correct_letters = ['E', 'F']
        board.used_letters = ['A', 'B', 'C', 'D', 'E', 'F']

        board_dict = board.to_dict()
        new_board = Board.from_dict(board_dict)

        self.assertEqual(new_board.current_row, 2)
        self.assertTrue(new_board.is_complete)
        self.assertEqual(new_board.date, "2024-06-01")
        self.assertEqual(new_board.rows[0].state[0].char, 'H')
        self.assertEqual(new_board.rows[0].state[0].status, 'correct')
        self.assertEqual(new_board.rows[0].state[1].char, 'E')
        self.assertEqual(new_board.rows[0].state[1].status, 'present')
        self.assertEqual(new_board.rows[0].state[2].char, 'L')
        self.assertEqual(new_board.rows[0].state[2].status, 'absent')
        self.assertEqual(new_board.absent_letters, ['A', 'B'])
        self.assertEqual(new_board.present_letters, ['C', 'D'])
        self.assertEqual(new_board.correct_letters, ['E', 'F'])
        self.assertEqual(new_board.used_letters, ['A', 'B', 'C', 'D', 'E', 'F'])


class TestUserSerialization(unittest.TestCase):
    def test_user_serialization(self):
        user = YappleUser("serialize_user")
        user.board.current_row = 4
        user.board.is_complete = False
        user.board.date = "2024-06-01"
        user.board.absent_letters = ['A', 'B', 'C']
        user.board.present_letters = ['D', 'E']
        user.board.correct_letters = ['F', 'G', 'H']
        user.board.used_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        user.stats = {
            "games_played": 15,
            "current_streak": 5,
            "max_streak": 10,
            "guess_distribution": [1, 2, 3, 4, 2, 1, 2]
        }
        user.board.rows[0].state[0].char = 'W'
        user.board.rows[0].state[0].status = 'correct'
        user.board.rows[0].state[1].char = 'O'
        user.board.rows[0].state[1].status = 'present'
        user.board.rows[0].state[2].char = 'R'
        user.board.rows[0].state[2].status = 'absent'

        user_dict = user.to_dict()
        new_user = YappleUser.from_dict(user_dict)

        self.assertEqual(new_user.user_id, "serialize_user")
        self.assertEqual(new_user.board.current_row, 4)
        self.assertFalse(new_user.board.is_complete)
        self.assertEqual(new_user.board.date, "2024-06-01")
        self.assertEqual(new_user.stats["games_played"], 15)
        self.assertEqual(new_user.stats["current_streak"], 5)
        self.assertEqual(new_user.stats["max_streak"], 10)
        self.assertEqual(new_user.stats["guess_distribution"], [1, 2, 3, 4, 2, 1, 2])
        self.assertEqual(new_user.board.rows[0].state[0].char, 'W')
        self.assertEqual(new_user.board.rows[0].state[0].status, 'correct')
        self.assertEqual(new_user.board.rows[0].state[1].char, 'O')
        self.assertEqual(new_user.board.rows[0].state[1].status, 'present')
        self.assertEqual(new_user.board.rows[0].state[2].char, 'R')
        self.assertEqual(new_user.board.rows[0].state[2].status, 'absent')
        self.assertEqual(new_user.board.absent_letters, ['A', 'B', 'C'])
        self.assertEqual(new_user.board.present_letters, ['D', 'E'])
        self.assertEqual(new_user.board.correct_letters, ['F', 'G', 'H'])
        self.assertEqual(new_user.board.used_letters, ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])



if __name__ == '__main__':
    unittest.main()
