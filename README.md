# Bluetooth Protocol for VERO VR N76/ Radioddity GA-5WB, BTECH UV-pro

This repo is very much a work in progress, and is in the "proof of concept"
stages.

Backstory: I have a Radiooddity GA-5WB and am enjoying the device even with all
of its quirks. The thing that really bothers me is the app. Sure, it's nice to
be able to program my phone over bluetooth using my phone, but:

1. I can't connect to the HT via bluetooth using my computer
2. I can't write my own apps for the HT
3. When they stop maintaining the app the HT loses much of its value because
   nothing will be able to program it

So, I've been poking around with the bluetooth protocol to see what I can figure
out.

Here's the quick summary:

1. The app uses bluetooth SPP to communicate with and control the HT
2. I can connect to and control the HT in both Python, and the web serial API
   _(this means we can write apps for the HT in the browser!)_
3. I can see the audio streams in Python (on RFCOMM channel 1), but haven't been
   able to access the audio in the web API

## Quick start

The easiest way to see it working is to try out the web serial API interface.
First you need to pair your device with your computer (put the HT in pairing
mode and use your bluetooth settings manager or whatever to connect to it). Then
all you need to do is go to
[this page](https://html-preview.github.io/?url=https://github.com/khusmann/bt-ht-n76/blob/main/simple_connect.html).

DISCLAIMER: I AM NOT RESPONSIBLE FOR ANY DAMAGE YOU DO TO YOUR DEVICE. BY USING
THIS YOU UNDERSTAND THIS IS SUPER EXPERIMENTAL SOFTWARE AND ARE RESPONSIBLE FOR
ANY CONSEQUENCES.

(Also note that I haven't upgraded my firmware yet (still on 0.6.9), and have no idea if there are any differences in the later versions... again, try the demo at your own risk!

Click "Connect to bluetooth device" and find your device, and it should connect.
I have two example commands ready to send -- the one to enable APRS reports, and
the one to print out the settings of channel one. Try them out and see what
happens. Also try changing settings on the radio, and you should see it send
updates as you change things. (TRY AT YOUR OWN RISK)

Here's what it looks like for me connecting to the device, enabling APRS reports, looking at channel 01 settings (You can see I have a channel named HarnessMtn), and then switching a couple channels on the device:

[![image](https://github.com/user-attachments/assets/28ddb184-ede1-4a57-b963-c4549addbbd0)](https://html-preview.github.io/?url=https://github.com/khusmann/bt-ht-n76/blob/main/simple_connect.html)


The Python script I've included has a little bit more features -- it allows you
to also see the audio clips the device sends as it receives them. Those of you
who know what you're doing can check it out.

From here, it's just a matter of us taking the time and the elbow grease to
reverse engineer the protocol being used. Thankfully it looks really simple!

The the two main ways of doing this is by creating BT logs in Android, and by
decompiling the apk. Here's a
[great resource for how to go about this](https://reverse-engineering-ble-devices.readthedocs.io/en/latest/protocol_reveng/00_protocol_reveng.html).

I've poked around with both approaches, and can confidently say that this is
totally do-able, it'll just take time. Here's
[some assorted notes I made](NOTES.md) while poking around that might be useful
to somebody.

Unfortunately I don't have much time to go much further on this project for now,
and need to catch up on other things... Anyone who can contribute, please jump
in! I'll be able to circle back in a bit.

## Where to go from here

The big feature I think is missing from these HTs is the ability to use the KISS
protocol, so they can be used with OSS like APRSDroid. I think the best way to
do this would be to write a little TCP server that runs on the phone and listens for
KISS packets, then translates them into the proper BT serial commands. This way,
we can use the HT with any [APRS program that supports KISS over TCP](https://github.com/ge0rg/aprsdroid/issues/300)!

(Side note: PLEASE DEMAND OF MANUFACTURERS THAT THEY SUPPORT KISS RIGHT OUT OF
THE BOX. WE SHOULDN'T HAVE TO HACK TOGETHER SOLUTIONS LIKE THIS. SERIOUSLY,
EMAIL THE SUPPORT TEAM OF YOUR DEVICE MANUFACTURER RIGHT NOW AND TELL THEM YOU REALLY WISH
YOUR DEVICE HAD KISS)

But also, once we know the full protocol, the sky's the limit for
controlling and programming the device! We could, for example, have web-based
programmers that use the web serial API to program in repeater settings, you
could have a web-based APRS interface, etc. etc. etc.

## Note structure of APRS SPP messages

The standard header looks like this:

ff:01:00:37:00:02:00:09:<message>

Here's the breakdown:

bytes[0:3] = ff:01:00 <- A standard header, doesn't change

bytes[3] = 37 <- The length of the message

bytes[4:6] = 00:02 <- Another standard header, doesn't change

bytes[6] = 00 <- Whether the message is a response or a command (0x00 for
command, 0x80 for response)

bytes[7] = 09 <- The command (0x09 for APRS message)

Here's what the <message> looks like for a multipart aprs update:

02:00:<ax.25 frame start>

02:01:<ax.25 frame continued>

02:82:<message frame end>

The first byte (0x02) doesn't seem to change. The second byte is the part number
of the message, in the form 0b0000XYYY, where X is 1 for the last message part,
and 0 for the rest. YYY is the message number.
