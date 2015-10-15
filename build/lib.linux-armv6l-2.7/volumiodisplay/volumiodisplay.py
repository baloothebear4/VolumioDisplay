#!/usr/bin python
#
# Volumio Display Project
#
# v0.1     12.08.15     Baloothebear4
# v0.2	   20.08.15		Baloothebear4 -- port to OLED Display
#
# Module : main
# Purpose:
#      Main routine to parse arguments, selecting which screens to be displayed.
#	   Basic polling loop to collect meta data and dump to the screen
#	   Idea is that display routines can be changed to suit different displays
#
#		The screens selected are displayed in rotation, these are checked against
#		the screens that are available are listed in the config file or by the help command
#		If the -s option is used on the command line the selected screens are used
#		Otherwise the default is to use the selection in  /etc/VolumioDisplay.conf
#		This config file is used to dynamically changes the screens chosen as the users can use the Display menu to make changes
#		The base config file is generated with the available screens if not in existance

import time, sys, io, os, stat
from formatscreens import Display
from ConfigParser import SafeConfigParser

SCREEN_ACTIVE_TIME = 3     # default time to display one SCREEN_ACTIVE_TIME, note this updated by the config file
SCREEN_REFRESH     = 0.25     # how often to refresh
HELP_TEXT_HEADER   = '\n%s\n\n%s\n%s\n%s\n' % (
					   	'Usage: $python VolumioDisplay.py <help | -h> <-s> <screen> <screen> ...',
					 	'VolumioDisplay will periodically display one or more screens in rotation',
						'presenting music and quality metadata (eg Song, bitrate) being played',
						'by Volumio, either through MPD, Webradio, Spotify or Airplay.'
					 	)
CONFIG_FILE_HEADER = '\n%s\n%s\n%s\n%s\n%s\n\n%s\n' % (
					 	'# VolumioDisplay will periodically display one or more screens in rotation',
						'# presenting music and quality metadata (eg Song, bitrate) being played',
						'# by Volumio, either through MPD, Webradio, Spotify or Airplay.',
						'# This config file is dynamically updated from the Volumio WebUI',
						'# and will be created automatically if does not exist',
						'# v0.1   baloothebear4    13/09/2015'
					 	)
DISPLAY_INTRO_TEXT = "Display is capable of showing multiple screens in rotation, plus a screensaver when idle. Display type is: "
CONFIG_FILE	   	   = "/etc/VolumioDisplay.conf"
CONFIG_FILE_UMASK  = stat.S_IRWXG | stat.S_IRWXO | stat.S_IRWXU
CONFIG_SECTIONS    = ['intro', 'screens_available', 'screens_active', 'settings']
OFF = '0'
ON  = '1'


class Config:
	# config file structure:
	# [intro]   text about the file
	# [screens_available]  list of screens with with either decriptive text or "not available"
	# [screens_active]  list of screens set on or off - defaults to all off
	# [settings]  parameter settings eg Screen_duration

	def __init__(self, file, available, shortcuts, screen_type):
		self.parser = SafeConfigParser( allow_no_value= True )
		self.available = available
		self.shortcuts = shortcuts
		self.config_file = file
		self.screen_type = screen_type
		for section in CONFIG_SECTIONS:
			self.parser.add_section( section )

		#check if the config file exists, if not create one using the current display info
		if self.parser.read(file) == []:
			self.create(file)


	def create(self, file):
		#(re)creates a config file
		#Section Structure:
		print "Creating new config file: " + file

		self.parser.set( 'intro', CONFIG_FILE_HEADER )
		for s, a in self.available.items():
#				print "creating new config: %s:  %s" % (s, a)
 				self.parser.set( 'screens_available', s, a)
				self.parser.set( 'screens_active', s, OFF)

		self.parser.set('settings', 'screen_duration', str(SCREEN_ACTIVE_TIME) )
		self.parser.set('settings', 'displayhelp', '"'+DISPLAY_INTRO_TEXT+self.screen_type+'"' )

		try:
			#need to fix the file permissions os.system("")
			with open( file, 'w' ) as configfile:
				self.parser.write( configfile )
				os.chmod( file, CONFIG_FILE_UMASK )
		except:
			print "failed to create config file"
			raise

	def write_selections(self, sel):
		try:
			self.parser.read( self.config_file )
			with open( self.config_file, 'w' ) as configfile:
				for s, sh in self.shortcuts.items():
					state = OFF
					for scr in sel:
						if scr == sh:
							#print "writing to config: %s:  %s" % (sh, s)
							state = ON
						self.parser.set( 'screens_active', s, state)

					self.parser.write( configfile )
					os.chmod( self.config_file, CONFIG_FILE_UMASK )
				print self.parser
		except:
			print "failed to write to config file"
			raise

	def get_selections(self):
		selection = []
		try:
			self.parser.read( self.config_file )
			for s, a in self.available.items():
				screen_choice = self.parser.get( 'screens_active', s )
				if screen_choice == ON and a != 'not available':
					selection.append( self.shortcuts[ s ] )

		except IOError:
			print "could not read config file"

		return selection

	def get_duration(self):
		try:
			self.parser.read( self.config_file)
			duration = int(self.parser.get( 'settings', 'screen_duration'))
		except:
			duration = SCREEN_ACTIVE_TIME
			print 'Failed to read screen duration'

		return duration

	def __rpr__(self):
		#print out the whole config file - for debug purposes
		return

def main( argv ):

	displays = Display()
	config   = Config( CONFIG_FILE, displays.available(), displays.shortcuts(), displays.screen_type() )
	command_selection = False
	selected_screens = []


	#If the user has selected screens on the command line these take precedence:
	for opt in argv:
		if opt == 'h' or opt == '-h' or opt == 'help':
			print HELP_TEXT_HEADER + displays.help_text()
			sys.exit()
		elif opt =='-s':
		# selected screens come from command line
			command_selection = True
		elif command_selection == True:
			selected_screens.append( opt )

	#print "selected screens " + str(selected_screens)
	if command_selection:
		config.write_selections( selected_screens )
	else:
		selected_screens = config.get_selections()
	displays.startup()
	displays.select( selected_screens )
	time.sleep( SCREEN_REFRESH * 4 )

	try:			# keep going around until told to stop
		while True:

			for screen_time in range( config.get_duration() ):
				displays.update( False )
				time.sleep( SCREEN_REFRESH )

			new_selection = config.get_selections()     # check if user has changed config
			if new_selection == selected_screens:
				#print "no new selections"
				displays.update( True )                # move to the next screen
			else:
				selected_screens = new_selection
				#print "selected screens " + str(selected_screens)
				displays.select( selected_screens )

	except KeyboardInterrupt:
		pass

	displays.shutdown()

if __name__ == "__main__":
	main(sys.argv[1:])
