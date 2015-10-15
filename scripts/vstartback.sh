#!/bin/bash
#
# Startup script for VolumioDisplay
#
# Purpose: create a continuous log capturing debug and error messages
#          2 versions exist - one that is forked and one for execute from an init.d script (held in /usr/local/bin)
#
# v0.1 baloothebear4
#
LOGPATH=/var/log/VolumioDisplay
LOGFILE=$LOGPATH/vd.log
sudo chmod +rwx $LOGPATH
# put in a test to make the directory if if doesnt exist
echo "Starting VolumioDisplay on "$(date) &>>$LOGFILE
sudo python volumiodisplay.py &>> $LOGFILE &
