import asyncio
from robomodules.comm.serverProto import ServerProto
from robomodules.comm.udpServerProto import UdpServerProto
from robomodules.comm.subscribe_pb2 import Subscribe
from robomodules.comm.constants import _SUBSCRIBE

class Server():
    def __init__(self, addr, tcp_port, udp_port, MsgType):
        self.loop = asyncio.get_event_loop()
        self.clients = []
        self.tcp_subs = {}
        self.udp_subs = {}
        self.MsgType = MsgType

        tcp_coro = self.loop.create_server(lambda: ServerProto(self), addr, tcp_port)
        udp_coro = self.loop.create_datagram_endpoint(lambda: UdpServerProto(self), local_addr=(addr, udp_port))
        self.tcp_server = self.loop.run_until_complete(tcp_coro)
        self.udp_server = self.loop.run_until_complete(udp_coro)

    def _handle_subscriptions(self, protocol, data):
        if data.dir == Subscribe.SUBSCRIBE:
            self._add_subscriptions(protocol, data)
        else:
            self._remove_subscriptions(protocol, data)

    def _remove_subscriptions(self, protocol, data):
        for msg_type in data.msg_types:
            m_type = self.MsgType(msg_type)
            subs_arr = self.tcp_subs if data.protocol == Subscribe.TCP else self.udp_subs
            if m_type in subs_arr:
                subs_arr[m_type].remove(protocol)

    def _add_subscriptions(self, protocol, data):
        for msg_type in data.msg_types:
            m_type = self.MsgType(msg_type)
            subs_arr = self.tcp_subs if data.protocol == Subscribe.TCP else self.udp_subs
            if m_type in subs_arr:
                subs_arr[m_type].append(protocol)
            else:
                subs_arr[m_type] = [protocol]

    def _forward_msg(self, msg, msg_type):
        m_type = self.MsgType(msg_type)
        for subs in [self.tcp_subs, self.udp_subs]:
            if m_type in subs:
                for client in subs[m_type]:
                    client.write(msg, m_type)

    def remove_client(self, protocol):
        self.clients.remove(protocol)
        for subs in [self.tcp_subs, self.udp_subs]:
            for msg_type in subs:
                if protocol in subs[msg_type]:
                    subs[msg_type].remove(protocol)

    def msg_received(self, protocol, msg, msg_type):
        if msg_type == _SUBSCRIBE:
            data = Subscribe()
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
