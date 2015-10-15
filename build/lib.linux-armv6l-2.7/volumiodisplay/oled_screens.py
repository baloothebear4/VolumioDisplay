#!/usr/bin/env python
#
# Volumio Display Project
#
# v0.1	   20.08.15		Baloothebear4 -- port to OLED Display
#
# Module :  screens.py     -- sh1106 128x64 OLED I2C display
# Purpose:  Class to manage all the screen formating and display interactions
#           Does the real work to
#
# based from:
# https://github.com/rm-hull/ssd1306/blob/master/examples/demo.py

from oled.device import sh1106
from oled.render import canvas
from PIL import ImageFont
from getmetadata import Metadata
from system import SystemStatus
import RPi.GPIO as GPIO
import time


DEFAULT_SCREEN = 'bitrate'

DISPLAY_TYPE    = 'sh1106 OLED 128x64 I2C'
RST_PIN         = 4

SCREEN_AVAILABILITY = {
	'bitrate'       : '"Display of music quality type parameters to see the fidelity of the source material eg bitrate & sample rate"',
	'tracks'		: '"Display artist, song & album info plus time elaped and track duration"',
	'volumio'		: '"Graphical display like volumio webUI, plus bitrate, track and artist details"',
	'screensaver'	: '"Display a screen saver when nothing else is happening"',
	'system'		: '"Technical items like CPU usage, mem status, IP etc"',
	'coverart' 		: '"not available"',	# NOT AVAILABLE display of coverart
	'visualiser'  	: '"not available"'	# NOT AVAILABLE spectrum analyser display
	}

SCREEN_SHORTCUTS = {					 # define the user shortcut options to select screens
	'bitrate'       : 'bit',
	'tracks'		: 'trk',
	'volumio'		: 'vol',
	'screensaver'	: 'scr',
	'system'		: 'sys',
	'coverart' 		: 'art',
	'visualiser'  	: 'vis'
	}

START_UP_MESSAGE  = 'Welcome to'
TITLE1			  = 'Volumio'
TITLE2			  = 'Display'
SHUTDOWN_MESSAGE  = ''

SCREEN_HEIGHT  = 64
SCREEN_WIDTH   = 128
CONTROLS_WIDTH = 35

BASE_FONT      = 'fonts/arial.ttf'
VD_FONT		   = 'fonts/lucon.ttf'
VD_FONTSIZE    = 24
STD_FONTSIZE   = 12
PIXELSPERCHAR  = 5     # assume this is for 10pt
FONTSCALER     = 10

