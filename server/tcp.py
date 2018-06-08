# -*- coding: utf-8 -*-
from socket import *
from threading import Thread


class TCPServer:
    def __init__(self, addr=('localhost', 8010)):
        self.addr = addr
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind(self.addr)
        self.socket.settimeout(2)
        self.socket.listen(1)
        self.connection = None
        self.client_addr = None
        self.started = False
        self.queue = []

    def start_server(self, started=True):
        self.started = started
        t = Thread(target=self.check_data_task)
        t.start()

    def check_data_task(self):
        while self.started:
            # получаем TCP сообщения по таймауту
            try:
                self.connection, self.client_addr = self.socket.accept()
                payload = self.connection.recv(1024)
                self.queue.append((self.client_addr, payload))
            except timeout:
                continue

    def send_data(self, addr, data):
        self.connection.send(data.encode())

    def stop_server(self):
        self.started = False
        self.socket.close()
