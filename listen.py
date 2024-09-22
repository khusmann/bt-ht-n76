import socket
import typing as t
import argparse


def hexdump(data: bytes):
    # Print the hex dump of the data, 16 bytes per line
    for i in range(0, len(data), 16):
        # Slice 16 bytes from the data
        chunk = data[i:i+16]

        # Convert to hex values
        hex_values = ' '.join(f'{byte:02x}' for byte in chunk)

        # Convert to ASCII, replace non-printable characters with a dot
        ascii_values = ''.join(chr(byte) if 32 <= byte <=
                               126 else '.' for byte in chunk)

        # Print the offset, hex values, and ASCII values
        print(f'{i:08x}  {hex_values:<48}  {ascii_values}')


def is_valid_packet(data: bytes) -> bool:
    return data.startswith(b'\x7e') and data.endswith(b'\x7e')


def decode_packet(data: bytes):
    if data.startswith(b'\x00\x9c\x71\x12'):
        print("Received Audio")
    elif data.startswith(b'\x01\x00\x01\x00'):
        print("Received APRS message")
    elif data.startswith(b'\x09\x9c\x71\x12'):
        print("Transmitting audio")
    elif data.startswith(b'\x01\x00\x04\x00'):
        print("Got this after transmitting audio one time?")
    else:
        print("Unknown packet:")
        hexdump(data)


def bind_rfcomm(target_device_mac: str):
    # Define the RFCOMM channel
    channel = 1  # RFCOMM channel number, adjust based on your needs

    sock: t.Optional[socket.socket] = None

    try:
        # Create an RFCOMM socket
        sock = socket.socket(socket.AF_BLUETOOTH,
                             socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

        # Connect to the target device
        sock.connect((target_device_mac, channel))
        print(f"Connected to {target_device_mac} on RFCOMM channel {channel}.")

        # Listening for incoming data
        while True:
            data = sock.recv(1024)
            if not data:
                break

            if is_valid_packet(data):
                decode_packet(data[1:-1])
            else:
                print("Invalid packet:")
                hexdump(data)

    except socket.error as e:
        print(f"Error: {e}")
    finally:
        if sock:
            sock.close()
        print()
        print("Disconnected.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Connect to a Bluetooth device via RFCOMM.")
    parser.add_argument("mac_address", type=str,
                        help="Bluetooth MAC address of the target device.")
    args = parser.parse_args()

    bind_rfcomm(args.mac_address)
