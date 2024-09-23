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
cmd_channel = 1
data_channel = 3

cmd_sock = socket.socket(
    socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
cmd_sock.connect((target_device_mac, cmd_channel))
print('Connected to command channel')

data_sock = socket.socket(
    socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
data_sock.connect((target_device_mac, data_channel))
print('Connected to data channel')

# Enable APRS reports on data channel
data_sock.send(b'\xff\x01\x00\x01\x00\x02\x00\x06\x01')

while True:
    r, w, e = select.select([cmd_sock, data_sock], [], [])
    for s in r:
        if s is cmd_sock:
            print('Received command:')
        elif s is data_sock:
            print('Received data:')
        else:
            print('Unknown socket:', s)

        cmd = s.recv(1024)
        hexdump(cmd)
