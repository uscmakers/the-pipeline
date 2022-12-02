# the-pipeline
Fully automated IDEX 3D printer with Slackbot support

## Canbus Setup

Create a new file in RPi /etc/network/interfaces.d/can0 with the following contents:

'''
allow-hotplug can0
iface can0 can static
    bitrate 250000
    up ifconfig $IFACE txqueuelen 128
'''
