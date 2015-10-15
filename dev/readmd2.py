import os
import sys, time

from multiprocessing import Process, Pipe

AIRPLAY_FILE = "/etc/shairport_metadata/now_playing"
AIRPLAY_DEFAULT = {
	'artist'	: '',
	'album' 	: '',
	'comment' 	: '',
	'title' 	: '',
	'artwork' 	: '',
	'genre'		: ''
	}

def read_shairport_pipe(file, pipe):
# Look for a block, keep reading if one is found
	line      = ''

	try:
		# This works but blocks
		fifo = open(file, 'r')    #os.O_RDONLY | os.O_NONBLOCK )
		while True:
			line += fifo.readline()[:-1]
			print 'Pipe reader read >>%s<<\n' % (line)

			if line.find('comment=') != -1 and line.find('artist=') != -1:
				print "Block in pipe len %d:chunk >%s<" % (len(line), line)
				pipe.send(line)
				line = ''

	except Exception, e:
		print "Fault reading airplay pipe: "+ str(e)
		raise


class Airplay():
	def __init__(self, file):
		self.metadata   = AIRPLAY_DEFAULT
		self.block      = ''
		self.out_pipe, self.in_pipe = Pipe()

		p = Process(target=read_shairport_pipe, args=(file, self.in_pipe,))
		p.start()

	def __repr__(self):
		printout = "metadata:\n"+self.metadata
		# for k,v in self.metadata.items():
		# 		printout += '%12s : %s\n' % (k,v)
		return printout


	def grab(self):
		if self.out_pipe.poll(0):
			s = True
			self.metadata = self.out_pipe.recv()   # prints "[42, None, 'hello']"
		else:
			print "nothing in pipe"
			s = False

		return s


ap = Airplay(AIRPLAY_FILE)

while True:
	print "Check queue"
	new_track = ap.grab()
	if new_track:
		print ap

	print "Sleep"
	time.sleep(3)
	print "Awake"
# Once all the keys have been received the metadata is received
