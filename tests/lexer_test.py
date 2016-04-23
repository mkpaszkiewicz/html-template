import unittest
import unittest.mock

from html_template_parser import SourceController


class SourceControllerTest(unittest.TestCase):
    """Class tests SourceController class"""
    FILE_CONTENT = 'exemplary content\nsecond line\n'

    def run(self, result=None):
        # Mock built in open() function
        # open is mocked in every test case
        mocked_open = unittest.mock.mock_open(read_data=self.FILE_CONTENT)
        mocked_open.return_value.__next__ = lambda self: self.readline()
        with unittest.mock.patch('html_template_parser.lexer.open', mocked_open, create=True):
            super(SourceControllerTest, self).run(result)

    def test_buffer_should_be_empty_before_first_get_char(self):
        with SourceController('anything') as source_controller:
            self.assertTrue(source_controller._is_empty_buffer(), 'Buffer instead of being empty contains '
                            + source_controller.buffer)
            self.assertEqual(source_controller.buffer, '')

    def test_should_return_file_content(self):
        with SourceController('anything') as source_controller:
            try:
                i = 0
                while True:
                    char = source_controller.get_char()
                    self.assertEqual(char, self.FILE_CONTENT[i])
                    i += 1
            except StopIteration:
                # After mocking the built in open function, at end of file it
                # raises StopIteration instead of returning None
                pass

    def test_should_update_position(self):
        with SourceController('anything') as source_controller:
            try:
                i = 0
                line_number = 1
                position_number = 1
                while True:
                    char = source_controller.get_char()
                    msg = 'Got ' + char + ' instead of ' + self.FILE_CONTENT[i] +\
                          ' on line: ' + str(line_number) + ' pos: ' + str(position_number)
                    self.assertEqual(source_controller.line_number, line_number, msg)
                    self.assertEqual(source_controller.position_number, position_number, msg)
                    if self.FILE_CONTENT[i] == '\n':
                        line_number += 1
                        position_number = 1
                    else:
                        position_number += 1
                    i += 1
            except StopIteration:
                # After mocking the built in open function, at end of file it
                # raises StopIteration instead of returning None
                pass


if __name__ == '__main__':
    unittest.main()
