#!/usr/bin/env python
#
# Volumio Display Project
#
# v0.1	   20.08.15		Baloothebear4
#
# Module : getmetadata.py
# Purpose: Routines to manage the interface to MPD and shairport capturing the metadata for
#          subsequent formatting and display (not done here)
#
##

import math, re, os, sys                        #format the numerics appropriately
from mpd import MPDClient
from system import SystemStatus
from multiprocessing import Process, Pipe

AIRPLAY_FILE = "/etc/shairport_metadata/now_playing"
AIRPLAY_DEFAULT = {
	'artist'    : '',
	'album' 	: '',
	'comment' 	: '',
	'title' 	: '',
	'artwork' 	: '',
	'genre'		: ''
	}

PLAY_STATES = (
	'stop',
	'play',
	'pause',
	'airplay'
	)

class Metadata:                    # collect and manage the metadata

	def clear( self ):
		self.state = 'stop'
		self.volume = ''
		self.song = ''
		self.artist = ''
		self.bitrate = ''
		self.samplerate = ''
		self.bitsize = ''
		self.album = ''
		self.genre = ''
		self.file = ''
		self.duration = '0'
		self.time = ['', '']     # integer elapsed & duration
		self.elapsed = '0.0'
		self.elapsedpc = 0
		self.vol = 0.0

	def __init__( self, sys ):
		self.clear()
		try:
			self.client  = MPDClient()   # connect to the MPD server
			self.airplay = Airplay()
			self.sys     = sys

		except Exception, e:
			print "Metadata initialisation error "+ str(e)

	def __repr__( self ):
		text  = "Volume %s\n" % self.volume
		text += "Song %s\n" % self.song
		text += "Artist %s\n" % self.artist
		text += "Bitrate %s\n" % self.bitrate
		text += "Sample rate %s\n" % self.samplerate
		text += "Bitsize %s\n" % self.bitsize
		text += "Album %s\n" % self.album
		text += "Genre %s\n" % self.genre
		text += "File %s\n" % self.file
		text += "State %s\n" % self.state
		text += "Elapsed %s\n" % self.elapsed
		text += "Duration %s\n" % self.duration
		text += "Elapsed %3f\n" % self.elapsedpc
		return ( text )

	def grab( self ):
		# First of all work out if where to get the data from
		if self.is_airplay():
			self.grab_Airplay()
		else:
			self.grab_MPD()

	def grab_MPD_song( self ):  # sometimes Minim server fails to get the track right
		try:
			currentsong = self.client.currentsong()
			#print currentsong
			self.song = currentsong[ 'title' ]
			self.artist = currentsong[ 'artist' ]
			self.album = currentsong[ 'album' ]


			#self.genre = currentsong[ 'genre' ]
			self.file = currentsong[ 'file']
		except:
			self.file = currentsong[ 'file']
			if not self.file_to_metadata():
				self.artist = 'Artist unknown'
				self.song   = 'Song unknown'
				self.album  = 'Album unknown'

	def grab_MPD( self ):

		try:
			self.client.timeout = 10                # network timeout in seconds (floats allowed), default: None
			self.client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
			self.client.connect("localhost", 6600)  # connect to localhost:6600
			mpd_status  = self.client.status()      # either use the MPD status call or a string

			if mpd_status[ 'single'] == '1':
				print 'playing through playlist'
				self.client.single( 0 )             # ie keep going through the playlist

			#print mpd_status
			self.state = mpd_status[ 'state' ]

			if not mpd_status[ 'state' ]=='stop' and 'audio' in mpd_status:
				self.state = mpd_status[ 'state' ]
				audio = mpd_status[ 'audio' ].split(":")
				self.grab_MPD_song()

				self.bitrate = '%4.0fkbps' %float( mpd_status[ 'bitrate' ] )
				self.bitsize = '%2.0fbits' % float( audio[ 1 ] )
				self.samplerate = '%5.1fkHz' % ( float ( audio[ 0 ] ) /1000 )
				self.vol = float( mpd_status[ 'volume' ])
				self.volume = '%3.0f%%' % self.vol
				self.elapsed = mpd_status[ 'elapsed' ]
				self.time = mpd_status[ 'time' ].split(':')
				self.duration = str(self.time[1])
				self.elapsedpc = float(self.time[0]) / float(self.time[1])
				#print "Duration %s Time %s + %s & elapsed %f\n" % (self.duration, self.time[0], self.time[1], self.elapsedpc)

			else:
				self.clear()
				self.vol = float( mpd_status[ 'volume' ])
				self.volume = '%3.0f%%' % self.vol

			self.client.close()                     # send the close command
			self.client.disconnect()                # disconnect from the server

		except Exception, e:
			print "MPD access failure: "+ str(e)
			self.state = "fail"

	def is_airplay( self ):			# remember Airplay will override MPD if active
		return self.state == 'airplay'

	def is_airplay_active( self ):			# remember Airplay will override MPD if active
		if self.sys.shairport_active():
			self.state = 'airplay'
			return True
		else:
			self.state = 'stop'
			return False

	def grab_Airplay( self ):
		#need to read the volume
		if self.airplay.grab_metadata():
			self.artist = self.airplay.metadata['artist']
			self.song   = self.airplay.metadata['title']
			self.album  = self.airplay.metadata['album']
			self.bitrate = ''
			self.samplerate = '44.1kHz'
			self.bitsize = '16 bits'
			self.elapsedpc = 0

	def is_idle( self ):					# work out if the player is playing out or idle
		idle = (self.state == 'stop' or self.state == 'pause')
		return idle

	def file_to_metadata(self):

	    sections = file_to_text(self.file).split('/')
	    if len(sections)>3:
	        self.song = sections[len(sections)-1].split('.')[0]
	        self.artist = sections[len(sections)-3]
	        self.album = sections[len(sections)-2]
	        #print "Song :%s\nArtist : %s\nAlbum:%s\n" % (self.song, self.artist, self.album)
	        return True
	    else:
	        return False


