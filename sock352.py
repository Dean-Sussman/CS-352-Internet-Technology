import binascii
import socket as syssock
import struct
import sys


receiving_port = 4125
transmitting_port = 4125
# flags
SOCK352_SYN = 0x01
SOCK352_FIN = 0x02
SOCK352_ACK = 0x04
SOCK352_RESET = 0x08
SOCK_352_HAS_OPT = 0xA0

PACKET_SIZE = 64000
head = "!BBBBHHLLQQLL"
header_len = struct.calcsize(head)

# these functions are global to the class and
# define the UDP ports all messages are sent
# and received from


def init(udp_port_tx, udp_port_rx):  # initialize your UDP socket here
    global receiving_port
    global transmitting_port

    if int(udp_port_tx) != 0:
        transmitting_port = int(udp_port_tx)

    if int(udp_port_rx) != 0:
        receiving_port = int(udp_port_rx)


class socket:

    def __init__(self):  # fill in your code here
        self.syssock = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)

        return

    def bind(self, address):
        return

    def connect(self, address):  # fill in your code here
        # listens at the receiving port
        self.syssock.bind(('', receiving_port))
        # transmits from the transmission port
        self.syssock.connect((address[0], transmitting_port))
        self.syssock.send(RDPPacket(0x1, SOCK352_SYN, 0, 0, header_len, 0, 0, 0, 0, 0, 0, 0, b'').pack())
        packet = self.receive_packets(1)
        self.syssock.send(RDPPacket(0x1, SOCK352_ACK, 0, 0, header_len, 0, 0, 0, 0, 0, 0, 0, b'').pack())
        print("Client side of connection startup completed")
        return

    def listen(self, backlog):
        return

    def accept(self):
        packet, address = self.receive_packets(1)
        self.syssock.connect((address[0], transmitting_port))
        self.syssock.send(RDPPacket(0x1, SOCK352_SYN | SOCK352_ACK, 0, 0, header_len, 0, 0, 0, 0, 0, 0, 0, b'').pack())
        packet = self.receive_packets(1)
        print("server side of connection startup completed")
        return self, address

    def close(self):  # fill in your code here
        return

    def send(self, buffer):
        bytes_sent = 0  # fill in your code here
        return bytes_sent

    def recv(self, nbytes):
        bytes_received = 0  # fill in your code here
        return bytes_received

    def receive_packets(self, number_of_packets):
        (packed_packet, address) = self.syssock.recvfrom(PACKET_SIZE + header_len)
        header = struct.unpack(head, packed_packet[:header_len])
        data = packed_packet[header_len:]
        return_packet = RDPPacket(header[0], header[1], header[2], header[3], header[4], header[5],
        									 header[6], header[7], header[8], header[9], header[10], data)
        return return_packet, address

    def send_packets(self):
        return


class RDPPacket:

    def __init__(self, version, flags, opt_ptr, protocol, header_len, checksum, source_port, dest_port, sequence_no, ack_no,
                 window, payload_len, data):
        self.version = version          # should be 0x1
        self.flags = flags
        self.opt_ptr = opt_ptr          # should be 0
        self.protocol = protocol        # should be 0
        self.header_len = header_len    # size of the header, in bytes
        self.checksum = checksum        # should be 0
        self.source_port = source_port  # should be 0
        self.dest_port = dest_port      # should be 0
        self.sequence_no = sequence_no
        self.ack_no = ack_no
        self.window = window            # should be 0
        self.payload_len = payload_len
        self.data = data

    def pack(self):
        return struct.pack("BBBBHHLLQQLL", self.version, self.flags, self.opt_ptr, self.protocol, self.header_len, self.checksum,
                           self.source_port, self.dest_port, self.sequence_no, self.ack_no, self.window,
                           self.payload_len) + self.data


