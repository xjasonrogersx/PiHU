# PiHU

A Pi based Linux headunit from my car.  

I currently have a cheap chinese 10.1" Android head unit.  This can do Android Auto and Dab Radio but does have it's issues.  Sometimes it loosed Audio after a short stop and requres a reboot - not very conveniuent while driving.    

I'll document the development as I go, including my discussions with Gemenai and Co-Pilot. (Don't tell Gemenai I'm talking with Co-Pilot,  he'll get jellous)

# Logo

First things first,  Desing a logo with Gemani

| 1                             | 2                             |
| ----------------------------- | ----------------------------- |
| ![](images/1775205902337.png) | ![](images/1775206450840.png) |

# The Plan

Make some requirments

- Simple fun GUI
- Supports OpenAuto Somehow 
- Supports Dab Radio
- Using Buster ( becuase apparently this is what OpenAuto requires )

# GUI #1

Something like this but not this compex

| mockup 1 | mockup 2 |
| -- | -- |
| ![](images/1775207006248.png) | ![](images/1775206749039.png) |

[discussions](discussions/tkinter.md)
[discussions](discussions/tkinter1.md)

Full details on the Gui develoment [here](gui/README.md)

# Dab Radio intergarions

This is the dongle I currently have.
Its apparenly a keystone dab chip rathern than a SDR based dongle.  

| 1 | 2 |
| -- | -- |
| ![img](images/dab-dongle1.jpeg) | ![img](images/dab-dongle2.jpeg) |

Full details on Dab intergration [here](dab/README.md)


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
