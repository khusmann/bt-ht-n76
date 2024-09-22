import socket
import typing as t


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


def bind_rfcomm():
    # Define the Bluetooth MAC address and the RFCOMM channel
    # Replace with your target device's MAC address
    target_device_mac = "XXX"
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

            print("Received data (hex dump):")
            hexdump(data)

    except socket.error as e:
        print(f"Error: {e}")
    finally:
        if sock:
            sock.close()
        print()
        print("Disconnected.")


if __name__ == "__main__":
    bind_rfcomm()
