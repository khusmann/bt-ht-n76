import socket
import select
import sys


def hexdump(data: bytes, length: int = 16):
    for i in range(0, len(data), length):
        chunk = data[i:i+length]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f'{i:08x}  {hex_part:<{length*3}}  |{ascii_part}|')


target_device_mac = sys.argv[1]
audio_channel_id = 1
data_channel_id = 3

audio_sock = socket.socket(
    socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
)
audio_sock.connect((target_device_mac, audio_channel_id))
print('Connected to rx/tx audio channel')

data_sock = socket.socket(
    socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
)
data_sock.connect((target_device_mac, data_channel_id))
print('Connected to data channel')

# Enable APRS reports on data channel
data_sock.send(b'\xff\x01\x00\x01\x00\x02\x00\x06\x01')

while True:
    r, w, e = select.select([audio_sock, data_sock], [], [])
    for s in r:
        if s is audio_sock:
            print('Received rx/tx audio clip:')
        elif s is data_sock:
            print('Received data:')
        else:
            print('Unknown socket:', s)

        cmd = s.recv(1024)
        hexdump(cmd)
