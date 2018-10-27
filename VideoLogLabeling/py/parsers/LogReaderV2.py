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
    """Parses raw protobuf messages based on their name and returns the parsed data."""

    def __init__(self):
        """Constructor. Initializes all known protobuf messages."""
        self.messages = {}
        self.messages.update(CommonTypes_pb2.DESCRIPTOR.message_types_by_name)
        self.messages.update(Framework_Representations_pb2.DESCRIPTOR.message_types_by_name)
        self.messages.update(Messages_pb2.DESCRIPTOR.message_types_by_name)
        self.messages.update(Representations_pb2.DESCRIPTOR.message_types_by_name)

    def parse(self, name, data):
        """
        Parses the given :data: and uses the :name: for identifying the appropriate protobuf object. Returns None if no
        protobuf object could be found.

        :param name:    the (protobuf) name of the given :data:
        :param data:    the raw (bytes) data which should be parsed
        :return:        the parsed protobuf message
        """
        if name in self.messages:
            return google.protobuf.reflection.ParseMessage(self.messages[name], data)
        return None

class LogReader:
    """A log reader for parsing a log file. A log file consist of frames and each frame has multiple (protobuf) messages,
    which contains the data. A filter can be used to modify the returned data of each frame. For example, the filter can
    be used to return the frames data in a specific format or just return a specific portion of the frame."""

    def __init__(self, path, parser=Parser(), filter=lambda x: x):
        """Constructor. Reads the log file from the :path: and creates an index of the contained frames."""
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
        """Returns an iterator object for iterating over the log frames."""
        return iter(self.frames)

    def __getitem__(self, item):
        """Applies the filter to the data returned by the frame at :item: position of this log and returns its result."""
        return self.filter(self.frames[item])

    def close(self):
        """Closes the log file and releases all file descriptors."""
        self.mm.close()
        self.file.close()

class Frame:
    """A Frame represents a container of data (messages) at a certain time frame in a log file."""

    def __init__(self, reader, number):
        """Constructor. Initializes the frame variables."""
        self.reader = reader
        self.number = number
        self.messages = {}

    def __getitem__(self, name):
        """
        Returns the parsed data of this frame identified by :name:.
        See :func:`~Frame.getMessage`

        :param name:    the name of the frames message
        :return:        the data of the frames message
        """
        return self.getMessage(name)

    def getMessage(self, name):
        """
        Returns the parsed data of this frame identified by :name:. The data is only parsed once and cached for subsequent
        requests. If there is no data with :name: in this frame, None is returned

        :param name:    the name of the frames message
        :return:        the parsed data of the frame message or None
        """
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
