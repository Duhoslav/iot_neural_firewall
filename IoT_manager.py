# -*- coding: utf-8 -*-


class Manager:
    def __init__(self):
        print "Device is ready to start!"
        self.working = True
        self.documents = [
            {
                'id': 0,
                'name': 'Python book',
                'file': 'test.txt'
            },
            {
                'id': 1,
                'name': 'Python book - copy',
                'file': 'test2.txt'
            }
        ]

    def pause(self, flag):
        self.working = flag

    def get_document_list(self):
        return self.documents

    def get_document(self, id):
        for b in self.documents:
            if b['id'] == id:
                return b
        return 'No document with id: ' + id

    @staticmethod
    def fread_chunked(file, sz):
        while True:
            chunk = file.read(sz)
            if not chunk:
                break
            yield chunk
