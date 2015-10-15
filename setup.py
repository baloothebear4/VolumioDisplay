#!/usr/bin python

from distutils.core import setup,Extension
setup(
    name = "VolumioDisplay",
    version = "0.1.0",
    author = "Baloothebear4",
    author_email = "Baloothebear4@gmail.com",
    description = ("Companion to Volumio RPi music player: collects metadata from MPD & Shairport metadata for display on a range of screens and display types"),
    license = "GNU",
    keywords = "raspberry pi rpi volumio shairport oled",
    url = "https://github.com/baloothebear4/VolumioDisplay",
    packages=['volumiodisplay'],
    package_data={'volumiodisplay': ['fonts/*.*']},
)
