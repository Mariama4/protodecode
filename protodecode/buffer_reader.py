from .varint import decode_varint
from .utils import buffer_to_pretty_hex

class BufferReader:
    def __init__(self, buffer: bytes):
        self.buffer = buffer
        self.offset = 0
        self.saved_offset = None

    def read_varint(self):
        value, length = decode_varint(self.buffer, self.offset)
        self.offset += length
        return value

    def read_buffer(self, length: int) -> bytes:
        self.check_byte(length)
        result = self.buffer[self.offset:self.offset + length]
        self.offset += length
        return result

    def try_skip_grpc_header(self):
        backup_offset = self.offset
        if self.left_bytes() >= 5 and self.buffer[self.offset] == 0:
            self.offset += 1
            if self.offset + 4 > len(self.buffer):
                self.offset = backup_offset
                return
            length = int.from_bytes(self.buffer[self.offset:self.offset + 4], byteorder='big', signed=True)
            self.offset += 4
            if length > self.left_bytes():
                self.offset = backup_offset

    def left_bytes(self) -> int:
        return len(self.buffer) - self.offset

    def check_byte(self, length: int):
        bytes_available = self.left_bytes()
        if length > bytes_available:
            raise Exception(f"Not enough bytes left. Requested: {length} left: {bytes_available}")

    def checkpoint(self):
        self.saved_offset = self.offset

    def reset_to_checkpoint(self):
        if self.saved_offset is not None:
            self.offset = self.saved_offset
