import struct
from h2p.error import ErrorCodes
from h2p.factory import FrameFactory
from h2p.frames import *
from h2p.stream import Stream
from hpack import Decoder
import json
import binascii


class Frame(object):
    ''' Define an HTTP2 Frame Class '''

    ### - Class Constants -- ###
    FRAME_TYPES = {
        0x0: 'DATA',
        0x1: 'HEADERS',
        0x2: 'PRIORITY',
        0x3: 'RST_STREAM',
        0x4: 'SETTINGS',
        0x5: 'PUSH_PROMISE',
        0x6: 'PING',
        0x7: 'GOAWAY',
        0x8: 'WINDOW_UPDATE',
        0x9: 'CONTINUATION'
    }

    def __init__(self, header, payload, parser):
        self.header = header
        self.payload = payload
        self.type = header['type']
        self.parser = parser
        self.text_data = self.parser.parser(self.type, payload, header, self.header['flags'])

    def __len__(self):
        ''' Return the length of the frame '''
        return self.header['length']

    def __str__(self):
        ''' Return a string representation of the frame '''
        return self.__repr__()

    def __repr__(self):
        ''' Return a string representation of the frame '''
        # TODO: Improve!
        return 'HTTP2 Frame of type %s' % str(self.type)

    def print_info(self):
        print('Frame Length: %s' % str(self.header['length']))
        print('Frame Type: %s' % str(self.type))
        print('Flags: %s' % format(self.header['flags'], '#010b'))
        print('Stream ID: %i' % self.header['stream'])
        print("Payload: %s" % self.text_data)

    @staticmethod
    def parse_header(header):
        ''' Parse the header of a frame '''
        frame_length = sum(struct.unpack('hB', header[:3]))
        if frame_length == 1702:
            print(struct.unpack('hb', header[:3]))
        header = header[3:]
        frame_type = Frame.FRAME_TYPES.get(
            struct.unpack('b', header[:1])[0],
            'ERROR'
        )
        header = header[1:]
        frame_flags = struct.unpack('b', header[:1])[0]
        header = header[1:]
        frame_stream = struct.unpack('cccc', header[:4])[::-1]
        stream_id = Stream.parse_stream(frame_stream)

        header = {
            'length': frame_length,
            'type': frame_type,
            'flags': frame_flags,
            'stream': stream_id
        }

        return header


class Parser:
    def __init__(self):
        self.decoder = Decoder()

    def parser(self, frame_type, payload, header, flag=None):
        # payload = b"".join(payload)
        kwargs = {'payload': payload, "header": header}
        if frame_type in ["HEADERS", "CONTINUATION"]:
            kwargs['decoder'] = self.decoder
        if frame_type in ["PUSH_PROMISE", "HEADERS"]:
            kwargs["flag"] = flag
        frame = FrameFactory(frame_type, kwargs=kwargs)
        return frame.get_data()





