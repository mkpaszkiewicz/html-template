class SourceController:
    """Class reads from input stream and place characters in buffer.
    Stores information about line and position."""

    def __init__(self, source):
        self.line_number = 0
        self.position_number = 0
        self.buffer = ''
        self._source = source

    def __enter__(self):
        self._input = open(self._source, 'r')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._input.close()

    def get_char(self):
        """Returns character from source and None if end of file"""
        if self._is_empty_buffer() and not self._next_line():
            return None
        result = self.buffer[self.position_number]
        self.position_number += 1
        return result

    def _next_line(self):
        """Reads next line and place it in buffer. Returns the buffer."""
        self.buffer = self._input.readline()
        self.line_number += 1
        self.position_number = 0
        return self.buffer

    def _is_empty_buffer(self):
        return not self.position_number < len(self.buffer)
