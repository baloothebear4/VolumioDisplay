#
#  Title :  System.py
#  Purpose: Class definition part of VolumioDisplay to capture system status info for display
#  Author :  baloothebear4    23/09/15
#  Usage :  3 functions to capture and format strings with

import psutil, time


SYS_DEFAULT = {
		'cpu_load' 	 	 : '',
		'mpd_load'       : '',
		'shairport_load' : '',
		'disk_used'      : '',
		'mem_used'       : '',
		'ethernet_status': '',
		'wifi_status'    : '',
		'ip_address'     : '',
		'wlan_strength'  : '' }
FIFO_LENGTH = 10

LOAD_FIFO = ('cpu', 'mpd', 'shp')

class SystemStatus:

	def __init__(self):
		self.status = SYS_DEFAULT
		self.cpu_fifo = []
		self.mpd_fifo = []
		self.shp_fifo = []
		# for f in range (FIFO_LENGTH):
		# 	self.fifo.append(0.0)


	#Find Volumio thread PID
		try:
			self.pid_names = {}
			self.shairport_pid = 0

			self.get_PIDs()

		except Exception, e:
			print "Failed to initiatialise system parameters: %s" % str(e)


		#print self.pid_names
		#print "\n MPD PID = "+str(self.mpd_pid)
	def get_PIDs(self):
		for p in psutil.process_iter():
			self.pid_names[p.pid] = p.name()
		self.mpd_pid 	   = self.pid_names.keys()[ self.pid_names.values().index('mpd')]
		self.shairport_pid = self.pid_names.keys()[ self.pid_names.values().index('shairport')]

	def __repr__(self):
		printout = ''
		for k,v in self.status.items():
				printout += '%18s : %s\n' % (k,v)
		return printout

	def grab(self):
		success = True

	#CPU load
		try:
			if self.shairport_pid == 0:
				self.get_PIDs()

			self.status['cpu_load'] = self.smooth( self.cpu_fifo, psutil.cpu_percent(interval = 0.1))
			self.cpu_fifo = self.cpu_fifo[-FIFO_LENGTH:]

			load = psutil.Process(self.mpd_pid)
			self.status['mpd_load'] = self.smooth( self.mpd_fifo, load.cpu_percent(interval = 0.1))
			self.mpd_fifo = self.mpd_fifo[-FIFO_LENGTH:]

			load = psutil.Process(self.shairport_pid)
			self.status['shairport_load'] = self.smooth( self.shp_fifo, load.cpu_percent(interval = 0.1))
			self.shp_fifo = self.shp_fifo[-FIFO_LENGTH:]

	#Disk & Memory
			self.status['mem_used'] = psutil.virtual_memory().percent
			self.status['disk_used']= psutil.disk_usage('/').percent

	#Network parameters
			# net = psutil.net_connections(kind='inet')
			# for c in net:
			# 	print "%s:%s" % (c.laddr)
			# addr = psutil.net_if_addrs()
			# print addr
			#self.status['
			# iwconfig wlan0 | grep -i --color quality
			# ifconfig

		except Exception, e:
			print "Failed to get system status %s" % (str(e))
			self.status['disk_used']  = 0.0
			self.status['mem_used']   = 0.0
			self.status['cpu_load']   = 0.0
			self.status['shairport_load'] = 0.0
			self.status['mpd_load']   = 0.0
			success = False

		#print self
		return success

	def shairport_active(self):
		self.grab()
		if self.status['shairport_load'] > self.status['mpd_load']:
			active = True
		else:
			active = False
		return active

	def smooth(self, fifo, value):
		fifo.append(value)
		#fifo = fifo[-FIFO_LENGTH:]
		sum = 0.0
		for v in fifo:
			sum += v
		ave = sum/len(fifo)
		#print "Val %5d: %5d Smoothed: FIFO len %d" % (value, ave, len(fifo))

		return ave


#
# sys = SystemStatus()
# while True:
# 	sys.grab()
# 	print sys
