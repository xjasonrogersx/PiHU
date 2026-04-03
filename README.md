# PiHU

A Pi based Linux headunit

# Logo

| 1                             | 2                             |
| ----------------------------- | ----------------------------- |
| ![](images/1775205902337.png) | ![](images/1775206450840.png) |

Plan

- Simple fun GUI
- Supports OpenAuto Somehow
- Supports Dab Radio
- Using Buster

# GUI

Something like this but not this compex

| mockup 1 | mockup 2 |
| -- | -- |
| ![](images/1775207006248.png) | ![](images/1775206749039.png) |

[discussions](discussions/tkinter.md)
[discussions](discussions/tkinter1.md)

# Dab Radio intergarions

wip

# MQTT

[discussions](discussions/mqtt.md)

Topics

| topic                     | description                                       |
| ------------------------- | ------------------------------------------------- |
| car/speed                 |                                                   |
| car/HU/bg_image           | index of backgrond image to display - for testing |
| car/HU/volume             | 0% - 100% volume                                  |
| car/dab/set_station       | request a station <frequency subchannel bitrate>  |
| car/dab/frequency         | current                                           |
| car/dab/subchannel        | current                                           |
| car/dab/bitrate           | current                                           |
| car/dab/programme_type    | current                                           |
| car/dab/programme_service | current                                           |
| car/dab/ensemble          | current                                           |

## How to install mosquito

install:

```bash
sudo apt install mosquitto mosquitto-clients
```

start:

```bash
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

or

```
docker exec -it gracious_rubin mosquitto

mosquitto_pub -h localhost -t car/speed -m "60"
```

## OpenAuto

So this is the nightmare bit. I have tried and fails multiple times to install and build OpenAuto.

https://github.com/opencardev/openauto

Crankshaft did work, but its not quite what I want.

links:

https://github.com/opencardev/prebuilts



installations

## Images

![](images/1775206081435.png)
