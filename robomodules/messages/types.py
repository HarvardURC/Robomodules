from enum import Enum
from .mockMsg_pb2 import MockMsg
from .subscribe_pb2 import Subscribe

class MsgType(Enum):
    SUBSCRIBE = 0
    MOCK_MSG = 1

message_buffers = {
    MsgType.SUBSCRIBE: Subscribe,
    MsgType.MOCK_MSG: MockMsg
}


