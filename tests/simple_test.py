import unittest


class SimpleTest(unittest.TestCase):
    """Class provides simple test"""


    def test_should_count_sum(self):
        """Test comment"""
        self.assertEqual(5, 2 + 3)


if __name__ == '__main__':
    unittest.main()
