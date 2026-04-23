# DAB Radio

This repository contains some command line tools which can control DAB radio dongles which are often sold as Android DAB dongles. I believe these dongles are based upon the MTV318 chip manufactured by Roantech. These tuners have a 10 bit adc which is able to get better reception of weaker transmissions than rtl-sdr based tuners (which only have an 8 bit adc). The **NXB110** by Nexell seems to be the best fit when looking for a datasheet to document how to control the tuner. The tuner I have has the vendor id `0x16c0` and product ids `0x05dc`.

My main aim for this project is to add DAB radio stations to [tvheadend](https://tvheadend.org/) by producing an `.m3u` file which can be added as an IPTV feed (leveraging the pipe:// syntax). See [Custom MPEG-TS Input](https://tvheadend.org/projects/tvheadend/wiki/Custom_MPEG-TS_Input0)

## Installation

In order to build the project, your system will require

- libusb-1.0-dev
- libmosquitto-dev (for MQTT-controlled tuner)
- nlohmann-json3-dev (for MQTT-controlled tuner)
- cmake
- g++

To install dependencies on Ubuntu/Debian:

```bash
sudo apt install libusb-1.0-dev libmosquitto-dev nlohmann-json3-dev cmake build-essential
```

To build the code:

```bash
cd /home/jason/work/RootPiHu/PiHU
mkdir build
cd build
cmake ..
make
```

The compiled executables will be located in `build/dab/dab-radio/`:

Grant access to the usb device. Create a file /etc/udev/rules.d/50-dab-radio.rules with the following content

        SUBSYSTEMS=="usb", ATTR{idVendor}=="16c0", ATTR{idProduct}="05dc", GROUP="users", MODE="0666"

## Tools

### dab_scan

Scans all DAB frequencies and outputs a playlist file (dab.m3u) with discovered stations.

```bash
./dab_scan
```

### dab_mp2

Tunes to a specific DAB station and decodes MP2 audio. Takes frequency, subchannel, and bitrate as arguments.

```bash
./dab_mp2 <frequency_hz> <subchannel> <bitrate>
# Example: dab_mp2 225648000 1 64
```

### dab_aac

Tunes to a specific DAB+ station and decodes AAC audio. Takes frequency, subchannel, and bitrate as arguments.

```bash
./dab_aac <frequency_hz> <subchannel> <bitrate>
# Example: dab_aac 230640000 1 128
```

### dab_tuner_aac

MQTT-controlled DAB+ radio tuner with AAC audio decoder. Listens to MQTT messages on `car/dab/tune_to` topic for tuning commands. This is useful for integrating with home automation systems or building a networked radio interface.

**Usage:**

```bash
./dab_tuner_aac [broker_host] [broker_port]
# Example: dab_tuner_aac localhost 1883
```

**Dependencies:**

- Mosquitto MQTT broker running on specified host:port
- JSON library for parsing tune commands

**MQTT Topics:**

- **Subscription:** `car/dab/tune_to` - receives JSON tune commands
- **Format:** `{"frequency": 230640000, "subchannel": 1, "bitrate": 128}`

**Starting the MQTT Broker:**

```bash
# Install mosquitto if not already installed
sudo apt install mosquitto mosquitto-clients

# Start the broker
sudo systemctl start mosquitto

# Send a tune command
mosquitto_pub -h localhost -t car/dab/tune_to -m '{"frequency":230640000,"subchannel":1,"bitrate":128}'
```

## Scanning for Stations

Running `./dab_scan` will produce a `dab.m3u` playlist. This can be added to TV Headend as an **IPTV Automatic Network** under **Configuration > DVB Inputs >> Networks**. A full scan takes approximately 2 minutes and will produce a m3u file with content similar to this:

        #EXTM3U
        #EXTINF:-1, BBC Radio 1
        pipe:///opt/dab-radio/dab_mpegts 'BBC National DAB' 'BBC Radio 1' 225648000 1 mp2
        #EXTINF:-1, BBC Radio 2
        pipe:///opt/dab-radio/dab_mpegts 'BBC National DAB' 'BBC Radio 2' 225648000 2 mp2
        #EXTINF:-1, BBC Radio 3
        pipe:///opt/dab-radio/dab_mpegts 'BBC National DAB' 'BBC Radio 3' 225648000 3 mp2
        #EXTINF:-1, BBC Radio 4
        pipe:///opt/dab-radio/dab_mpegts 'BBC National DAB' 'BBC Radio 4' 225648000 4 mp2

## Future work

Multiple radio stations are broadcast on the same frequency, segmented on different logical subchannels. Ideally, all the subchannels would be muxed on to the same mpegts stream resulting in each frequency being listed in the m3u file once.

## Credits

The code in this project is based on:

- https://github.com/Opendigitalradio/dablin
- https://github.com/hradio/omri-usb
