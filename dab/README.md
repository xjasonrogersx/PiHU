# DAB

```
pi@PiHU:~ $ lsusb
Bus 001 Device 005: ID 16c0:05dc Van Ooijen Technische Informatica shared ID for use with libusb
Bus 001 Device 003: ID 0424:ec00 Standard Microsystems Corp. SMSC9512/9514 Fast Ethernet Adapter
Bus 001 Device 002: ID 0424:9514 Standard Microsystems Corp. SMC9514 Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```

```
sudo nano /etc/udev/rules.d/99-dab.rules

SUBSYSTEM=="usb", ATTRS{idVendor}=="16c0", ATTRS{idProduct}=="05dc", MODE="0666"

```

## DabLin

I install dablin an

```
sudo apt update
sudo apt install dablin rtl-sdr
```

##

https://github.com/chrisjohnson1988/dab-radio?tab=readme-ov-file

```
pi@PiHU:~/dab-radio $ ./dab_scan
[RaonUsbTuner] Powering up
[RaonUsbTuner] PowerUp okay!
[RaonUsbTuner] Setting up MSC Threshold...
[RaonUsbTuner] Setting up FIC Memory...
[RaonUsbTuner] Initialized
Creating Scanner
[RaonUsbTuner] Tuning Frequency: 174928000
[RaonUsbTuner] Tuning Frequency: 176640000
[RaonUsbTuner] Tuning Frequency: 178352000
[RaonUsbTuner] Tuning Frequency: 180064000
[RaonUsbTuner] Tuning Frequency: 181936000
[RaonUsbTuner] Tuning Frequency: 183648000
[RaonUsbTuner] Tuning Frequency: 185360000
[RaonUsbTuner] Tuning Frequency: 187072000
[RaonUsbTuner] Tuning Frequency: 188928000
[RaonUsbTuner] Tuning Frequency: 190640000
[RaonUsbTuner] Tuning Frequency: 192352000
[RaonUsbTuner] Tuning Frequency: 194064000
[RaonUsbTuner] Tuning Frequency: 195936000
[RaonUsbTuner] Tuning Frequency: 197648000
[RaonUsbTuner] Tuning Frequency: 199360000
[RaonUsbTuner] Tuning Frequency: 201072000
[RaonUsbTuner] Tuning Frequency: 202928000
[RaonUsbTuner] Tuning Frequency: 204640000
FICDecoder: SId 0xC6D6: audio service (SubChId 14, DAB+, primary)
FICDecoder: SId 0xC7D9: audio service (SubChId 15, DAB+, primary)
FICDecoder: SId 0xCF84: audio service (SubChId 16, DAB+, primary)
FICDecoder: SId 0xCAD6: audio service (SubChId 17, DAB+, primary)
FICDecoder: SId 0xC8D4: audio service (SubChId 18, DAB+, primary)
FICDecoder: SId 0xCD90: audio service (SubChId 19, DAB+, primary)
FICDecoder: SId 0xC9C3: audio service (SubChId 20, DAB+, primary)
FICDecoder: SId 0xCBD4: audio service (SubChId 21, DAB+, primary)
FICDecoder: SId 0xCFF2: audio service (SubChId 22, DAB+, primary)
FICDecoder: SId 0xCCD4: audio service (SubChId 23, DAB+, primary)
FICDecoder: SId 0xCED4: audio service (SubChId 24, DAB+, primary)
FICDecoder: SId 0xC1D5: audio service (SubChId 25, DAB+, primary)
FICDecoder: SId 0xCFE3: audio service (SubChId 26, DAB+, primary)
FICDecoder: SId 0xC758: audio service (SubChId 27, DAB+, primary)
FICDecoder: SId 0xCA5F: audio service (SubChId 28, DAB+, primary)
FICDecoder: UTC date/time: 2026-04-03, Fri - 13:57:00.776
FICDecoder: SId 0xCDC2, SCIdS  0: Slideshow (2 bytes UA data)
FICDecoder: SId 0xCDC2: programme type (dynamic): 'Oldies Music'
FICDecoder: SubChId 28: start 768 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId 27: start 738 CUs, size  30 CUs, PL EEP 3-A =  40 kBit/s
FICDecoder: SubChId 26: start 714 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId 25: start 690 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId 24: start 654 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s
FICDecoder: SubChId 23: start 630 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId 22: start 606 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId 21: start 582 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId 20: start 558 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId 19: start 510 CUs, size  48 CUs, PL EEP 3-A =  64 kBit/s
FICDecoder: SubChId 18: start 474 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s
FICDecoder: SubChId 17: start 438 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s
FICDecoder: SubChId 16: start 390 CUs, size  48 CUs, PL EEP 3-A =  64 kBit/s
FICDecoder: SubChId 15: start 366 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId 14: start 342 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId 13: start 318 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId 12: start 294 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId 11: start 270 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId 10: start 234 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s
FICDecoder: SubChId  9: start 210 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId  8: start 186 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId  7: start 150 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s
FICDecoder: SubChId  6: start 132 CUs, size  18 CUs, PL EEP 3-A =  24 kBit/s
FICDecoder: SubChId  5: start 108 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId  4: start  72 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s
FICDecoder: SubChId  3: start  48 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId  2: start  24 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId  1: start   0 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SId 0xCDC2: audio service (SubChId  1, DAB+, primary)
FICDecoder: SId 0xC080: audio service (SubChId  2, DAB+, primary)
FICDecoder: SId 0xC0EB: audio service (SubChId  3, DAB+, primary)
FICDecoder: SId 0xCDD4: audio service (SubChId  4, DAB+, primary)
FICDecoder: SId 0xCFD8: audio service (SubChId  5, DAB+, primary)
FICDecoder: SId 0xCFFC: audio service (SubChId  6, DAB+, primary)
FICDecoder: SId 0xC254: audio service (SubChId  7, DAB+, primary)
FICDecoder: SId 0xCDF6: audio service (SubChId  8, DAB+, primary)
FICDecoder: SId 0xC55A: audio service (SubChId  9, DAB+, primary)
FICDecoder: SId 0xC092: audio service (SubChId 10, DAB+, primary)
FICDecoder: SId 0xC15C: audio service (SubChId 11, DAB+, primary)
FICDecoder: SId 0xCA91: audio service (SubChId 12, DAB+, primary)
FICDecoder: SId 0xC1D0: audio service (SubChId 13, DAB+, primary)
FICDecoder: EId 0xC1C6: ensemble label 'London N' ('London N')
FICDecoder: SId 0xCDC2: programme service label 'Angel Vintage' ('Angel')
FICDecoder: SId 0xC080: programme service label 'ASIAN STAR RADIO' ('ASIANSTR')
FICDecoder: SId 0xC0EB: programme service label 'CAMDEN XPERIENCE' ('CDNX')
FICDecoder: SId 0xCDD4: programme service label 'Delite Radio' ('Delite')
FICDecoder: SId 0xCFD8: programme service label 'Fun Kids' ('Fun Kids')
FICDecoder: SId 0xCFFC: programme service label 'GreekBeat Radio' ('GrkBeat')
FICDecoder: SId 0xC254: programme service label 'House FM' ('House FM')
FICDecoder: SId 0xCDF6: programme service label 'KOOL FM' ('KOOL FM')
FICDecoder: SId 0xC55A: programme service label 'Liberty Radio' ('Liberty')
FICDecoder: SId 0xC092: programme service label 'LGR' ('LGR')
FICDecoder: SId 0xC15C: programme service label 'HELLAS RADIO UK' ('HELLAS')
FICDecoder: SId 0xCA91: programme service label 'Nagrecha Radio' ('Nagrecha')
FICDecoder: SId 0xC1D0: programme service label 'Polish Radio Ldn' ('Polish')
FICDecoder: SId 0xC6D6: programme service label 'Radio Caroline' ('Caroline')
FICDecoder: SId 0xC7D9: programme service label 'Rainbow Radio' ('Rainbow')
FICDecoder: SId 0xCF84: programme service label 'Reprezent' ('Repreznt')
FICDecoder: SId 0xCAD6: programme service label 'Resonance FM' ('Res')
FICDecoder: SId 0xC8D4: programme service label 'Resonance Extra' ('ResExtra')
FICDecoder: SId 0xCD90: programme service label 'RINSE FM' ('RINSE FM')
FICDecoder: SId 0xC9C3: programme service label 'BOOM ROCK' ('BOOMROCK')
FICDecoder: SId 0xCFF2: programme service label 'Shine 879' ('Shine879')
FICDecoder: SId 0xCED4: programme service label 'Solar Radio' ('Solar')
[RaonUsbTuner] Tuning Frequency: 206352000
FICDecoder: SubChId  8: start 216 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s
FICDecoder: SubChId  9: start 252 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s
FICDecoder: SubChId 10: start 288 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s
FICDecoder: SubChId 11: start 312 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s
```

