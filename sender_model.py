# -*- coding: utf-8 -*-
from socket import *
from errors import Error
from Crypto.Cipher import AES
from IoT_manager import Manager
import json
import time


class Sender:
    def __init__(self, delay, legal_count, illegal_count, udp_endpoint=('localhost', 63000),
                 tcp_endpoint=('localhost', 8010)):
        self.delay = delay
        self.legal_count = legal_count
        self.illegal_count = illegal_count
        self.udp_endpoint = udp_endpoint
        self.tcp_endpoint = tcp_endpoint
        s_key = 'Very S3cr3t Key!11!11111'
        BS = 16
        self.padding = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        self.reduce_padding = lambda s: s[0:-ord(s[-1])]
        self.aes = AES.new(s_key, AES.MODE_CBC, '0123456789987654')

    def __send_udp(self, data):
        if not data:
            raise Error('no payload to send via UDP')
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_socket.settimeout(0.1)
        data = self.aes.encrypt(self.padding(data))
        udp_socket.sendto(data, self.udp_endpoint)
        try:
            data = udp_socket.recvfrom(1024)
        except Exception:
            data = ''
        udp_socket.close()
        return data

    def __send_tcp(self, data):
        if not data:
            raise Error('no data to send via TCP')
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        tcp_socket.settimeout(0.1)
        tcp_socket.connect(self.tcp_endpoint)
        data = self.aes.encrypt(self.padding(data))
        tcp_socket.send(data)
        try:
            resp = tcp_socket.recv(1024)
        except timeout:
            resp = [False]
        tcp_socket.close()
        return resp

    def run_device(self, legal):
        ack = self.__send_tcp(u'connect')
        if u'ack' in ack:
            print(u'connection established')
            if legal:
                resp = self.__send_tcp('run')
            else:
                resp = self.__send_tcp('run_illegal')
        else:
            resp = ack
        if resp == u'ready':
            manager = Manager()
            documents = manager.get_document_list()
            send_data = json.dumps({
                u'get_document_list': documents
            })
            resp = self.__send_udp(send_data)[0]
            resp = json.loads(resp)
            id = resp[u'get_document']
            file = manager.get_document(id)['file']
            for chunk in manager.fread_chunked(open(file, 'rb'), 900):
                send_data = json.dumps({
                    u'chunk': chunk
                })
                resp = self.__send_udp(send_data)
                if resp != u'ok' and len(resp) > 0:
                    print(resp)
            time.sleep(2)
            return resp

    def send_legal(self, legal=True):
        return self.run_device(legal)

    def send_disconnect(self):
        self.__send_tcp(u'disconnect')
