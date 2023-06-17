import h2p.frame

from h2p.stream import Stream
from h2p.error import ErrorCodes, error_code_enum_to_str
from hpack import Decoder
from h2p.utilities import bytes_to_error_code, bits_to_int, bytes_concat
import abc


class FrameType:

    def __init__(self, frame_type, header, flag=None):
        self.type = frame_type
        self.header = header
        self.data = ""
        if flag:
            self.flag = self.parse_flag(flag)

    def parse_flag(self, flag):
        return {
            "END_STREAM": flag & 0x1 == 1,
            "END_HEADERS": flag & 0x4 == 1,
            "PADDED": flag & 0x8 == 1,
            "PRIORITY": flag & 0x20 == 1
        }

    @abc.abstractmethod
    def parse(self, payload):
        return

    def get_data(self):
        return {
            "header": self.header,
            "frame_type": self.type,
            "data": self.data
        }


class GoawayFrame(FrameType):
    def __init__(self, payload, header):
        super(GoawayFrame, self).__init__("GOAWAY", header=header)
        self.data = self.parse(payload)

    def parse(self, payload):
        """
        Note that Additional Debug Data has not been transferred, because its type is unknown.
        :param payload: a byte array
        :return:
        """
        last_stream_id = Stream.parse_stream(payload[:4][::-1])
        error_code = bytes_to_error_code(payload[4:8])
        additional_data = payload[8:]
        return {
            "Last-Stream-ID": last_stream_id,
            "Error Code": error_code_enum_to_str.get(error_code, "UNKNOWN"),
            "Additional Debug Data": additional_data
        }


class WindowUpdateFrame(FrameType):
    def __init__(self, payload, header):
        super(WindowUpdateFrame, self).__init__("WINDOW_UPDATE", header=header)
        self.data = self.parse(payload)

    def parse(self, payload):
        window_size_increment = WindowUpdateFrame.parse_window_size(payload)
        return {
            "Window Size Increment": window_size_increment
        }

    @staticmethod
    def parse_window_size(data):
        bits = []
        for byte in data[::-1]:
            for i in range(8):
                bits.append((ord(byte) >> i) & 1)
        # bits.reverse()
        bits.pop(-1)
        return bits_to_int(bits)


class PriorityFrame(FrameType):
    def __init__(self, payload, header):
        super(PriorityFrame, self).__init__("PRIORITY", header=header)
        self.is_exclusive = False
        self.data = self.parse(payload)

    def parse(self, payload):
        if not self.flag["PRIORITY"]:
            return None
        self.is_exclusive = ((ord(payload[0]) >> 7) & 1) == 1
        stream_dependency_id = Stream.parse_stream(payload[:4][::-1])
        weight = ord(payload[4])
        return {
            "is_exclusive": self.is_exclusive,
            "Stream Dependency": stream_dependency_id,
            "Weight": weight
        }


class RstStreamFrame(FrameType):
    def __init__(self, payload, header):
        super(RstStreamFrame, self).__init__("RST_STREAM", header=header)
        self.data = self.parse(payload)

    def parse(self, payload):
        error_code = bytes_to_error_code(payload)
        return {
            "Error Code": error_code_enum_to_str.get(error_code, "UNKNOWN")
        }


class SettingsFrame(FrameType):
    SETTINGS_TYPES = {
        0x1: 'SETTINGS_HEADER_TABLE_SIZE',
        0x2: 'SETTINGS_ENABLE_PUSH',
        0x3: 'SETTINGS_MAX_CONCURRENT_STREAMS',
        0x4: 'SETTINGS_INITIAL_WINDOW_SIZE',
        0x5: 'SETTINGS_MAX_FRAME_SIZE',
        0x6: 'SETTINGS_MAX_HEADER_LIST_SIZE'
    }

    def __init__(self, payload, header):
        super(SettingsFrame, self).__init__("SETTINGS", header=header)
        self.data = self.parse(payload)

    def parse(self, payload):
        payload = bytes_concat(payload)
        settings = {}
        while len(payload) > 0:
            settings_id = int.from_bytes(payload[:2], byteorder='big')
            settings_key = SettingsFrame.SETTINGS_TYPES.get(settings_id, 'ERROR')
            settings_value = int.from_bytes(payload[2:6], byteorder='big')
            payload = payload[6:]
            settings[settings_key] = settings_value
        return settings


class DataFrame(FrameType):
    def __init__(self, payload, header):
        super(DataFrame, self).__init__("DATA", header=header)
        self.data = self.parse(payload)

    def parse(self, payload):
        payload = bytes_concat(payload)
        text = ""
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError:
            text = str(payload)
        return text


class PushPromiseFrame(FrameType):
    def __init__(self, payload, decoder, flag, header):
        super(PushPromiseFrame, self).__init__("PUSH_PROMISE", header=header, flag=flag)
        self.decoder = decoder
        self.data = self.parse(payload)

    def parse(self, payload):
        data = {}
        end_len = len(payload)
        if self.flag["PADDED"]:
            data['Pad Length'] = ord(payload[0])
            payload = payload[1:]
            end_len -= data['Pad Length']
            if end_len < 4:
                raise ValueError("Format is not valid!")

        data["Promised Stream ID"] = Stream.parse_stream(payload[:4][::-1])

        data["Header Block Fragment"] = HeadersFrame.parse_headers_blocks(payload[4:end_len])
        return data


class PingFrame(FrameType):
    def __init__(self, payload, header):
        super(PingFrame, self).__init__("PING", header=header)
        self.data = self.parse(payload)

    def parse(self, payload):
        payload = bytes_concat(payload)
        return {"pong": bytes.hex(payload)}


class HeadersFrame(FrameType):
    def __init__(self, payload, flag, decoder: Decoder, header):
        super(HeadersFrame, self).__init__("HEADERS", header=header, flag=flag)
        self.decoder = decoder
        self.data = self.parse(payload)

    def parse(self, payload):
        end_len = len(payload)
        data = {}
        if self.flag["PADDED"]:
            data['Pad Length'] = ord(payload[0])
            payload = payload[1:]
            end_len -= data['Pad Length']
            if end_len < 4:
                raise ValueError("Format is not valid!")
        if self.flag["PRIORITY"]:
            data["Stream Dependency"] = Stream.parse_stream(payload[:4][::-1])
            data["Weight"] = ord(payload[4])
            payload = payload[5:]
        data["Header Block Fragment"] = HeadersFrame.parse_headers_blocks(self.decoder, payload)
        return data

    @staticmethod
    def parse_headers_blocks(decoder, payload):
        payload = bytes_concat(payload)
        headers = {}
        for key, value in decoder.decode(payload):
            headers[key] = value
        return headers


class ContinuationFrame(FrameType):
    def __init__(self, payload, decoder: Decoder, header):
        super(ContinuationFrame, self).__init__("CONTINUATION", header=header)
        self.decoder = decoder
        self.data = self.parse(payload)
        # FrameFactory

    def parse(self, payload):
        return HeadersFrame.parse_headers_blocks(self.decoder, payload)


