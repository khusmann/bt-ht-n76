import socket
import typing as t
import argparse
import select
import time
import threading


# Global flag to control the shutdown of threads
stop_event = threading.Event()


def hexdump(data: bytes):
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_values = ' '.join(f'{byte:02x}' for byte in chunk)
        ascii_values = ''.join(chr(byte) if 32 <= byte <=
                               126 else '.' for byte in chunk)
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


def listen_for_cmd(sock: socket.socket):
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


def listen_for_data(sock: socket.socket):
    while not stop_event.is_set():
        ready_to_read, _, _ = select.select([sock], [], [], 1.0)

        if ready_to_read:
            data = sock.recv(1024)
            if not data:
                break

            print()
            print("Received data:")
            hexdump(data)

            # Print command prompt again
            print("\nEnter command: ", end='')

        else:
            time.sleep(0.1)


def command_prompt(command_sock: socket.socket, data_sock: socket.socket):
    while not stop_event.is_set():
        command = input("Enter command: ")
        if command.strip() == "test1":
            command_sock.send(b'\x7e\x02\x00\x00\x00\x00\x00\x00\x00\x00\x7e')
        elif command.strip() == "test2":
            data_sock.send(b'\xff\x01\x00\x01\x00\x02\x00\x04\x03')
            data_sock.send(
                b'\xff\x01\x00\x10\x00\x02\x00\x20\x14\x2e\x0a\xc7\xa2\xfe\x00\x64\xff\xff\xff\xff\x66\xef\x8b\x6c'
            )
            data_sock.send(b'\xff\x01\x00\x00\x00\x02\x00\x16')
            data_sock.send(b'\xff\x01\x00\x01\x00\x02\x00\x06\x01')
            data_sock.send(b'\xff\x01\x00\x00\x00\x02\x00\x0a')
            data_sock.send(b'\xff\x01\x00\x01\x00\x02\x00\x2c\x01')
            data_sock.send(b'\xff\x01\x00\x01\x00\x02\x00\x0d\x00')
        elif command.strip() == "test3":
            command_sock.send(b'\x7e\x02\x00\x00\x00\x00\x00\x00\x00\x00\x7e')
            command_sock.send(b'\x7e\x02\x00\x00\x00\x00\x00\x00\x00\x00\x7e')
            # data_sock.send(b'\xff\x01\x00\x00\x00\x02\x00\x16')
            data_sock.send(
                b'\xff\x01\x00\x19\x00\x02\x00\x0e\x03\x08\xb2\x41\xe0\x08\xb2\x41\xe0\x00\x00\x00\x00\x15\x00\x62\x6c\x61\x68\x00\x00\x00\x00\x00\x00'
            )
        elif command.strip() == 'test4':
            command_sock.send(b'\x7e\x02\x00\x00\x00\x00\x00\x00\x00\x00\x7e')
            time.sleep(0.1)
            command_sock.send(
                b'\xff\x01\x00\x19\x00\x02\x00\x0e\x03\x08\xb3\xc8\x80\x08\xb3\xc8\x80\x00\x00\x00\x00\x15\x00\x62\x69\x6e\x67\x00\x00\x00\x00\x00\x00'
            )
            command_sock.send(
                b'\xff\x01\x00\x00\x00\x02\x00\x16'
            )
        elif command.strip() == "test5":
            command_sock.send(b'\x7e\x02\x00\x00\x00\x00\x00\x00\x00\x00\x7e')
            data_sock.send(
                b'\xff\x01\x00\x19\x00\x02\x00\x0e\x03\x08\xb3\xc8\x80\x08\xb3\xc8\x80\x00\x00\x00\x00\x15\x00\x62\x69\x6e\x67\x00\x00\x00\x00\x00\x00'
            )
            data_sock.send(
                b'\xff\x01\x00\x00\x00\x02\x00\x16'
            )
            data_sock.send(
                b'\xff\x01\x00\x00\x00\x02\x00\x0c'
            )
            data_sock.send(
                b'\xff\x01\x00\x14\x00\x02\x00\x0b\x3f\x01\xa6\x06\x58\x10\x3c\xa0\xa1\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00'
            )

        else:
            print("Unknown command.")


def bind_rfcomm(target_device_mac: str):
    data_channel = 3
    command_channel = 1
    data_sock: t.Optional[socket.socket] = None
    command_sock: t.Optional[socket.socket] = None

    try:
        # Data socket
        data_sock = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        data_sock.connect((target_device_mac, data_channel))
        print(
            f"Connected to {target_device_mac} on RFCOMM channel {data_channel} (data socket).")

        # Command socket
        command_sock = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        command_sock.connect((target_device_mac, command_channel))
        print(
            f"Connected to {target_device_mac} on RFCOMM channel {command_channel} (command socket).")

        # Start a thread for listening to incoming data
        cmd_listener_thread = threading.Thread(
            target=listen_for_cmd, args=(command_sock,), daemon=True
        )
        cmd_listener_thread.start()

        data_listener_thread = threading.Thread(
            target=listen_for_data, args=(data_sock,), daemon=True
        )
        data_listener_thread.start()

        # Start the command prompt in the main thread
        command_prompt(command_sock, data_sock)

    except socket.error as e:
        print(f"Error: {e}")
    finally:
        stop_event.set()  # Signal threads to stop
        if data_sock:
            data_sock.close()
        if command_sock:
            command_sock.close()
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
