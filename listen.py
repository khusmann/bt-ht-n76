import socket
import typing as t
import argparse
import select
import time
import threading


# Global flag to control the shutdown of threads
stop_event = threading.Event()


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
        print(f'{i:08x}  {hex_values:<48}  {ascii_values}\n')


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


def listen_for_data(sock: socket.socket):
    while not stop_event.is_set():
        ready_to_read, _, _ = select.select([sock], [], [], 1.0)

        if ready_to_read:
            data = sock.recv(1024)
            if not data:
                break

            print()

            if is_valid_packet(data):
                decode_packet(data[1:-1])
            else:
                print("Invalid packet:")
                print(hexdump(data))

            # Print command prompt again
            print("\nEnter command: ", end='')

        else:
            time.sleep(0.1)


def command_prompt(sock: socket.socket):
    while not stop_event.is_set():
        command = input("Enter command: ")
        if command.strip() == "aprs":
            byte_string = b'\x7e\x02\x00\x00\x00\x00\x00\x00\x00\x00\x7e'
            print(sock.send(byte_string))
            print("Sent byte string:", byte_string.hex())
        else:
            print("Unknown command. Available commands: aprs")


def bind_rfcomm(target_device_mac: str):
    channel = 1
    sock: t.Optional[socket.socket] = None

    try:
        sock = socket.socket(socket.AF_BLUETOOTH,
                             socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        sock.connect((target_device_mac, channel))
        print(f"Connected to {target_device_mac} on RFCOMM channel {channel}.")

        # Start a thread for listening to incoming data
        listener_thread = threading.Thread(
            target=listen_for_data, args=(sock,), daemon=True)
        listener_thread.start()

        # Start the command prompt in the main thread
        command_prompt(sock)

    except socket.error as e:
        print(f"Error: {e}")
    finally:
        stop_event.set()  # Signal threads to stop
        if sock:
            sock.close()
        print("Disconnected.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Connect to a Bluetooth device via RFCOMM.")
    parser.add_argument("mac_address", type=str,
                        help="Bluetooth MAC address of the target device.")
    args = parser.parse_args()

    try:
        bind_rfcomm(args.mac_address)
    except KeyboardInterrupt:
        print("\nShutting down...")
        stop_event.set()  # Signal threads to stop
