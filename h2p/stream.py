from h2p.utilities import bits_to_int


class Stream(object):
    ''' Define an HTTP2 Stream Class '''

    def __init__(self, stream_id):
        self.id = stream_id
        self.frames = []

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        ''' Returns a string representation of the stream '''
        return 'HTTP2 Stream #%s' % str(self.id)

    def __iter__(self):
        for frame in self.frames:
            yield frame

    def add_frame(self, frame):
        ''' Add a frame to the stream '''
        self.frames.append(frame)

    @staticmethod
    def parse_stream(stream_data):
        ''' Parse the Stream ID '''
        bits = []
        for byte in stream_data:
            for i in range(8):
                bits.append((ord(byte) >> i) & 1)
        # Get rid of the reserved bit
        bits.pop(-1)
        return bits_to_int(bits)
