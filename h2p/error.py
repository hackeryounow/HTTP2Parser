from enum import Enum

# from dpkt.http2 import FrameFactory


class ErrorCodes(Enum):
    """
    错误代码是在 RST_STREAM 和 GOAWAY 帧中使用的 32 位字段，用于表示流或连接错误的原因。
    详细含义参考：https://github.com/halfrost/Halfrost-Field/blob/master/contents/Protocol/HTTP:2-HTTP-Frames-Definitions.md#%E5%8D%81%E4%B8%80-error-codes
    """
    NO_ERROR = 0x0
    PROTOCOL_ERROR = 0x01
    INTERNAL_ERROR = 0x2
    FLOW_CONTROL_ERROR = 0x03
    SETTINGS_TIMEOUT = 0x04
    STREAM_CLOSED = 0x05
    FRAME_SIZE_ERROR = 0x06
    REFUSED_STREAM = 0x07
    CANCEL = 0x08
    COMPRESSION_ERROR = 0x09
    CONNECT_ERROR = 0x0a
    ENHANCE_YOUR_CALM = 0x0b
    INADEQUATE_SECURITY = 0x0c
    HTTP_1_1_REQUIRED = 0x0d


error_code_enum_to_str = {
    ErrorCodes.NO_ERROR: "NO_ERROR",
    ErrorCodes.PROTOCOL_ERROR: "PROTOCOL_ERROR",
    ErrorCodes.INTERNAL_ERROR: "INTERNAL_ERROR",
    ErrorCodes.FLOW_CONTROL_ERROR: "FLOW_CONTROL_ERROR",
    ErrorCodes.STREAM_CLOSED: "STREAM_CLOSED",
    ErrorCodes.FRAME_SIZE_ERROR: "FRAME_SIZE_ERROR",
    ErrorCodes.REFUSED_STREAM: "REFUSED_STREAM",
    ErrorCodes.CANCEL: "CANCEL",
    ErrorCodes.COMPRESSION_ERROR: "COMPRESSION_ERROR",
    ErrorCodes.ENHANCE_YOUR_CALM: "ENHANCE_YOUR_CALM",
    ErrorCodes.INADEQUATE_SECURITY: "INADEQUATE_SECURITY",
    ErrorCodes.HTTP_1_1_REQUIRED: "HTTP_1_1_REQUIRED",
}
