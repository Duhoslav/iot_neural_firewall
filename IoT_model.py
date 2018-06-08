# -*- coding: utf-8 -*-
# Сторонние библиотеки
from threading import Thread
import types
import IoT_tasks
from IoT_tasks import get_random_document, display_book, update_connection, run_illegal
import json
# Вспомогательные модули
from server.udp import UDPServer
from server.tcp import TCPServer

s_key = 'Very S3cr3t Key!11!11111'


BS = 16
padding = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
reduce_padding = lambda s: s[0:-ord(s[-1])]
map = {
    u'connect': u'ack',
    u'run': u'ready',
    u'run_illegal': run_illegal,
    u'disconnect': update_connection,
    u'get_document_list': get_random_document,
    u'chunk': display_book
}


def udp_data_handler(data):
    aes = IoT_tasks.aes
    payload = reduce_padding(aes.decrypt(data))
    try:
        payload = json.loads(payload)
        response = ''
    except Exception:
        return 'recieved invalid JSON via UPD'
    key = payload.keys()[0]
    if key in map:
        if type(map[key]) is types.FunctionType:
            response = map[key](payload[key])
        else:
            response = map[key]
    else:
        print 'unknown command ' + payload
    return response


def tcp_data_handler(data):
    aes = IoT_tasks.aes
    response = ''
    payload = reduce_padding(aes.decrypt(data))
    if payload in map:
        if type(map[payload]) is types.FunctionType:
            response = map[payload](payload)
        else:
            response = map[payload]
    else:
        print 'unknown command ' + payload
    print 'recieved: ' + payload + '\n'
    return response


def udp_server(flag):
    # данные сервера
    host = 'localhost'
    port = 63000
    addr = (host, port)

    server = UDPServer(addr)
    server.start_server(started=True)
    while flag[0]:
        if len(server.queue):
            s_addr, payload = server.queue.pop()
            response = udp_data_handler(payload)
            if response:
                server.send_data(s_addr, response)
    server.stop_server()
    print 'UDP server stopped!'


def tcp_server(flag):
    host = 'localhost'
    port = 8010
    addr = (host, port)

    server = TCPServer(addr)
    server.start_server(started=True)
    while flag[0]:
        if len(server.queue):
            s_addr, payload = server.queue.pop()
            response = tcp_data_handler(payload)
            if response:
                server.send_data(s_addr, response)
    server.stop_server()
    print 'TCP server stopped!'


if __name__ == '__main__':
    flag = [1]
    ThreadUDP = Thread(target=udp_server, args=[flag])
    ThreadTCP = Thread(target=tcp_server, args=[flag])

    print "Starting Server..."
    ThreadUDP.start()
    print "UDP Server Started!"
    ThreadTCP.start()
    print "TCP Server Started!"
    while True:
        key = raw_input('press "q" to quit')
        if key == 'q':
            print 'exiting...'
            flag[0] = 0
            exit(2)
