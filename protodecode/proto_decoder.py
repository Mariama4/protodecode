import struct
from .types import TYPES
from .utils import parse_input_data, buffer_to_pretty_hex
from .varint import decode_varint, decode_varint_parts
from .fixed import decode_fixed32, decode_fixed64
from .buffer_reader import BufferReader

def decode_proto(buffer: bytes):
    reader = BufferReader(buffer)
    parts = []
    reader.try_skip_grpc_header()

    try:
        while reader.left_bytes() > 0:
            reader.checkpoint()
            byte_range = [reader.offset]
            index_type = int(reader.read_varint())
            type_field = index_type & 0b111
            index = index_type >> 3

            if type_field == TYPES['VARINT']:
                value = str(reader.read_varint())
            elif type_field == TYPES['LENDELIM']:
                length = int(reader.read_varint())
                value = reader.read_buffer(length)
            elif type_field == TYPES['FIXED32']:
                value = reader.read_buffer(4)
            elif type_field == TYPES['FIXED64']:
                value = reader.read_buffer(8)
            else:
                raise Exception("Unknown type: " + str(type_field))
            byte_range.append(reader.offset)

            parts.append({
                "byteRange": byte_range,
                "index": index,
                "type": type_field,
                "value": value
            })
    except Exception:
        reader.reset_to_checkpoint()

    return {
        "parts": parts,
        "leftOver": reader.read_buffer(reader.left_bytes())
    }

def ProtobufVarintPart(value):
    return decode_varint_parts(value)

def ProtobufFixed32Part(value: bytes):
    decoded = decode_fixed32(value)
    for d in decoded:
        if d["type"] == "float":
            float_val = d["value"]
            if float_val.is_integer():
                return int(float_val)
            return float_val
    return decoded

def ProtobufFixed64Part(value: bytes):
    return decode_fixed64(value)

def ProtobufStringOrBytesPart(value):
    return value["value"]

def get_protobuf_part(part):
    if part["type"] == TYPES['VARINT']:
        return (ProtobufVarintPart(part["value"]), None)
    elif part["type"] == TYPES['LENDELIM']:
        decoded = decode_proto(part["value"])
        if len(part["value"]) > 0 and len(decoded["leftOver"]) == 0 and decoded["parts"]:
            return (ProtobufDisplay(decoded), "protobuf")
        else:
            decoded2 = decode_string_or_bytes(part["value"])
            return (ProtobufStringOrBytesPart(decoded2), decoded2["type"])
    elif part["type"] == TYPES['FIXED64']:
        return (ProtobufFixed64Part(part["value"]), None)
    elif part["type"] == TYPES['FIXED32']:
        return (ProtobufFixed32Part(part["value"]), None)
    else:
        return ("Unknown type", None)

def ProtobufPart(part):
    contents, _ = get_protobuf_part(part)
    return contents

def ProtobufDisplay(decoded):
    return [ProtobufPart(part) for part in decoded["parts"]]

def decode_grpc(data: str):
    return ProtobufDisplay(decode_proto(parse_input_data(data)))

def decode_string_or_bytes(value: bytes):
    if len(value) == 0:
        return {"type": "string|bytes", "value": ""}
    try:
        decoded = value.decode("utf-8")
        return {"type": "string", "value": decoded}
    except UnicodeDecodeError:
        return {"type": "bytes", "value": buffer_to_pretty_hex(value)}
