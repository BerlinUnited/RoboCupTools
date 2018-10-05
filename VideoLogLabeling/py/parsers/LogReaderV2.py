import os
import struct
import mmap

import google.protobuf.reflection
import CommonTypes_pb2, Framework_Representations_pb2, Messages_pb2, Representations_pb2

'''
# Log file structure:
|----|--------|------|------|----|-----
| FN | String | Size | Data | FN | ...
|----|--------|------|------|----|-----
'''

class Parser:
    def __init__(self):
        self.messages = {}
        self.messages.update(CommonTypes_pb2.DESCRIPTOR.message_types_by_name)
        self.messages.update(Framework_Representations_pb2.DESCRIPTOR.message_types_by_name)
        self.messages.update(Messages_pb2.DESCRIPTOR.message_types_by_name)
        self.messages.update(Representations_pb2.DESCRIPTOR.message_types_by_name)

    def parse(self, name, data):
        if name in self.messages:
            return google.protobuf.reflection.ParseMessage(self.messages[name], data)
        return None

class LogReader:
    def __init__(self, path, parser=Parser(), filter=lambda x: x):

        self.file = open(path, 'r+b')
        self.mm = mmap.mmap(self.file.fileno(), 0)
        self.size = os.stat(path).st_size

        self.parser = parser
        self.filter = filter

        self.frames = []
        while self.mm.tell() < self.mm.size():
            # search for string end and start after the frameNumber
            end_pos = self.mm.find(b'\0', self.mm.tell()+4)
            # calculate the string size
            str_size = end_pos - self.mm.tell()
            # extract frameNumber, name and data size; ignore NULL-byte (\0)
            fn, name, size = struct.unpack('=l'+str(str_size-4)+'sxl', self.mm.read(str_size+5))
            # create new frame, if the frameNumber doesn't exists
            if not self.frames or self.frames[-1].number != fn: self.frames.append(Frame(self, fn))
            # add representation to frame
            self.frames[-1].messages[name.decode('utf8')] = (self.mm.tell(), size, None)
            # advance file pointer
            self.mm.seek(size, os.SEEK_CUR)

    def __iter__(self):
        return iter(self.frames)

    def __getitem__(self, item):
        return self.frames[item]

    def close(self):
        self.mm.close()
        self.file.close()

class Frame:
    def __init__(self, reader, number):
        self.reader = reader
        self.number = number
        self.messages = {}

    def __getitem__(self, name):
        return self.getMessage(name)

    def getMessage(self, name):
        if name in self.messages:
            position, size, message = self.messages[name]

            if message is not None:
                return message

            self.reader.mm.seek(position)
            data = self.reader.mm.read(size)

            message = self.reader.parser.parse(name, data)
            self.messages[name] = (position, size, message)
            return message
        return None