Saving a stream to a file:

```
./dab_aac 216928000 21 32 > absolute90s.aac
```

Piping to FFplay

```
./dab_aac 216928000 21 32 | ffplay -i - -nodisp
```

```
# Run this before starting the tuner
mkfifo /tmp/dab_pipe
chmod 666 /tmp/dab_pipe
```

```
ffplay -i /tmp/dab_pipe -nodisp -autoexit
```

Forcing to headphones

```
PULSE_SINK=0 ffplay -i /tmp/dab_pipe -nodisp
```

```
mkfifo /tmp/dab_pipe
chmod 666 /tmp/dab_pipe
PULSE_SINK=0 ffplay -ar 48000 -i /tmp/dab_pipe -nodisp -fflags nobuffer
```

## Buster specific Audio

```
pi@PiHU:/tmp $ aplay -l
**** List of PLAYBACK Hardware Devices ****
card 0: Headphones [bcm2835 Headphones], device 0: bcm2835 Headphones [bcm2835 Headphones]
  Subdevices: 8/8
  Subdevice #0: subdevice #0
  Subdevice #1: subdevice #1
  Subdevice #2: subdevice #2
  Subdevice #3: subdevice #3
  Subdevice #4: subdevice #4
  Subdevice #5: subdevice #5
  Subdevice #6: subdevice #6
  Subdevice #7: subdevice #7

```

```
pi@PiHU:/tmp $ pactl list short sinks
0	alsa_output.platform-bcm2835_audio.analog-stereo	module-alsa-card.c	s16le 2ch 48000Hz	SUSPENDED

```
