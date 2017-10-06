import asyncio
from robomodules.comm.serverProto import ServerProto
from robomodules.messages.subscribe_pb2 import Subscribe
from robomodules.messages.types import MsgType, message_buffers

class Server():
    def __init__(self, addr, port):
        self.loop = asyncio.get_event_loop()
        self.clients = []
        self.subs = {}

        coro = self.loop.create_server(lambda: ServerProto(self), addr, port)
        self.server = self.loop.run_until_complete(coro)

    def _handle_subscriptions(self, protocol, data):
        if data.dir == Subscribe.SUBSCRIBE:
            self._add_subscriptions(protocol, data)
        else:
            self._remove_subscriptions(protocol, data)

    def _remove_subscriptions(self, protocol, data):
        for msg_type in data.msg_types:
            m_type = MsgType(msg_type)
            if m_type in self.subs:
                self.subs[m_type].remove(protocol)

    def _add_subscriptions(self, protocol, data):
        for msg_type in data.msg_types:
            m_type = MsgType(msg_type)
            if m_type in self.subs:
                self.subs[m_type].append(protocol)
            else:
                self.subs[m_type] = [protocol]

    def _forward_msg(self, msg, msg_type):
        if msg_type in self.subs:
            for protocol in self.subs[msg_type]:
                protocol.write(msg, msg_type)

    def remove_client(self, protocol):
        self.clients.remove(protocol)
        for msg_type in self.subs:
            if protocol in self.subs[msg_type]:
                self.subs[msg_type].remove(protocol)

    def msg_received(self, protocol, msg, msg_type):
        if msg_type == MsgType.SUBSCRIBE:
            data = message_buffers[msg_type]()
            data.ParseFromString(msg)
            self._handle_subscriptions(protocol, data)
        else:
            self._forward_msg(msg, msg_type)

    def quit(self):
        self.loop.stop()

    def run(self):
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.quit()
