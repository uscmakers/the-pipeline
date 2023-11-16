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


## Cura Setup

Install latest version of Cura. Then copy all json files under `cura-resources` into their respective folders in `C:\Program Files\Ultimakers Cura 5.0.0\share\cura\resources\` or where Cura keeps its config files. If you need further assistance on this step please watch this video on [how to add SOVOL SV04 Printer into Cura 5.0](https://www.youtube.com/watch?v=4KL_7jbV8KM) but use the files from this repo. You should preferably `git clone` this repo to make copying easier since there are many folders and files.
