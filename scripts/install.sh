#!/bin/sh
#
# Install script for volumiodisplay
#
# assume this is run from the top level directory of the package
#

# install all the dependent libraries required
# perform the python install

#i2c environment
sudo cp config.txt /boot/config.txt
sudo adduser volumio i2c

# Shairport metadata
sudo mkdir /etc/shairport_metadata
sudo chmod +rw /etc/shairport_metadata
# setup the run enviroment and daemon to start on powerup
sudo cp vdstart /usr/local/bin/vdstart
sudo chmod +x /usr/local/bin/vdstart

sudo cp volumiodisplay.sh /etc/init.d/volumiodisplay
sudo update-rc.d volumiodisplay defaults
