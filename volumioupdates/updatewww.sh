#!/bin/usr/bash
# Copy the display html,php, sql & js across
sudo cp -v _header.php /var/www/_header.php
sudo cp -v display.php /var/www/display.php
sudo cp -v display.html /var/www/templates/display.html
sudo cp -v settings.php /var/www/settings.php
sudo cp -v settings.html /var/www/templates/settings.html
sudo cp -v display-service.?.sql /var/www/updates
sudo cp -v modules.json /var/www/updates/modules.json
sudo cp -v player_lib.php /var/www/inc/player_lib.php
sudo cp -v player_wrk.php /var/www/command/player_wrk.php
echo "All copied across"
