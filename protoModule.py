import asyncio
from robomodules.comm.asyncClient import AsyncClient
from robomodules.comm.udpClient import UdpClient
from robomodules.comm.subscribe_pb2 import Subscribe

class ProtoModule:
    def __init__(self, addr, port, message_buffers, MsgType, frequency=0, tcp_subscriptions=[], udp_subscriptions=[], loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.tcp_client = AsyncClient(addr, port, self.msg_received, message_buffers, MsgType, tcp_subscriptions, self.loop)
        self.udp_client = UdpClient(addr, port, self.msg_received, message_buffers, MsgType, udp_subscriptions, self.loop)
        self.frequency = frequency
        self.loop.call_soon(self._internal_tick)

    def _internal_tick(self):
        if self.frequency > 0:
            self.loop.call_later(1.0/self.frequency, self._internal_tick)
            self.tick()

    def set_frequency(self, frequency):
        self.frequency = frequency
        self.loop.call_soon(self._internal_tick)

    def tick(self):
        raise NotImplementedError()

    def msg_received(self, msg, msg_type):
        raise NotImplementedError()

    def subscribe(self, msg_types, protocol='tcp'):
        if protocol == 'tcp':
            self.tcp_client.subscribe(msg_types, Subscribe.SUBSCRIBE)
        elif protocol == 'udp':
            self.udp_client.subscribe(msg_types, Subscribe.SUBSCRIBE)

    def unsubscribe(self, msg_types, protocol='tcp'):
        if protocol == 'tcp':
            self.tcp_client.subscribe(msg_types, Subscribe.UNSUBSCRIBE)
        elif protocol == 'udp':
            self.udp_client.subscribe(msg_types, Subscribe.UNSUBSCRIBE)

    def write(self, msg, msg_type, protocol='tcp'):
        if protocol == 'tcp':
            self.tcp_client.write(msg, msg_type)
        elif protocol == 'udp':
            self.udp_client.write(msg, msg_type)

    def connect(self):
        self.tcp_client.connect()
        self.udp_client.connect()
    
    def run(self):
        try:
            self.connect()
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.quit()

    def quit(self):
        self.loop.stop()
