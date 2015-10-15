#!/bin/bash
#
# VolumioDisplay set up script
#
#
# v0.1  Baloothebear4    23/09/15

#Install all the libraries required
# python
# ssh1306
# pil etc

#Set up access permission defaults so config file is shared
sudo chmod g+w,o+w /etc
sudo usermod -a -G volumio www-data
umask g+w
echo "Config file access permissions established"
