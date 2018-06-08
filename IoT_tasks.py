# -*- coding: utf-8 -*-
import json
from random import randint
from Crypto.Cipher import AES
import hashlib

s_key = 'Very S3cr3t Key!11!11111'
aes = AES.new(s_key, AES.MODE_CBC, '0123456789987654')
illegal = False
illegal_count = 0

def update_connection(data):
    global aes
    global illegal
    global illegal_count
    print illegal_count
    illegal_count = 0
    illegal = False
    aes = AES.new(s_key, AES.MODE_CBC, '0123456789987654')
    print u'Updating session...wait'
    return u'disconnected'


def get_random_document(list):
    id = randint(0, len(list) - 1)
    send_data = json.dumps({
        'get_document': id
    })
    return send_data


def display_book(chunk):
    global illegal
    global illegal_count
    print chunk
    hash = ''
    illegal_count+=1
    if illegal and len(chunk):
        hash = hashlib.md5(chunk)
        hash = hash.hexdigest()
    return hash


def run_illegal(data):
    global illegal
    illegal = True
    return u'ready'
