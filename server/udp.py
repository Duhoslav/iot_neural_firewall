# -*- coding: utf-8 -*-
from socket import *
from threading import Thread


class UDPServer:
    def __init__(self, addr=('localhost', 63000)):
        self.addr = addr
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(self.addr)
        self.socket.settimeout(2)
        self.started = False
        self.queue = []

    def start_server(self, started=True):
        self.started = started
        t = Thread(target=self.check_data_task)
        t.start()

    def check_data_task(self):
        while self.started:
            # recvfrom - получает UDP сообщения
            try:
                payload, addr = self.socket.recvfrom(1024)
                self.queue.append((addr, payload))
            except timeout:
                continue

    def send_data(self, addr, data):
        self.socket.sendto(data, addr)

    def stop_server(self):
        self.started = False
        self.socket.close()
