#!/bin/usr/bash
# Copy the display html,php, sql & js across
sudo cp -v  /var/www/_header.php  _header.php
sudo cp -v  /var/www/display.php  display.php
sudo cp -v  /var/www/templates/display.html  display.html
sudo cp -v  /var/www/settings.php  settings.php
sudo cp -v /var/www/templates/settings.html  settings.html
sudo cp -v  /var/www/updates  display-service.?.sql
sudo cp -v /var/www/updates/modules.json  modules.json
sudo cp -v  /var/www/inc/player_lib.php  player_lib.php
sudo cp -v  /var/www/command/player_wrk.php  player_wrk.php
echo "All copied back"
