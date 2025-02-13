import struct

def decode_fixed32(value: bytes):
    # Читаем 4 байта как little-endian float и целые
    float_value = struct.unpack('<f', value)[0]
    int_value = struct.unpack('<i', value)[0]
    uint_value = struct.unpack('<I', value)[0]
    result = []
    result.append({"type": "int", "value": int_value})
    if int_value != uint_value:
        result.append({"type": "uint", "value": uint_value})
    result.append({"type": "float", "value": float_value})
    return result

def decode_fixed64(value: bytes):
    return struct.unpack('<d', value)[0]
