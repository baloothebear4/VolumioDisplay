import os, re
import sys, time

AIRPLAY_FILE = "/etc/shairport_metadata/now_playing"
AIRPLAY_DEFAULT = {
	'artist'	: '',
	'album' 	: '',
	'comment' 	: '',
	'title' 	: '',
	'artwork' 	: '',
	'genre'		: ''
	}
class Airplay:

	def __init__(self, file):
		self.file       = file
		self.metadata   = AIRPLAY_DEFAULT
		self.block      = ''

	def __repr__(self):
		printout = ''
		for k,v in self.metadata.items():
				printout += '%12s : %s\n' % (k,v)
		return printout

	def read_pipe(self):
	# Look for a block, keep reading if one is found
		new_block = False
		CHUNK_SIZE = 2000
		self.block = ''
		try:
			# This works but blocks
			# fifo = open(self.file, 'r') #os.O_RDONLY | os.O_NONBLOCK )
			# while True:
			# 	line = fifo.readline()[:-1]
			# 	print 'Parent %d got "%s" at %s' % (os.getpid(), line, time.time( ))
	#		while self.block.find('comment=') == -1 and self.block.find('artist=') != -1:

			fifo = os.open(self.file, os.O_RDONLY)#  | os.O_NONBLOCK )
			chunk = os.read(fifo, CHUNK_SIZE)    # Read it in in chunks
			self.block += chunk
			#new_block = self.block.find('comment=') != -1 and self.block.find('artist=') != -1
			#new_block = chunk > 0
			print "chunk len %d:chunk >%s<" % (len(chunk), chunk)
			os.close(fifo)
			if new_block:
				print "Block received : \n>>>>%s<<<<\nchunk %s" % (self.block, chunk)
		except Exception, e:
			if e.errno == 11:    #legitimate end of pipe
				print "Err 11: end of pipe found"
				new_block = len(self.block) > 0
			else:
				print "Fault reading airplay pipe: "+ str(e)
				new_block = False

		return new_block

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

ap = Airplay(AIRPLAY_FILE)

while True:
	print "Check pipe"
	new_track = ap.grab_metadata()
	if new_track:
		print ap

	print "Sleep"
	time.sleep(3)
	print "Awake"
# Once all the keys have been received the metadata is received
