import struct
import numpy as np

class Stl:
    dtype = np.dtype([
        ('normals',np.float32, (3,)),
        ('v0',np.float32,(3,)),
        ('v1',np.float32,(3,)),
        ('attr','u2',(1,)),
        ])

    def __init__(self,header,data):
        self.header = header
        self.data = data

    @classmethod
    def from_file(cls, filename, mode='rb'):
        with open(filename,mode) as fh:
            header = fh.read(80)
            size, = struct.unpack("@i", fh.read(4))
            data = np.fromfile(fh, dtype=cls.dtype, count=size)
            return Stl(header,data)

    def to_file(self, filename,mode='wb'):
        with open(filename, mode) as fh:
            fh.write(self.header)
            fh.write(struct.pack("@i",self.data.size))
            self.data.tofile(fh)


if __name__ == '__main__':
    stl = Stl.from_file('test.stl')

    stl.data['v0'][:, 0] += 1
    stl.data['v1'][:, 0] += 1
    stl.data['v2'][:, 0] += 1

    stl.to_file('test2.stl')
