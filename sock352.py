import binascii
import socket as syssock
import struct
import sys
import time


receiving_port = 4125
transmitting_port = 4125

# flags
SOCK352_SYN = 0x01
SOCK352_FIN = 0x02
SOCK352_ACK = 0x04
SOCK352_RESET = 0x08
SOCK352_HAS_OPT = 0xA0

PACKET_SIZE = 32000
#given in pdf
head = "!BBBBHHLLQQLL"
header_len = struct.calcsize(head)

time_out = 0.2

# these functions are global to the class and
# define the UDP ports all messages are sent
# and received from
def init(udp_port_tx, udp_port_rx):  # initialize your UDP socket here
    global receiving_port
    global transmitting_port

    #if transmitting port is given in terminal argument
    if int(udp_port_tx) != 0:
        transmitting_port = int(udp_port_tx)

    #if receiving port is given in terminal argument
    if int(udp_port_rx) != 0:
        receiving_port = int(udp_port_rx)
    #else use globally instantiated ports

class socket:

    def __init__(self):  # fill in your code here
        self.syssock = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)

    def bind(self, address):
        #binds Server to receiving_port
        self.syssock.bind((address[0], receiving_port))
        return

    #Where Client does 3-way handshake to connect to the transmitting_port and receive from receiving_port
    def connect(self, address):  # fill in your code here
        # listens at the receiving port
        self.syssock.bind(('', receiving_port))
        # transmits from the transmission port
        self.syssock.connect((address[0], transmitting_port))
        #Part 1 - send SYN to server
        self.syssock.send(RDPPacket(0x1, SOCK352_SYN, 0, 0, header_len, 0, 0, 0, 0, 0, 0, 0, b'').pack())
        #Part 2 - receive SYN and ACK
        packet, temp = self.receive_packets(1)
        #Part 3 - send ACK to connect to server
        self.syssock.send(RDPPacket(0x1, SOCK352_ACK, 0, 0, header_len, 0, 0, 0, 0, 0, 0, 0, b'').pack())
        return

    def listen(self, backlog):
        return

    #Server accepts the connection from Client using a 3-way Handshake
    def accept(self):
        #Part 1 - receive packet and address
        packet, address = self.receive_packets(1)
        #Connect to the other port
        self.syssock.connect((address[0], transmitting_port))
        #Part 2 - send SYN and ACK signals
        self.syssock.send(RDPPacket(0x1, SOCK352_SYN | SOCK352_ACK, 0, 0, header_len, 0, 0, 0, 0, 0, 0, 0, b'').pack())
        #Part 3 - receive ACK
        packet = self.receive_packets(1)
        return self, address

    #Closes the connection between Client and Server using double 2-way handshake
    def close(self):  # fill in your code here
        #First Handshake Part 1 - Send closing FIN
        self.syssock.send(RDPPacket(0x1, SOCK352_FIN, 0, 0, header_len, 0, 0, 0, 0, 0, 0, 0, b'').pack())
        #First Handshake Part 2 - Receive closing FIN
        packet = self.receive_packets(1)
        #Second Handshake Part 1 - Send ACK
        self.syssock.send(RDPPacket(0x1, SOCK352_ACK, 0, 0, header_len, 0, 0, 0, 0, 0, 0, 0, b'').pack())
        #Second Handshake Part 2 - Receive ACK
        packet = self.receive_packets(1)
        #final close on socket
        self.syssock.close()
        return

    # send buffer of data that is broken into smaller RDP packets and sent through the socket
    def send(self, buffer):
        packets = []
        bytes_sent = header_len
        for i in range(0, len(buffer), PACKET_SIZE):
            #where buffer is broken up
            buffer_chunk = buffer[i:i + PACKET_SIZE]
            packet = RDPPacket(1, 0, 0, 0, header_len, 0, 0, 0, i / PACKET_SIZE, i / PACKET_SIZE, 0, len(buffer_chunk), buffer_chunk)
            packets.append(packet)
            self.send_packets(packets)
            bytes_sent += header_len
        return bytes_sent

    def recv(self, nbytes):
        #want to receive bytes given
        bytes_received = self.syssock.recv(nbytes)
        return bytes_received

    def receive_packets(self, number_of_packets):
        #for Go-Back-N looking at one unit
        (packed_packet, address) = self.syssock.recvfrom(PACKET_SIZE + header_len)
        header = struct.unpack(head, packed_packet[:header_len])
        #data is in the index of header_len
        data = packed_packet[header_len:]
        return_packet = RDPPacket(header[0], header[1], header[2], header[3], header[4], header[5],
        									 header[6], header[7], header[8], header[9], header[10], header[11], data)
        return return_packet, address

    def send_packets(self, packets):
            self.syssock.sendto(packets[-1].data, ('', transmitting_port))
            # while(time.time() != time_out):
                # while(lastAck < len(packets)):
                    #More packets to send
                    #last_packet++
                    #timer did not start
                    #if time.time()==0:
                        #start timer
                    #self.send_packets(packets[last_packet])
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