class Airplay:

	def __init__(self):
		self.file       = AIRPLAY_FILE
		self.metadata   = AIRPLAY_DEFAULT
		self.block      = ''
		self.out_pipe, self.in_pipe = Pipe()
		p = Process(target=read_shairport_pipe, args=(self.file, self.in_pipe,))
		p.start()

	def __repr__(self):
		printout = ''
		for k,v in self.metadata.items():
				printout += '%12s : %s\n' % (k,v)
		return printout

	def read_pipe(self):
		if self.out_pipe.poll(0):
			s = True
			self.block = self.out_pipe.recv()   # prints "[42, None, 'hello']"
			#print "received block >>%s<<" % self.block
		else:
			#print "nothing in pipe"
			s = False

		return s

	def grab_metadata(self):
	# assume a full message is received
		new_track = self.read_pipe()
		if new_track:
			#clean up the block then parse it, dump all previous tracks leaving just the last
			self.block = self.block.strip()
			art = self.block.rfind('artist')
			if art > 0:    # ie more than one block in pipe
				self.block = self.block[art:]
			#print "clean block "+self.block
			self.metadata = dict(x.split('=') for x in self.block.split('\n'))

		return new_track

def hexchar(s):
    hex = '0x'+s.replace('*','')
    return chr(int(hex,16))

def file_to_text(s):
    p=re.compile('\*\d\d')
    found = p.search(s)
    f = s
    while found:
        f = p.sub(hexchar(p.search(s).group()),f,1)
        found = p.search(f)
    return f

def read_shairport_pipe(file, pipe):
# Look for a block, keep reading if one is found
	line      = ''
	try:
		# This works but blocks
		fifo = open(file, 'r')    #os.O_RDONLY | os.O_NONBLOCK )
		while True:
			line += fifo.readline() #[:-1]
			#print 'Pipe reader read >>%s<<\n' % (line)

			if line.find('comment=') != -1 and line.find('artist=') != -1:
				#print "Block in pipe len %d:chunk >%s<" % (len(line), line)
				pipe.send(line)
				line = ''

	except Exception, e:
		print "Fault reading shairport pipe: "+ str(e)
		raise
