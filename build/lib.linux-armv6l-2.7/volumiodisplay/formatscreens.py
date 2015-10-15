#
#
# Volumio Metadata Display
# v0.1     12.08.15     Baloothebear4
#
# Module : formatscreens -
# Purpose: Routines to setup and structure screens for display, display independant
#          Abstracts screens available and provides control logic
#
##

IDLE_PERIOD   = 10    # this is the number ticks to wait before activating the screensaver when idle
NOT_AVAILABLE = '"not available"'

from oled_screens import Screens
import time

class Display:
# This is the overall class capturing the various displays that could be used
	def __init__( self ):
		# display_screens is a dictionary with the types of screens
		# this is the first one to display
		self.screens = Screens()
		self.active_screen = 0				# this is current screen in the list to display
		self.screens_to_display = []			# if no screens selected then dont display anything
		self.idle_counter = 0
		self.screensaver_selected = False

	def update( self, next ):
		# Control logic for which screen to display
		# Either update each screen moving on to the next one when told to move to the next,
		# or display the startup, screensaver or exit screens as appropriate
		if next:
			self.next_screen()

		if self.idle_counter < IDLE_PERIOD:
			if self.screens.update( self.screens_to_display[ self.active_screen ] ):  # ie the system is idle_counter
				self.idle_counter += 1
		elif self.screensaver_selected:
			idle = self.screens.update( 'screensaver' )	# ie system is no longer idle
			if not idle:	self.idle_counter = 0
		else:
			if self.screens.update( self.screens_to_display[ self.active_screen ] ):  # ie the system is idle_counter
				self.idle_counter += 1
			else:
				self.idle_counter = 0

		#print self.idle_counter

	def select( self, user_selection ):
		#create a list of the screens to display based on ones available and selected by the user
		#user selection is a list of screen shortcuts
		#print "user entered " + str( user_selection )
		self.active_screen = 0
		self.screens_to_display = []
		for selection in user_selection:
			if selection in self.screens.shortcuts().values():

				for s, shortcut in self.screens.shortcuts().items():

					if selection == shortcut and self.screens.availability()[ s ] != NOT_AVAILABLE:
						if s == 'screensaver':
							self.screensaver_selected = True
						else:
							self.screens_to_display.append( s )
					elif selection == shortcut and self.screens.availability()[ s ] == NOT_AVAILABLE:
						print "Selected screen %s, <%s> is not available" % (s, shortcut)
			else:
				print "Screen selection <%s> is not recognised" % selection

	def available(self):
		return self.screens.availability()

	def shortcuts(self):
		return self.screens.shortcuts()

	def startup( self ):
		self.screens.update( 'init' )

	def shutdown( self ):
		self.screens.update( 'exit' )

	def screen_type( self ):
		return( self.screens.display_type())

	def help_text( self ):
		help = '\nDisplay type: ' + self.screens.display_type() + '\nScreens available:'
		for s, a in self.available.items():

			if  a != NOT_AVAILABLE:
				help += '\n   <%s> %s screen: %s ' % ( self.screens.shortcuts()[ s ], s, a)

		return( help )

	def next_screen( self ):
		#  an algorithm to go to the next screen
		self.active_screen = self.active_screen + 1
		if self.active_screen == len( self.screens_to_display ):
			self.active_screen = 0
