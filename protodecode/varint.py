def decode_varint(buffer: bytes, offset: int):
    res = 0
    shift = 0
    start_offset = offset
    while True:
        if offset >= len(buffer):
            raise IndexError("Index out of bound decoding varint")
        byte = buffer[offset]
        offset += 1
        res |= (byte & 0x7F) << shift
        shift += 7
        if byte < 0x80:
            break
    return res, (offset - start_offset)

def decode_varint_parts(value):
    return str(value)