class Screens:
# Single place to deal with all screens supported on this device
# To add more screens, change this class, add the screen class
	def __init__( self ):

		self.sys         = SystemStatus()
		self.metadata 	 = Metadata(self.sys)
		self.font   	 = ImageFont.truetype( BASE_FONT, STD_FONTSIZE )
		self.bigger_font = ImageFont.truetype( BASE_FONT, 22 )
		self.status_font = ImageFont.truetype( BASE_FONT, 18 )
		self.vd_font 	 = ImageFont.truetype( VD_FONT, VD_FONTSIZE )
		self.active_screen = DEFAULT_SCREEN  # display this if nothing else
		self.screensaver_position = (0,0)

		#time.sleep(10)    #Make sure the dependent systems are running at startup

		try:
			GPIO.setwarnings(False)
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(RST_PIN,GPIO.OUT)
			GPIO.output(RST_PIN,True)
			GPIO.output(RST_PIN,False)
			GPIO.output(RST_PIN,True)
			self.device = sh1106(port=1, address=0x3C)

		except Exception, e:
			print "Failed to initialise Screens class : %s " % (str(e))
			raise

	def availability( self ):
		return( SCREEN_AVAILABILITY )

	def shortcuts( self ):
		return( SCREEN_SHORTCUTS )

	def default_screen( self ):
		return( DEFAULT_SCREEN )

	def display_type( self ):
		return( DISPLAY_TYPE )

	def update( self, screen ):    # say which screen to update
								   # return whether the system is playing or idle
	 	try:
			if self.metadata.is_airplay_active() and (
				screen == 'bitrate' or
				screen == 'tracks' or
				screen == 'volumio'):
				self.airplayscreen()

			elif  screen == 'bitrate':
				self.bitratescreen()
			elif screen == 'tracks':
				self.tracksscreen()
			elif screen == 'init':
				self.initscreen()
			elif screen == 'exit':
				self.exitscreen()
			elif screen == 'screensaver':
				self.screensaver()
			elif screen == 'volumio':
				self.volumioscreen()
			elif screen == 'system':
				self.systemscreen()
			else:
				print screen + ' not available'
		except Exception, e:
			print "Failed to update screen %s : %s " % (screen, str(e))
			raise

		#print self.metadata
		return( self.metadata.is_idle() )

	def initscreen( self ):
		self.splashpage( START_UP_MESSAGE )

	def exitscreen( self ):
		self.splashpage( SHUTDOWN_MESSAGE )

	def splashpage( self, text ):
		try:
			with canvas( self.device ) as draw:
				draw.text( (horz_centre( text, STD_FONTSIZE), 0), text,  font=self.font, fill=255)
				draw.text( (horz_centre( TITLE1, VD_FONTSIZE)-10, 13), TITLE1,  font=self.vd_font, fill=255)
				draw.text( (horz_centre( TITLE2, VD_FONTSIZE)-10, 38), TITLE2,  font=self.vd_font, fill=255)
		except Exception, e:
			print "Failed to display splashscreen : %s " % (str(e))

	def bitratescreen( self ):
		# update the screen according to the mode defined
		self.metadata.grab()
		#print self.metadata
		bigger_font = ImageFont.truetype( BASE_FONT, 22 )
		status_font = ImageFont.truetype( BASE_FONT, 18 )

		with canvas( self.device ) as draw:
			draw.text((20,20),    self.metadata.bitrate,  font=self.bigger_font, fill=255)
			draw.text((77,0),    self.metadata.samplerate,  font=self.font, fill=255)
			draw.text((0,0),    self.metadata.bitsize,  font=self.font, fill=255)
			draw.text((50,52),    'Volume '+ self.metadata.volume,  font=self.font, fill=255)
			draw.text((3,45),    playicon( self.metadata.state ),  font=self.status_font, fill=255)

	def tracksscreen( self ):
		self.metadata.grab()
		#print self.metadata
		with canvas( self.device ) as draw:
			draw.text((0,0),    self.metadata.song,  font=self.font, fill=255)
			draw.text((0,15),    self.metadata.artist,  font=self.font, fill=255)
			draw.text((0,30),    self.metadata.album,  font=self.font, fill=255)
			#draw.text((0,50),    self.metadata.genre,  font=self.font, fill=255)
			time = secs_to_mins(self.metadata.elapsed) + " / " + secs_to_mins(self.metadata.duration)
			draw.text((0,52),    time,  font=self.font, fill=255)
			draw.text((66,50),    playicon( self.metadata.state ),  font=self.font, fill=255)
			draw.text((78,52),    'Vol '+self.metadata.volume,  font=self.font, fill=255)

	def screensaver( self ):
		self.metadata.grab()     # check whats going on
		#print 'screensave'
		#with canvas( self.device ) as draw:
		#	draw.text( self.screensaver_position,   'bored...',  font=self.font, fill=255)
		self.splashpage( '' )

	def volumioscreen( self ):
		self.metadata.grab()

		with canvas( self.device ) as draw:
			padding = 5
			top = 2
			bottom = self.device.height - padding - 1
			fontsize = 11
			font = ImageFont.truetype( BASE_FONT, fontsize)
			sfont = ImageFont.truetype( BASE_FONT, 8)

			draw.rectangle( (0, 0, self.device.width-1, self.device.height-1) , fill=0, outline=255)

			# draw the left Song duration counter
			song_duration = 3 * 60  # until it can be found assume songs are 3 mins
			song_time = self.metadata.elapsedpc
			#print song_time
			y = 5+ (4 * padding)
			x = padding
			draw.pieslice( (x, y, x+CONTROLS_WIDTH, y+CONTROLS_WIDTH), 270, int(270+360*song_time), outline=0, fill=255)
			i = 7
			draw.ellipse( (x+i, y+i, x+CONTROLS_WIDTH-i, y+CONTROLS_WIDTH-i), outline=0, fill=0)
			t = 6
			draw.text( (x+i+t-4, y+i+t), 'Time',  font=sfont, fill=255)

			# Draw right volume status
			x = 90
			vol = self.metadata.vol
			draw.pieslice( (x, y, x+CONTROLS_WIDTH, y+CONTROLS_WIDTH), 135, int(135+(270*vol/100)), outline=0, fill=255)
			i = 7
			draw.ellipse( (x+i, y+i, x+CONTROLS_WIDTH-i, y+CONTROLS_WIDTH-i), outline=0, fill=0)
			t = 6
			draw.text( (x+i+t, y+i+t), 'Vol',  font=sfont, fill=255)

			# Draw the Text info
			fontsize = 11
			font = ImageFont.truetype( BASE_FONT, fontsize)

			a = self.metadata.artist
			s = self.metadata.song
			m = self.metadata.bitrate
			p = playicon( self.metadata.state )

			draw.text( (horz_centre( s, fontsize, padding), top),  s,  font=font, fill=255)
			draw.text( (horz_centre( a, fontsize, padding), top+10),  a,  font=font, fill=255)
			draw.text( (horz_centre( m, fontsize, padding), bottom-10),  m,  font=font, fill=255)
			draw.text( (horz_centre( p, fontsize, padding), SCREEN_HEIGHT/2),  p,  font=font, fill=255)

	def airplayscreen( self ):
		self.metadata.grab()

		with canvas( self.device ) as draw:
			padding = 5
			top = 2
			bottom = self.device.height - padding - 1
			fontsize = 11
			font = ImageFont.truetype( BASE_FONT, fontsize)
			sfont = ImageFont.truetype( BASE_FONT, 8)
			# outside box
			B = self.device.height-15
			draw.rectangle( (0, 0, self.device.width-1, B) , fill=0, outline=255)
			#airplay triange
			W = 30
			H = 20
			Xt= (self.device.width/2)-W/2
			Y_OFF = -3
			Yt= B+Y_OFF
			draw.polygon( (Xt,Yt+H, Xt+W/2, Yt, Xt+W, Yt+H), fill=255, outline=255)

			#Add Volume and Track data


			# Draw the Text info
			fontsize = 11
			font = ImageFont.truetype( BASE_FONT, fontsize)

			a = self.metadata.artist
			s = self.metadata.song
			m = self.metadata.album

			top = 2

			draw.text( (horz_centre( s, fontsize, padding), top),  s,  font=font, fill=255)
			draw.text( (horz_centre( a, fontsize, padding), top+12),  a,  font=font, fill=255)
			draw.text( (horz_centre( m, fontsize, padding), top+25),  m,  font=font, fill=255)
			draw.text((78,52),    'Vol '+self.metadata.volume,  font=font, fill=255)

	def systemscreen( self ):
		self.sys.grab()

		with canvas( self.device ) as draw:
			sfont = ImageFont.truetype( BASE_FONT, 9)
			self.bar_meter( draw, 0, 5, int(self.sys.status['cpu_load']), "CPU", sfont)
			self.bar_meter( draw, 0, 20, int(self.sys.status['mpd_load']), "MPD", sfont)
			self.bar_meter( draw, 0, 35, int(self.sys.status['shairport_load']), "Shair", sfont)
			self.bar_meter( draw, 0, 50, int(self.sys.status['disk_used']), "Disk", sfont)

	def bar_meter(self, pen, x, y, valuepc, title, font):
		OFFSET = 30
		WIDTH  = 70
		HEIGHT = 8
		pen.rectangle( (x+OFFSET, y, x+WIDTH+OFFSET, y+HEIGHT) , fill=0, outline=255)
		pen.rectangle( (x+OFFSET, y, OFFSET+(valuepc*(x+WIDTH)/100), y+HEIGHT) , fill=255, outline=255)
		pen.text( (x,y), title,  font=font, fill=255)

	def needle_meter(self, pen, x, y, valuepc, title):
		# draw.pieslice( (x, y, x+CONTROLS_WIDTH, y+CONTROLS_WIDTH), 270, int(270+360*song_time), outline=255, fill=255)
		# i = 7
		# draw.ellipse( (x+i, y+i, x+CONTROLS_WIDTH-i, y+CONTROLS_WIDTH-i), outline=255, fill=0)
		# t = 6
		# draw.text( (x+i+t-4, y+i+t), 'Time',  font=sfont, fill=255)
		pass

# other Screen ideas include:
#   visualiser
#   a blend with other data like clock
#

def horz_centre( text, font_size,min=0 ):
# work out the x offset to centre a word for a given font size
	c = (SCREEN_WIDTH/2)-( float(font_size/FONTSCALER) * (float(PIXELSPERCHAR * len(text))/2) )
	#c = (SCREEN_WIDTH/2)-( draw.textsize(text, font_size)/2 ) --- use draw.textsize() to improve this
	if c<min: c=min

	return( int(c ) )

def playicon( play_state ):
# needs to be updated to either return a bitmap icon or text
	if   play_state == 'play':
		return ( '>' )
	elif play_state == 'stop':
		return ( '[]' )
	elif play_state == 'pause':
		return ( '||' )
	elif play_state == 'airplay':
		return ( 'AP' )
	else:
		return ( '??' )

def secs_to_mins( seconds ):    # convert time from MPD as a string in seconds to a mins:secs formating
	mins = int( float(seconds) )/60
	timeformat = "%2d:%02d" % (mins, (float(seconds) - mins * 60) )
	return timeformat
