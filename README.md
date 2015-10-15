
# Project developing LCD, OLED &amp; TFT display functionality for Volumio

 The SRC Volumio Display project is a collection of python and C code
 to develop display interfaces to Volumio - the cool MPD/Shairport HiFi Music
 distro.

 The intention is to create a base set of classes that can be used to construct
 a range of user interfaces to Volumio for standalone Media Centre type uses.
 For example a Raspberry Pi enclosed on a box with an inexpensive OLED display,
 PSU serves a DLNA renderder/Airplay client when connected to a HiFi DAC and
 power amp.  The display provides a real time indication of track playing,
 bitrate, sample rate, volume level, even the album art.

 I envisage a number of implementations such as:
  - 2x16 LCD displays using LCDproc (eg based on mpdlcd py library or GPIO)
  - 128x64 1.3" OLED displays using SH1106 or sh1306 chipsets (py GPIO), I2C
  - 320x480 2.8"+ TFT displays, SPI based
.

Rather than use a config file to configure, I would prefer to write python
classes which will be much more flexible and more easily extensible.  In
particular to allow rotary controllers, IR remotes etc to be added.

The base classes are developed in python to build on a number of examples
but with the intention to take this further and bring together a disparate set of implementations and experiences.

MPD and Shairport, the underlying music player applications are well proven
and stable.  This project intends to add wrappers to collect the metadata
(ie info about what is playing and how it is playing) a publish this to a range of display drivers.

The implementation builds on Volumio 1.55, based on Debian 3.18 and is written in python, C & ssh scripts.
