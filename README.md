# Bluetooth Protocol for VERO VR N76/ Radioddity GA-5WB, BTECH UV-pro

## Creating BT Logs in Android

First, enable "Enable Bluetooth HCI snoop log" in the developer options.

Turn bluetooth off and on again. Now you can use the app to control the HT and
the bluetooth commands will be recorded.

Then, run the following command to create a bug report:

```
adb bugreport bugreport_name
```

Use wireshark to read the log found in:

```
FS/data/misc/bluetooth/logs/btsnoop_hci.log
```

For more info,
[this is a good resource](https://reverse-engineering-ble-devices.readthedocs.io/en/latest/protocol_reveng/00_protocol_reveng.html#logging-via-android).

## Log Analysis

I found that the app uses the rfcomm (AKA SPP) protocol to communicate with the
HT. It uses channel 1 for some commands and to transfer tx and rx sound clips.
Then channel 3 is used for most of the data (channel info, APRS data, etc.)

It does NOT use the more modern GATT protocol, which is for BLE.

## Pairing with the device in Linux

`bluetoothctl` is a command line utility that can be used to interact with
bluetooth devices. Here we use it to connect to the HT

```
sudo bluetoothctl
```

You'll get a console where you can interact with the bluetooth devices:

```
scan on # Start scanning for devices
scan off # Stop scanning for devices
pair XX:XX:XX:XX:XX:XX # Pair with the device
trust XX:XX:XX:XX:XX:XX # Trust the device
connect XX:XX:XX:XX:XX:XX # Connect to the device
disconnect XX:XX:XX:XX:XX:XX # Disconnect from the device
```

When you connect to the device, it seems to connect as a headset. It's not
necessary to connect to the device to send commands, however -- you can just

## Connecting to the device

There are a lot of examples of connecting to rfcomm channels with
[pybluez](https://github.com/pybluez/pybluez), but it doesn't seem to be
actively developed anymore.

Instead, we can use the built-in socket library in python to connect to the
device. See [simple_connect.py] for an example without error handling:

```bash
python3 simple_connect.py XX:XX:XX:XX:XX:XX
```

## Weird bug: Data channel gets "clogged" after disconnecting.

If you run the above code after freshly turning on the radio, it will work. But
if you quit and then try to run it again, connecting to the data channel will
result in a "Connection Refused" error.

If you turn the device on and off again, it will work again. But the app appears
to not have this problem. After some digging I found that the app will just move
to the next channel! So if you try to connect on channel 3 and it fails, try
channel 4, then 5, etc. Perhaps this will be fixed in future firmwares?

## Next steps

Start twiddling settings and figure out the commands!

## Odds and ends

### GATT

GATT services and characteristics can be probed with `gatttool`:

```bash
gatttool -b XX:XX:XX:XX:XX:XX -I
```

```
connect # Connect to the device
char-desc # List all characteristics
characteristics # List all characteristics
char-read-uuid <UUID> # Read a characteristic
disconnect # Disconnect from the device
```

### rfcomm

`rfcomm` can also be used to bind the device to a virtual serial port:

```bash
sudo rfcomm bind /dev/rfcomm0 XX:XX:XX:XX:XX:XX 1
```

This will bind the device to `/dev/rfcomm0` on channel 1.

You can then view the data being sent to the device with:

```bash
sudo cat /dev/rfcomm0
```

You can also send data to the device with:

```bash
echo -n -e '\x7e\x02\x00\x00\x00\x00\x00\x00\x00\x00\x7e' | sudo tee /dev/rfcomm0
```

When you're done, you can unbind the device with:

```bash
sudo rfcomm release /dev/rfcomm0
```

You can look at the status via

```bash
sudo rfcomm
```

### Serial

You can connect to a bound rfcomm via a terminal emulator like picocom as well:

```bash
picocom /dev/rfcomm0 -b 9600
```

Also pyserial:

```python
import serial

ser = serial.Serial('/dev/rfcomm0', 9600)
ser.write(b'\x7e\x02\x00\x00\x00\x00\x00\x00\x00\x00\x7e')

while True:
    print(ser.read())
```

Note that the baud rate doesn't really mean anything in this context; The
bluetooth stack handles everything under the surface...

## Resources

- https://reverse-engineering-ble-devices.readthedocs.io/en/latest/protocol_reveng/00_protocol_reveng.html
