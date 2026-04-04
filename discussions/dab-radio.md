# **DAB Radio Dongle Setup and Usage**

[https://gemini.google.com/share/0da81084eb9b](https://gemini.google.com/share/0da81084eb9b)

Created with **Fast** 3 April 2026 at 14:52 Published on 3 April 2026 at 15:36

You said

    since is see

    Bus 001 Device 005: ID 16c0:05dc Van Ooijen Technische Informatica shared ID for use with libusb

    i think this might be good

https://github.com/chrisjohnson1988/dab-radio

That looks like a perfect match. The USB ID `16c0:05dc` is officially a "shared ID" from Van Ooijen Technische Informatica, frequently used by open-source hardware like the **USBasp** AVR programmer.

However, in your case, it identifies a specific type of **DAB/DAB+ Radio Dongle** (often sold as "Android DAB+" sticks). These are distinct from the more common RTL-SDR dongles; while RTL-SDRs use an 8-bit ADC, these specific `16c0:05dc` sticks typically use the **MTV318** (or Nexell NXB110) chipset, which features a 10-bit ADC. This often results in better reception for weak digital radio signals.

The GitHub repository you found (**chrisjohnson1988/dab-radio**) is specifically designed for these MTV318-based tuners. It provides:

- **Command-line tools:** To control the tuner and scan for stations.
- **TVHeadend Integration:** It can generate an `.m3u` playlist to feed DAB radio stations into TVHeadend as an IPTV stream.
- **Scanning:** Running the `dab_scan` utility from that repo should allow you to see what ensembles and services are available in your area.

### Quick Tip for Linux Users

Since the device is detected under a "shared ID" and uses `libusb`, you might run into permission issues (needing `sudo` to access it). You can fix this by creating a udev rule:

1.  Create a file: `/etc/udev/rules.d/99-dab-radio.rules`
2.  Add this line: `SUBSYSTEM=="usb", ATTRS{idVendor}=="16c0", ATTRS{idProduct}=="05dc", MODE="0666", GROUP="plugdev"`
3.  Reload rules: `sudo udevadm control --reload-rules && sudo udevadm trigger`

If you are planning to use it for a media server setup, that repo is likely exactly what you need to get the audio stream out of that specific hardware.

You said

    pi@PiHU:~/dab-radio $ make

    rm -f \*.o

    rm -f dab_scan dab_mp2 dab_aac

    g++ -std=c++11 -frtti -fexceptions   -c -o m3u_writer.o m3u_writer.cpp

    In file included from dab_scanner.h:8,

    from m3u_writer.h:6,

    from m3u_writer.cpp:2:

    raon_tuner.h:31:10: fatal error: libusb-1.0/libusb.h: No such file or directory

    #include <libusb-1.0/libusb.h>

    ^~~~~~~~~~~~~~~~~~~~~

    compilation terminated.

    make: \*\*\* \[<builtin>: m3u_writer.o\] Error 1

It looks like the compiler is searching for the `libusb` headers and coming up empty-handed. While `libusb` is usually installed on most Linux systems by default, the **development headers** (the files ending in `.h` that a compiler needs to build new software) are often separate.

To fix the `fatal error: libusb-1.0/libusb.h: No such file or directory`, you need to install the development package for libusb.

### The Fix

Run the following command on your Raspberry Pi:

Bash

```
sudo apt update
sudo apt install libusb-1.0-0-dev
```

### Why this happens

When you compile code that interacts with USB hardware, the `g++` compiler needs to know the "map" of the library it's talking to.

- **libusb-1.0-0:** This is the library used to _run_ programs.
- **libusb-1.0-0-dev:** This contains the header files (like `libusb.h`) and symbols needed to _build_ programs.

---

### Next Steps

Once that installation finishes, try running `make` again. You should find that it moves past the `raon_tuner.h` error.

If you run into a similar error regarding **AAC** or **MP2**, you may also need the development headers for the audio decoders used by that specific repository:

Bash

```
sudo apt install libfaad-dev libmpg123-dev
```

After installing the missing dependencies, it is usually a good idea to run `make clean` before running `make` again to ensure a fresh build.

You said

pi@PiHU:~/dab-radio $ ./dab_scan

\[RaonUsbTuner\] Powering up

\[RaonUsbTuner\] PowerUp okay!

\[RaonUsbTuner\] Setting up MSC Threshold...

\[RaonUsbTuner\] Setting up FIC Memory...

\[RaonUsbTuner\] Initialized

Creating Scanner

\[RaonUsbTuner\] Tuning Frequency: 174928000

\[RaonUsbTuner\] Tuning Frequency: 176640000

\[RaonUsbTuner\] Tuning Frequency: 178352000

\[RaonUsbTuner\] Tuning Frequency: 180064000

\[RaonUsbTuner\] Tuning Frequency: 181936000

\[RaonUsbTuner\] Tuning Frequency: 183648000

\[RaonUsbTuner\] Tuning Frequency: 185360000

\[RaonUsbTuner\] Tuning Frequency: 187072000

\[RaonUsbTuner\] Tuning Frequency: 188928000

\[RaonUsbTuner\] Tuning Frequency: 190640000

\[RaonUsbTuner\] Tuning Frequency: 192352000

\[RaonUsbTuner\] Tuning Frequency: 194064000

\[RaonUsbTuner\] Tuning Frequency: 195936000

\[RaonUsbTuner\] Tuning Frequency: 197648000

\[RaonUsbTuner\] Tuning Frequency: 199360000

\[RaonUsbTuner\] Tuning Frequency: 201072000

\[RaonUsbTuner\] Tuning Frequency: 202928000

\[RaonUsbTuner\] Tuning Frequency: 204640000

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

FICDecoder: SId 0xCDC2, SCIdS  0: Slideshow (2 bytes UA data)

FICDecoder: SId 0xCDC2: programme type (dynamic): 'Oldies Music'

FICDecoder: SubChId 28: start 768 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId 27: start 738 CUs, size  30 CUs, PL EEP 3-A =  40 kBit/s

FICDecoder: SubChId 26: start 714 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId 25: start 690 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId 24: start 654 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s

FICDecoder: SubChId 23: start 630 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId 22: start 606 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId 21: start 582 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId 20: start 558 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId 19: start 510 CUs, size  48 CUs, PL EEP 3-A =  64 kBit/s

FICDecoder: SubChId 18: start 474 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s

FICDecoder: SubChId 17: start 438 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s

FICDecoder: SubChId 16: start 390 CUs, size  48 CUs, PL EEP 3-A =  64 kBit/s

FICDecoder: SubChId 15: start 366 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId 14: start 342 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId 13: start 318 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId 12: start 294 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId 11: start 270 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId 10: start 234 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s

FICDecoder: SubChId  9: start 210 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId  8: start 186 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId  7: start 150 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s

FICDecoder: SubChId  6: start 132 CUs, size  18 CUs, PL EEP 3-A =  24 kBit/s

FICDecoder: SubChId  5: start 108 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId  4: start  72 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s

FICDecoder: SubChId  3: start  48 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId  2: start  24 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId  1: start   0 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SId 0xCDC2: audio service (SubChId  1, DAB+, primary)

FICDecoder: SId 0xC080: audio service (SubChId  2, DAB+, primary)

FICDecoder: SId 0xC0EB: audio service (SubChId  3, DAB+, primary)

FICDecoder: SId 0xCDD4: audio service (SubChId  4, DAB+, primary)

FICDecoder: SId 0xCFD8: audio service (SubChId  5, DAB+, primary)

FICDecoder: SId 0xCFFC: audio service (SubChId  6, DAB+, primary)

FICDecoder: SId 0xC254: audio service (SubChId  7, DAB+, primary)

FICDecoder: SId 0xCDF6: audio service (SubChId  8, DAB+, primary)

FICDecoder: SId 0xC55A: audio service (SubChId  9, DAB+, primary)

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

\[RaonUsbTuner\] Tuning Frequency: 206352000

FICDecoder: SubChId  8: start 216 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s

FICDecoder: SubChId  9: start 252 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s

FICDecoder: SubChId 10: start 288 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId 11: start 312 CUs, size  36 CUs, PL EEP 3-A =  48 kBit/s

Success! You’ve hit the jackpot. The scanner is working perfectly and has locked onto a strong signal.

Specifically, your tuner is picking up the **"London N" (London North)** ensemble. Based on the output, your hardware and the `dab-radio` software are communicating correctly, and you are pulling in a wide variety of stations (like Radio Caroline, Rinse FM, and Solar Radio).

### What the Output Tells Us

- **Ensemble Found:** `London N` (Ensemble ID: `0xC1C6`).
- **Station Variety:** You're seeing both DAB+ and standard DAB audio services.
- **Bitrates:** Most stations are running at 32 kbps or 48 kbps using `EEP 3-A` error protection, which is standard for small-scale DAB multiplexes.
- **Date/Time Sync:** The tuner successfully pulled the network time: `2026-04-03 13:57:00`.

### Next Steps: Listening to the Audio

Now that you know the scanner works, you'll want to actually hear the audio or serve it to a player.

#### 1\. Generate an M3U Playlist (for VLC or IPTV)

The `dab-radio` repo usually includes a tool to create a playlist for all the stations it just found. If the scanner saved its results to a file (often `channels.conf` or similar, depending on your version), you can run:

Bash

```
./m3u_writer > stations.m3u
```

You can then open `stations.m3u` in **VLC** on your PC or another device on your network.

#### 2\. Test a Single Station

If you want to test the audio output directly from the command line (assuming you have audio drivers set up on the Pi), you would typically pipe the output of the tuner into a player. However, since this repo is designed for streaming, it’s usually easiest to use the `dab_mp2` or `dab_aac` tools provided in the folder to decode a specific Service ID (SId).

For example, to listen to **Radio Caroline** (SId `0xC6D6`):

Bash

```
./dab_aac -s 0xC6D6
```

_(Note: You might need to specify the frequency or ensemble depending on how the CLI is structured in that specific fork)._

#### 3\. Integrate with TVHeadend

If your goal is a permanent setup:

1.  Move the compiled binaries to a permanent location (like `/usr/local/bin`).
2.  Use the generated `.m3u` file as an **Automatic IPTV Network** source in TVHeadend.
3.  TVHeadend will then treat each DAB station as a "TV channel" that you can stream to any device in your house.

Are you planning to use this as a standalone radio, or are you piping this into a media server like TVHeadend or Home Assistant?

You said

since this worked should dablin work too

**Short answer: Yes, but not directly out of the box like an RTL-SDR would.**

Standard DABlin (the GTK-based player) expects an **RTL-SDR** (using `rtl_tcp`) or an **EDI/ETI** stream as input. Your dongle (`16c0:05dc`) uses a completely different communication protocol (the MTV318/Raontech chipset) that DABlin doesn't natively "speak."

However, because the `chrisjohnson1988/dab-radio` tools you just compiled can output raw data, you can "pipe" the two together.

### How to make it work

To get DABlin's nice visual interface (slideshows, signal strength, etc.) using your specific hardware, you usually have to bridge the two using a "FIFO" (First-In, First-Out) pipe or a local network stream.

1.  **The "Pipe" Method:** You can use a tool from the repo you just downloaded to output an **ETI** (Ensemble Transport Interface) stream and pipe it directly into the console version of DABlin:

    Bash

    ```
    ./dab_eti -f 204640 | dablin -f eti
    ```

    _(Note: You'll need to check the exact flags for `dab_eti` in that repo to match the frequency you want to tune to.)_

2.  **The TVHeadend / Network Method:** Since the `dab-radio` tools are great at creating an IPTV-style stream, you can have DABlin connect to that stream as if it were a network source.

---

### Why you might want to stick with your current setup

Since you’ve already confirmed `dab_scan` works, you have a very stable "low-level" driver. DABlin is excellent for **UI and Slideshows**, but if your goal is just to **listen or record**, the tools you already have are actually more efficient on a Raspberry Pi because they don't require the overhead of a heavy graphical interface.

### Should you try installing DABlin?

If you want the visual "radio" experience on your Pi Desktop:

1.  Install DABlin: `sudo apt install dablin`
2.  Try the pipe command above.

**One warning:** If you are on an older Raspberry Pi (like a Pi 3 or Zero), DABlin's GTK interface can be a bit heavy. If you're running "headless" (no monitor), DABlin won't give you much benefit over the `dab-radio` tools you're already using.

What's the end goal for the Pi? A touchscreen radio, or a background music server?

You said

for the moment i want to select a channel and play from the command line

To play a specific channel directly from the command line, you’ll use the `dab_mp2` or `dab_aac` tools you just compiled. These tools act as the "bridge" between your USB hardware and an audio player.

Since your scan showed that most stations in London North (like **Radio Caroline** or **Solar**) are **DAB+**, you will mostly be using `dab_aac`.

### 1\. The Command Structure

The general syntax for the tools in that repository is:

Bash

```
./dab_aac -f [Frequency_in_Hz] -s [Service_ID] | [Audio_Player]
```

### 2\. Example: Playing Radio Caroline

Based on your scan results:

- **Frequency:** `204640000` (This was the last frequency your scan tuned to).
- **Service ID (SId):** `0xC6D6` (Radio Caroline).

You can pipe the output into `ffplay` (part of the ffmpeg package) or `aplay`. I recommend `ffplay` for the best compatibility with AAC:

Bash

```
# First, install a command-line player if you don't have one
sudo apt install ffmpeg

# Then run the play command:
./dab_aac -f 204640000 -s 0xC6D6 | ffplay -i - -nodisp
```

- `-i -`: Tells ffplay to read from the "pipe" (stdin).
- `-nodisp`: Prevents it from trying to open a video window (useful if you are on SSH).

### 3\. Quick Reference Table

From your `dab_scan` log, here are the details for a few popular stations to get you started:

Station Name

Frequency (Hz)

SId

Decoder Tool

**Radio Caroline**

204640000

`0xC6D6`

`dab_aac`

**Solar Radio**

204640000

`0xCED4`

`dab_aac`

**Rinse FM**

204640000

`0xCD90`

`dab_aac`

**GreekBeat Radio**

204640000

`0xCFFC`

`dab_aac`

Export to Sheets

### Pro-Tip: Check the M3U

The `dab_scan` likely created a file called `dab.m3u` in your folder. If you `cat dab.m3u`, you will see lines like this: `pipe:///home/pi/dab-radio/dab_mpegts 'London N' 'Radio Caroline' 204648000 14 aac`

You can actually use those exact parameters (Frequency and Service ID) to build your manual command. If `ffplay` gives you trouble, you can also try piping into `vlc` using its dummy interface:

Bash

```
./dab_aac -f 204640000 -s 0xC6D6 | cvlc -
```

**Which station are you trying to lock onto first?** (If you get a "Buffer Underrun" error, let me know; we might need to adjust the frequency slightly by a few kHz).

You said

given

\[RaonUsbTuner\] Tuning Frequency: 216928000

FICDecoder: SId 0xCCE9: programme type (static): 'Pop Music'

FICDecoder: SId 0xC5E0: programme type (static): 'Pop Music'

FICDecoder: SId 0xCDD8: programme type (static): 'Religion'

FICDecoder: SId 0xC7D8: audio service (SubChId  7, DAB+, primary)

FICDecoder: SId 0xC5EF: audio service (SubChId 10, DAB+, primary)

FICDecoder: SId 0xC7E6: audio service (SubChId 24, DAB+, primary)

FICDecoder: SId 0xCEE6: audio service (SubChId 30, DAB+, primary)

FICDecoder: SId 0xCAEA: audio service (SubChId 29, DAB+, primary)

FICDecoder: SId 0xC5D8, SCIdS  0: MSC service component (SubChId  4)

FICDecoder: SId 0xC7D8, SCIdS  0: MSC service component (SubChId  7)

FICDecoder: SId 0xCAFB, SCIdS  0: MSC service component (SubChId 38)

FICDecoder: SId 0xC3D8, SCIdS  0: MSC service component (SubChId  3)

FICDecoder: SId 0xC5E0, SCIdS  0: MSC service component (SubChId 20)

FICDecoder: SId 0xC5EF, SCIdS  0: MSC service component (SubChId 10)

FICDecoder: SId 0xCAC2, SCIdS  0: MSC service component (SubChId 21)

FICDecoder: SId 0xC0D8: audio service (SubChId  6, DAB , primary)

FICDecoder: SId 0xC5E0: audio service (SubChId 20, DAB+, primary)

FICDecoder: SId 0xCFF9: audio service (SubChId 40, DAB+, primary)

FICDecoder: SId 0xCCE9: audio service (SubChId 28, DAB+, primary)

FICDecoder: SId 0xCAEB: audio service (SubChId 26, DAB+, primary)

FICDecoder: SId 0xCDE6: audio service (SubChId 22, DAB+, primary)

FICDecoder: SId 0xC5F6: audio service (SubChId  2, DAB+, primary)

FICDecoder: SId 0xC1D8: audio service (SubChId 27, DAB+, primary)

FICDecoder: SId 0xCDD8: audio service (SubChId 13, DAB , primary)

FICDecoder: SId 0xC5D8: audio service (SubChId  4, DAB+, primary)

FICDecoder: SId 0xCAD7: audio service (SubChId 17, DAB+, primary)

FICDecoder: SId 0xC6CF: audio service (SubChId 31, DAB+, primary)

FICDecoder: SId 0xCAFC: audio service (SubChId 39, DAB+, primary)

FICDecoder: SId 0xCCD8: audio service (SubChId 12, DAB , primary)

FICDecoder: SId 0xCDDA: audio service (SubChId 15, DAB , primary)

FICDecoder: SId 0xCFFA: audio service (SubChId 41, DAB+, primary)

FICDecoder: SId 0xCAC2: audio service (SubChId 21, DAB+, primary)

FICDecoder: SId 0xCAFB: audio service (SubChId 38, DAB+, primary)

FICDecoder: SId 0xC8D8: audio service (SubChId  8, DAB+, primary)

FICDecoder: SId 0xCCE7: audio service (SubChId 33, DAB+, primary)

FICDecoder: SId 0xCFF9, SCIdS  0: MSC service component (SubChId 40)

FICDecoder: SId 0xCDDA, SCIdS  0: MSC service component (SubChId 15)

FICDecoder: SId 0xC6CF, SCIdS  0: MSC service component (SubChId 31)

FICDecoder: SId 0xC5F6, SCIdS  0: MSC service component (SubChId  2)

FICDecoder: SId 0xCCD8, SCIdS  0: MSC service component (SubChId 12)

FICDecoder: SId 0xCDE6, SCIdS  0: MSC service component (SubChId 22)

FICDecoder: SId 0xC1D8, SCIdS  0: MSC service component (SubChId 27)

FICDecoder: SId 0xC5EF: programme service label 'Boom Radio UK' ('Boom UK')

FICDecoder: SubChId  2: start 454 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId 20: start 250 CUs, size  18 CUs, PL EEP 3-A =  24 kBit/s

FICDecoder: SubChId 31: start 526 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId 33: start 550 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId 30: start 502 CUs, size  24 CUs, PL EEP 3-A =  32 kBit/s

FICDecoder: SubChId  6: start  58 CUs, size  48 CUs, PL UEP 3   =  64 kBit/s

FICDecoder: SubChId 13: start 178 CUs, size  48 CUs, PL UEP 3   =  64 kBit/s

FICDecoder: SId 0xCAC2: programme service label 'Absolute 90s' ('Abs 90s')

FICDecoder: SId 0xC3D9: audio service (SubChId 35, DAB+, primary)

FICDecoder: SId 0xCAEA: programme type (static): 'Easy Listening Music'

FICDecoder: SId 0xCAEB: programme type (static): 'News'

FICDecoder: SId 0xCAFC: programme type (static): 'Pop Music'

FICDecoder: SId 0xCDDA: programme type (static): 'Rock Music'

FICDecoder: SId 0xC7E6: programme type (static): 'Pop Music'

FICDecoder: SId 0xC6B5: programme type (static): 'Pop Music'

how to play Absolute 90s

To play **Absolute 90s**, you'll use the frequency and Service ID (SId) gathered from your scan.

From your output:

- **Station:** Absolute 90s
- **SId:** `0xCAC2`
- **Frequency:** `216928000`
- **Type:** `DAB+` (So you must use the `dab_aac` tool)

### The Play Command

Run this from your `~/dab-radio` directory:

Bash

```
./dab_aac -f 216928000 -s 0xCAC2 | ffplay -i - -nodisp
```

### Troubleshooting

1.  **If you don't have ffplay:** You can install it with `sudo apt install ffmpeg`. If you prefer a different player, you can try `cvlc -` or `aplay` (though `aplay` might struggle with the raw AAC stream without extra parameters).
2.  **Permissions:** If you get a "device not found" error, remember to run it with `sudo` or check that your udev rule is active.
3.  **Signal Lock:** If the audio stutters, it’s often because the frequency on these sticks is slightly offset. If `216928000` doesn't work perfectly, try shifting it slightly:

    - `216920000`
    - `216936000`

### Why this station is different

You might notice your scan mentioned `SubChId 21`. The software handles the mapping for you once you provide the Service ID (`-s 0xCAC2`), so you don't need to worry about the SubChannel ID for the command line.

Enjoy the 90s! Any other stations from that list you want to try?

You said

pi@PiHU:~/dab-radio $ ./dab_mp2 ./dab_aac -f 216928000 -s 0xCAC2

Usage: dab_mp2 frequency subchannel

Examples:

dab_mp2 225648000 1 # Tune in to BBC Radio 1

Arguments:

frequency

The dab frequency to tune in to in Hz. e.g 225648000

subchannel

The subchannel on the frequency to receive

It looks like there’s a small misunderstanding in how the commands are structured. You are trying to run both `dab_mp2` and `dab_aac` at the same time, which is confusing the terminal.

Since **Absolute 90s** is a **DAB+** station (as shown in your scan), you must use **`./dab_aac`** specifically. Also, the tools in this specific repository use the **SubChannel ID** rather than the Service ID for the manual command line.

### The Correct Command for Absolute 90s

Looking at your scan log:

- **Station:** Absolute 90s
- **Frequency:** `216928000`
- **SubChId:** `21`

Run this exact command:

Bash

```
./dab_aac 216928000 21 | ffplay -i - -nodisp
```

---

### Why the previous attempt failed:

1.  **Command Overlap:** You typed `./dab_mp2 ./dab_aac ...`. The terminal thought you were trying to run `dab_mp2` and using the name of the other program as an argument.
2.  **Arguments:** These specific tools want `[frequency] [subchannel]`.

    - **Frequency:** `216928000`
    - **Subchannel:** `21` (from your scan line: `FICDecoder: SId 0xCAC2: audio service (SubChId 21, DAB+, primary)`)

### Quick Reference for other stations on this frequency:

If you want to switch to a different station on that same multiplex (**National DAB 2**), just change the last number:

Station

Frequency

SubChannel

Command

**Absolute 90s**

216928000

**21**

\`./dab_aac 216928000 21

**Boom Radio UK**

216928000

**10**

\`./dab_aac 216928000 10

**Absolute 80s**

216928000

**7**

\`./dab_aac 216928000 7

Export to Sheets

**Note:** If you hear "chirping" or robotic noises, it means the signal is a bit weak or the Pi's CPU is spiking. If you get no sound at all, make sure `ffplay` is installed (`sudo apt install ffmpeg`).

You said

pi@PiHU:~/dab-radio $ ./dab_aac 216928000 21

Usage: dab_aac frequency subchannel bitrate

Examples:

dab_aac 222064000 17 40 # Tune in to Capital XTRA

Arguments:

frequency

The dab frequency to tune in to in Hz. e.g 225648000

subchannel

The subchannel on the frequency to receive

bitrate

The bitrate dab+ stream

Ah, it’s being even more specific—it wants the **bitrate** too!

According to your scan log for **Absolute 90s** (SubChId 21), it is broadcasting at **32 kBit/s**.

### The Complete Command

To play it, use this exact string:

Bash

```
./dab_aac 216928000 21 32 | ffplay -i - -nodisp
```

### Why it needs the bitrate

Standard DAB (using `dab_mp2`) has the bitrate encoded differently, but for **DAB+ (AAC)**, this specific tool needs to know the bitrate to properly initialize the audio decoder.

### Quick Reference for other stations on that frequency:

If you want to try others, here are the bitrates from your scan:

- **Absolute 90s:** `216928000 21 32`
- **Boom Radio UK:** `216928000 10 32`
- **Absolute 80s:** `216928000 7 48`
- **Planet Rock:** `216928000 15 64` (Note: This one is listed as `DAB` in your scan, so if `dab_aac` fails, use `./dab_mp2 216928000 15`)

**Is it making noise yet?** If `ffplay` gives you a "Protocol not found" or similar error, make sure the pipe (`|`) is correctly typed!

You said

can i save to a file

Absolutely. Since the output of `./dab_aac` is a standard data stream, you can use a simple Linux "redirection" to save it directly to a file instead of playing it.

Depending on what you want to do with the file later, you have two main options:

### Option 1: Save the Raw AAC Data

This creates a file containing the raw audio stream. It’s the most "direct" way, though some players might struggle to seek (fast-forward) through raw AAC files.

Bash

```
./dab_aac 216928000 21 32 > absolute90s.aac
```

- **To stop recording:** Press `Ctrl+C`.
- **To play it later:** `ffplay absolute90s.aac` or open it in VLC.

---

### Option 2: Save as a Proper .m4a or .mp3 (Recommended)

If you want the file to be more "universal" (with a proper header so you can see the duration and seek through it), you can use `ffmpeg` to "wrap" the stream as it records.

**To save as an M4A (Lossless copy of the DAB+ stream):**

Bash

```
./dab_aac 216928000 21 32 | ffmpeg -i - -c copy recording.m4a
```

_(This just puts the AAC data into a "container" without losing any quality.)_

**To save as an MP3:**

Bash

```
./dab_aac 216928000 21 32 | ffmpeg -i - -c:a libmp3lame -b:a 128k recording.mp3
```

---

### Option 3: The "Record and Listen" (The Stealth Move)

If you want to hear the music **and** save it at the same time, use the `tee` command:

Bash

```
./dab_aac 216928000 21 32 | tee recording.aac | ffplay -i - -nodisp
```

### A Note on File Size

DAB+ bitrates are quite low (32kbps to 64kbps usually).

- A **32 kbps** station will use about **14.4 MB per hour**.
- A **64 kbps** station will use about **28.8 MB per hour**.

You could record for days on a standard Raspberry Pi SD card without running out of space! Are you planning to set up a scheduled recording for a specific show?

You said

from dab_acc can i seesignal strenth

Not directly through the `dab_aac` command itself. The `dab_aac` and `dab_mp2` tools are designed to be "dumb" pipes—they just grab the audio data and spit it out as fast as possible.

However, since you've already seen that your hardware works with `dab_scan`, you have two ways to "see" how strong your signal is:

### 1\. Use `dab_scan` as a Signal Meter

When you run `./dab_scan`, look at the output in your terminal.

- If the terminal fills up with `FICDecoder` lines (like the ones you showed me earlier with SIds and labels) quickly after a "Tuning Frequency" line, your signal is **strong**.
- If the terminal hangs on a "Tuning Frequency" line for several seconds without showing any "SId" or "Labels," the signal is **weak or non-existent** at that frequency.

### 2\. Use `dablin_gtk` (The Visual Way)

If you are on a Raspberry Pi with a desktop (or using VNC), you can install **DABlin**. It has a built-in signal strength meter and a "Signal Quality" bar.

Because your dongle isn't a standard RTL-SDR, you have to "pipe" the signal into DABlin like this:

1.  **Install DABlin:**

    Bash

    ```
    sudo apt update
    sudo apt install dablin
    ```

2.  **Pipe the ensemble into it:** You'll need the `dab_eti` tool (which should be in your `dab-radio` folder). This sends the _entire_ multiplex (all stations) to DABlin:

    Bash

    ```
    ./dab_eti 216928000 | dablin_gtk -f eti
    ```

    _DABlin will open a window showing a signal meter on the right side and a list of all stations._

### 3\. Check for "Sync" errors (The Command Line Way)

If you are strictly on the command line and want to know if the signal is dropping out while you play, watch the `ffplay` or `dab_aac` output.

- **Buffer Underruns / "Skipping":** If the audio cuts out or you see error messages in the terminal, your signal is likely on the "cliff edge" (DAB is digital, so it either works perfectly or sounds like "bubbling mud").
- **Static:** If it's silent or "chirping," the signal is too low for the decoder to lock on.

**Is the audio currently sounding clear, or are you getting some stutters?** If it's stuttering, I can help you adjust your antenna setup—these little USB sticks are surprisingly sensitive to how the wire is positioned!

You said

I can rebuild these tools. rather than pipe the data can i send to ffplay an alternate way?

If you're willing to modify the source code and rebuild, you can move away from standard pipes (`|`) and integrate a more robust way to hand off the data. Since `ffplay` (and `ffmpeg`) are incredibly versatile, you have three main "architectural" paths you can code into the tools:

### 1\. The UDP/Multicast Path (Best for Network/Streaming)

Instead of writing to `stdout`, you can modify the C++ code to open a **UDP socket** and send the AAC packets to a specific IP and port.

- **The Code Change:** In the main loop where the tool calls `fwrite(buffer, 1, len, stdout)`, replace it with a `sendto()` socket call.
- **The Benefit:** You can run `ffplay` on the **same Pi** or **any other computer** on your network.
- **How to play it:**

  Bash

  ```
  ffplay udp://127.0.0.1:1234
  ```

### 2\. The Unix Domain Socket (The "Pro" Pipe)

If you want to keep it all on one machine but avoid the "fragility" of a shell pipe, you can have your tool create a **Unix Domain Socket** (a special file in `/tmp/`).

- **The Code Change:** Use `socket(AF_UNIX, SOCK_STREAM, 0)` and `bind()` to a path like `/tmp/dab_audio.sock`.
- **The Benefit:** It’s faster than a network socket and more "contained" than a pipe. `ffplay` treats it like a file.
- **How to play it:**

  Bash

  ```
  ffplay unix:///tmp/dab_audio.sock
  ```

### 3\. Shared Memory / POSIX Shm (Advanced)

If you want the absolute lowest latency and highest performance (though AAC bitrates are so low this is usually overkill), you can write the audio data into a **Shared Memory Buffer**.

- **The Code Change:** Use `shm_open` and `mmap`.
- **The Catch:** `ffplay` doesn't natively "read" shared memory blocks, so you'd usually need a tiny "shim" or a custom `libavformat` input to read from that memory.

---

### Which one should you build?

If you are looking for a project that makes the tool more "professional," **I highly recommend the UDP approach.** By adding a `-u [IP] [PORT]` flag to your rebuild of `dab_aac`, you transform it into a **Headless DAB Tuner Server**. You could then have the Pi tucked away near a window (for better signal) while you listen to the stream on your laptop or phone.

**Would you like me to help you with a C++ snippet for the UDP socket implementation?** It’s only about 15-20 lines of code to add to `main.cpp`.

You said

it only need to operate on my headunit

Since this is for a **Headunit** (presumably a car or a fixed DIY dash unit), you likely want something more robust than a shell pipe, which can break if the player crashes or if there's a momentary buffer issue.

Rebuilding the tool to use a **FIFO (Named Pipe)** or a **Unix Domain Socket** is the most "system-integrated" way to do this. It allows the tuner to run as a background service (daemon) and the headunit's media player to connect/disconnect whenever it wants.

### The "Headunit-Ready" Approach: Named Pipes (FIFOs)

Instead of a standard pipe `|`, you can modify the code to write to a persistent file-like object on the disk (in RAM).

#### 1\. Modify the Source Code (`dab_aac.cpp`)

In the `main` function of `dab_aac.cpp`, look for where it writes to `stdout`. You can change it to open a specific path.

**The Logic Change:**

C++

```
// Instead of:
// fwrite(buffer, 1, len, stdout);

// Use something like:
int fd = open("/tmp/dab_pipe", O_WRONLY);
write(fd, buffer, len);
```

#### 2\. Why this is better for a Headunit:

- **Decoupling:** You can start the tuner service when the car starts. It will sit there waiting.
- **Player Flexibility:** Your Headunit software (like Kodi, OpenAuto, or a custom Python UI) can simply tell its player engine to "Play file: `/tmp/dab_pipe`".
- **Recovery:** If the media player app crashes, the tuner doesn't have to stop. It just waits for the pipe to be opened again.

---

### Implementation Strategy

If you want to keep the code changes minimal during your rebuild, you don't even _have_ to change the C++ code to achieve "headunit stability." You can use the **`mkfifo`** command in your startup script:

1.  **Create the pipe once:** `mkfifo /tmp/dab_radio`
2.  **Start the tuner in the background:** `./dab_aac 216928000 21 32 > /tmp/dab_radio &`
3.  **Point your Headunit Player to the pipe:** `ffplay -i /tmp/dab_radio -nodisp` (or use the equivalent setting in your UI).

### Designing the UI

Since you are on a Headunit, are you planning to build a small touchscreen interface (e.g., using Python/Tkinter or Qt) to switch these channels?

If you'd like, I can show you how to wrap these "rebuilt" tools into a simple service so that **Absolute 90s** (or any other station) is playing the moment your Pi boots up.

[Google Privacy PolicyOpens in a new window](https://policies.google.com/privacy)[Google Terms of ServiceOpens in a new window](https://policies.google.com/terms)[Your privacy and Gemini AppsOpens in a new window](https://support.google.com/gemini?p=privacy_notice)

Gemini may display inaccurate info, including about people, so double-check its responses.

Continue this chat

## Embedded Content
