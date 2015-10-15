#!/usr/bin/env python

#
# Volumio Metadata Display
# v0.1     24.08.15     Baloothebear4
#
# Module : formatscreens -
# Purpose: Routines to setup and structure screens for display, display independant
#          Abstracts screens available and provides control logic
#
##
# Ported from:
# https://github.com/adafruit/Adafruit_Python_SSD1306/blob/master/examples/shapes.py

from oled.device import sh1106
from oled.render import canvas
from PIL import ImageFont

font = ImageFont.load_default()
device = sh1106(port=1, address=0x3C)
SCREEN_HEIGHT  = 64
SCREEN_WIDTH   = 128
CONTROLS_WIDTH = 35
FONTSCALER     = 2


def horz_centre( words, font_size ):
    # work out the x offset to centre a word for a given font size
    # assume arial 8 lowercase char = 8 pixels
    return( 64-( fontsize/FONTSCALER * len(words)/2)  )


with canvas(device) as draw:
    # Draw some shapes.
    # First define some constants to allow easy resizing of shapes.
    padding = 5
    top = padding
    bottom = device.height - padding - 1
# Draw a rectangle of the same size of screen
    draw.rectangle( (0, 0, device.width-1, device.height-1), outline=255, fill=0)

    # Move left to right keeping track of the current x position for drawing shapes.
    x = padding
    y = 4 * top
    # Draw an left song status.
    inner = 5
    draw.pieslice( (x, y, x+CONTROLS_WIDTH, y+CONTROLS_WIDTH), 0, 270, outline=255, fill=255)
    #draw.pieslice( (x-inner, y-inner, x+CONTROLS_WIDTH-inner, y+CONTROLS_WIDTH-inner), 0, 270, outline=255, fill=255)

    x = padding + 80

    # Draw right volume status
    #for vol in range(0,360):
    vol = 80
    draw.pieslice( (x, y, x+CONTROLS_WIDTH, y+CONTROLS_WIDTH), 270, 270+360*vol/100, outline=255, fill=255)

    fontsize = 11
    font = ImageFont.truetype('fonts/arial.ttf', fontsize)

    a = 'Artist'
    s = 'Song Title'
    b = 'Album'
    m = '1400kbps'
    p = '>'

    draw.text( (horz_centre( s, fontsize), top),  s,  font=font, fill=255)
    draw.text( (horz_centre( a, fontsize), top+10),  a,  font=font, fill=255)
    draw.text( (horz_centre( m, fontsize), bottom-10),  m,  font=font, fill=255)
    draw.text( (horz_centre( p, fontsize), SCREEN_HEIGHT/2),  p,  font=font, fill=255)
