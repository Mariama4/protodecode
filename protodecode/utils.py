import base64

def is_hex(s: str) -> bool:
    for ch in s:
        if ch not in "abcdef0123456789":
            return False
    return True

def parse_input_data(input_data: str) -> bytes:
    normalized_input = "".join(input_data.split())
    normalized_hex_input = normalized_input.replace("0x", "").lower()
    if is_hex(normalized_hex_input):
        return bytes.fromhex(normalized_hex_input)
    else:
        return base64.b64decode(normalized_input)

def buffer_to_pretty_hex(b: bytes) -> str:
    return " ".join(f"{c:02x}" for c in b)
