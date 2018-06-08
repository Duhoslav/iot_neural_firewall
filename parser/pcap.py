# -*- coding: utf-8 -*-
import dpkt
import re

"""
digitized_packet
[
    type: upd 0, tcp 1
    len: size in bytes
    direction: to dev 0, from dev 1
    is_word: 0, 1
    seq_num: int
]
"""


class PcapParser:
    def __init__(self, filename):
        f = open(filename)
        self.pcap = dpkt.pcap.Reader(f)
        self.digitized_packets = []
        self.illegal_packets = []

    @staticmethod
    def __is_word(str):
        is_word = 0
        if len(str) > 0 and re.match(r'\w+$', str):
            is_word = 1
        return is_word

    def parse(self):
        u_first = True
        t_first = True
        t_dport = None
        u_dport = None
        direction = 0
        seq_num = 0
        MAX_PACKET_SIZE = 10
        MAX_SEQ_SIZE = 6
        for ts, buf in self.pcap:
            digitized_packet = []
            if len(buf) < 3:
                continue
            eth = dpkt.ethernet.Ethernet(buf)
            if eth.type == dpkt.ethernet.ETH_TYPE_IP:
                ip = eth.data
                if ip.p == dpkt.ip.IP_PROTO_TCP:
                    tcp = ip.data
                    if not hasattr(tcp, u'data'):
                        continue
                    if t_first:
                        t_dport = tcp.dport
                        t_first = False
                    digitized_packet.append(0)
                    # Для корректной работы нужно представить длину данных в двоичном виде. Максимально 16 байт (т.к. макс. длина пакета 65 535)
                    binary_data_len = "{0:b}".format(len(tcp.data))
                    if len(binary_data_len) < MAX_PACKET_SIZE:
                        binary_data_len = (MAX_PACKET_SIZE - len(binary_data_len)) * '0' + binary_data_len
                    digitized_packet += [int(l) for l in binary_data_len]
                    # Если пакет отправлен на устройство, то 0, иначе 1
                    if tcp.dport == t_dport:
                        if direction == 1:
                            direction = 0
                            seq_num = 0
                        else:
                            seq_num += 1
                            # digitized_packet.append(direction)
                    else:
                        if direction == 0:
                            direction = 1
                            seq_num = 0
                        else:
                            seq_num += 1
                    digitized_packet.append(direction)
                    digitized_packet.append(self.__is_word(tcp.data))
                elif ip.p == dpkt.ip.IP_PROTO_UDP:
                    udp = ip.data
                    if u_first:
                        u_dport = udp.dport
                        u_first = False
                    digitized_packet.append(1)
                    # Для корректной работы нужно представить длину данных в двоичном виде. Максимально 16 байт (т.к. макс. длина пакета 65 535)
                    binary_data_len = "{0:b}".format(len(udp.data))
                    if len(udp.data)==32 and udp.dport != u_dport:
                        self.illegal_packets.append(len(self.digitized_packets))
                    if len(binary_data_len) < MAX_PACKET_SIZE:
                        binary_data_len = (MAX_PACKET_SIZE - len(binary_data_len)) * '0' + binary_data_len
                    digitized_packet += [int(l) for l in binary_data_len]
                    if udp.dport == u_dport:
                        if direction == 1:
                            direction = 0
                            seq_num = 0
                        else:
                            seq_num += 1
                    else:
                        if direction == 0:
                            direction = 1
                            seq_num = 0
                        else:
                            seq_num += 1
                    digitized_packet.append(direction)
                    digitized_packet.append(self.__is_word(udp.data))
                # Для корректной работы нужно представить seq_num в двоичном виде. Будем считать, что это число от 0 до 126, т.е. 7 байт.
                binary_seq_num = "{0:b}".format(seq_num)
                if len(binary_seq_num) < MAX_SEQ_SIZE:
                    binary_seq_num = (MAX_SEQ_SIZE - len(binary_seq_num)) * '0' + binary_seq_num
                digitized_packet += [int(l) for l in binary_seq_num]
                # print digitized_packet
                self.digitized_packets.append(digitized_packet)
        return self.digitized_packets
