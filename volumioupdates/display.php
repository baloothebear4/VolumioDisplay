<?php
/*
 *      PlayerUI Copyright (C) 2013 Andrea Coiutti & Simone De Gregori
 *		 Tsunamp Team
 *      http://www.tsunamp.com
 *
 *  This Program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 3, or (at your option)
 *  any later version.
 *
 *  This Program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with RaspyFi; see the file COPYING.  If not, see
 *  <http://www.gnu.org/licenses/>.
 *
 *
 *	UI-design/JS code by: 	Andrea Coiutti (aka ACX)
 * PHP/JS code by:			Simone De Gregori (aka Orion)
 *
 * file:		display.php
 * version:		1.0
 * notes   created from system.php, sets up the  display options for connected displays
 */

// common include
include('inc/connection.php');
playerSession('open',$db,'','');
playerSession('unlock',$db,'','');
$VDconf = '/etc/VolumioDisplay.conf';

?>

<?php
if (isset($_POST['syscmd'])){
	switch ($_POST['syscmd']) {

	case 'reboot':

			if ($_SESSION['w_lock'] != 1 && $_SESSION['w_queue'] == '') {
			// start / respawn session
			session_start();
			$_SESSION['w_queue'] = "reboot";
			$_SESSION['w_active'] = 1;
			// set UI notify
			$_SESSION['notify']['title'] = 'REBOOT';
			$_SESSION['notify']['msg'] = 'reboot player initiated...';
			// unlock session file
			playerSession('unlock');
			} else {
			echo "background worker busy";
			}
		// unlock session file
		playerSession('unlock');
		break;

	case 'poweroff':

			if ($_SESSION['w_lock'] != 1 && $_SESSION['w_queue'] == '') {
			// start / respawn session
			session_start();
			$_SESSION['w_queue'] = "poweroff";
			$_SESSION['w_active'] = 1;
			// set UI notify
			$_SESSION['notify']['title'] = 'SHUTDOWN';
			$_SESSION['notify']['msg'] = 'shutdown player initiated...';
			// unlock session file
			playerSession('unlock');
			} else {
			echo "background worker busy";
			}
		break;

	case 'mpdrestart':

			if ($_SESSION['w_lock'] != 1 && $_SESSION['w_queue'] == '') {
			// start / respawn session
			session_start();
			$_SESSION['w_queue'] = "mpdrestart";
			$_SESSION['w_active'] = 1;
			// set UI notify
			$_SESSION['notify']['title'] = 'MPD RESTART';
			$_SESSION['notify']['msg'] = 'restarting MPD daemon...';
			// unlock session file
			playerSession('unlock');
			} else {
			echo "background worker busy";
			}
		break;

	case 'backup':

			if ($_SESSION['w_lock'] != 1 && $_SESSION['w_queue'] == '') {
			// start / respawn session
			session_start();
			$_SESSION['w_jobID'] = wrk_jobID();
			$_SESSION['w_queue'] = 'backup';
			$_SESSION['w_active'] = 1;
			playerSession('unlock');
				// wait worker response loop
				while (1) {
				sleep(2);
				session_start();
					if ( isset($_SESSION[$_SESSION['w_jobID']]) ) {
					// set UI notify
					$_SESSION['notify']['title'] = 'BACKUP';
					$_SESSION['notify']['msg'] = 'backup complete.';
					pushFile($_SESSION[$_SESSION['w_jobID']]);
					unset($_SESSION[$_SESSION['w_jobID']]);
					break;
					}
				session_write_close();
				}
			} else {
			session_start();
			$_SESSION['notify']['title'] = 'Job Failed';
			$_SESSION['notify']['msg'] = 'background worker is busy.';
			}
		// unlock session file
		playerSession('unlock');
		break;

	case 'updatempdDB':

			if ($_SESSION['w_lock'] != 1 && $_SESSION['w_queue'] == '') {
				session_start();
				sendMpdCommand($mpd,'update');
				// set UI notify
				$_SESSION['notify']['title'] = 'MPD Update';
				$_SESSION['notify']['msg'] = 'database update started...';
				// unlock session file
				playerSession('unlock');
			} else {
				echo "background worker busy";
				playerSession('unlock');
			}

	break;

	case 'clearqueue':

			if ($_SESSION['w_lock'] != 1 && $_SESSION['w_queue'] == '') {
			session_start();
			sendMpdCommand($mpd,'clear');
			// set UI notify
			$_SESSION['notify']['title'] = 'Clear Queue';
			$_SESSION['notify']['msg'] = 'Play Queue Cleared';
			// unlock session file
			playerSession('unlock');
			} else {
			echo "background worker busy";
			}
			// unlock session file
			playerSession('unlock');
	break;

	case 'updateui':

			if ($_SESSION['w_lock'] != 1 && $_SESSION['w_queue'] == '') {
			// start / respawn session
			session_start();
			$_SESSION['w_queue'] = "updateui";
			$_SESSION['w_active'] = 1;
			// set UI notify
			$_SESSION['notify']['title'] = 'Update';
			$_SESSION['notify']['msg'] = 'Retrieving Updates, if available';
			// unlock session file
			playerSession('unlock');
			} else {
			echo "background worker busy";
			}
	break;

	case 'totalbackup':

		break;

	case 'restore':

		break;

	}

}

//Make sure the display switches are aligned with config file
$VolumioDisplayConfig = read_VolumioDisplay_config( $VDconf );
init_displayscreens( $VolumioDisplayConfig, $db );

$displaysettingschanged = False;

//bitrate Screen Display
if (isset($_POST['bitratescreen']) && $_POST['bitratescreen'] != $_SESSION['bitratescreen']){
	// load worker queue
	// start / respawn session
	session_start();
	// save new value on SQLite datastore
	if ($_POST['bitratescreen'] == 1 OR $_POST['bitratescreen'] == 0) {
		playerSession('write',$db,'bitratescreen',$_POST['bitratescreen']);
		$VolumioDisplayConfig['screens_active']['bitrate'] = $_POST['bitratescreen'];
	}
	// set UI notify
	$_SESSION['notify']['title'] = 'Display settings';
	if ($_POST['bitratescreen'] == 1) {

		$_SESSION['notify']['msg'] .= 'Bitrate screen enabled\n';
	} else {
		$_SESSION['notify']['msg'] .= 'Bitrate screen disabled\n';
	}
	// unlock session file
	$displaysettingschanged = True;
	playerSession('unlock');
}
//tracks Screen Display
if (isset($_POST['tracksscreen']) && $_POST['tracksscreen'] != $_SESSION['tracksscreen']){
	// load worker queue
	// start / respawn session
	session_start();
	// save new value on SQLite datastore
	if ($_POST['tracksscreen'] == 1 OR $_POST['tracksscreen'] == 0) {
		playerSession('write',$db,'tracksscreen',$_POST['tracksscreen']);
		$VolumioDisplayConfig['screens_active']['tracks'] = $_POST['tracksscreen'];
	}
	// set UI notify
	$_SESSION['notify']['title'] = 'Display settings';
	if ($_POST['tracksscreen'] == 1) {
		$_SESSION['notify']['msg'] .= 'Tracks screen enabled\n';
	} else {
		$_SESSION['notify']['msg'] .= 'Tracks screen disabled\n';
	}
	// unlock session file
	$displaysettingschanged = True;
	playerSession('unlock');
}


//volumio Screen Display
if (isset($_POST['volumioscreen']) && $_POST['volumioscreen'] != $_SESSION['volumioscreen']){
	// load worker queue
	// start / respawn session
	session_start();
	// save new value on SQLite datastore
	if ($_POST['volumioscreen'] == 1 OR $_POST['volumioscreen'] == 0) {
	playerSession('write',$db,'volumioscreen',$_POST['volumioscreen']);
	$VolumioDisplayConfig['screens_active']['volumio'] = $_POST['volumioscreen'];
	}
	// set UI notify
	$_SESSION['notify']['title'] = 'Display settings';
	if ($_POST['volumioscreen'] == 1) {
		$_SESSION['notify']['msg'] .= 'Volumio screen enabled\n';
	} else {
		$_SESSION['notify']['msg'] .= 'Volumio screen disabled\n';
	}
	// unlock session file
	$displaysettingschanged = True;
	playerSession('unlock');
}
//System Screen Display
if (isset($_POST['systemscreen']) && $_POST['systemscreen'] != $_SESSION['systemscreen']){
	// load worker queue
	// start / respawn session
	session_start();
	// save new value on SQLite datastore
	if ($_POST['systemscreen'] == 1 OR $_POST['systemscreen'] == 0) {
		playerSession('write',$db,'systemscreen',$_POST['systemscreen']);
		$VolumioDisplayConfig['screens_active']['system'] = $_POST['systemscreen'];
	}
	// set UI notify
	$_SESSION['notify']['title'] = 'Display settings';
	if ($_POST['systemscreen'] == 1) {
		$_SESSION['notify']['msg'] .= 'System screen enabled\n';
	} else {
		$_SESSION['notify']['msg'] .= 'System screen disabled\n';
	}

	// unlock session file
	$displaysettingschanged = True;
	playerSession('unlock');

}
//Visualiser Screen Display
if (isset($_POST['visualiserscreen']) && $_POST['visualiserscreen'] != $_SESSION['visualiserscreen']){
	// load worker queue
	// start / respawn session
	session_start();
	// save new value on SQLite datastore
	if ($_POST['visualiserscreen'] == 1 OR $_POST['visualiserscreen'] == 0) {
		playerSession('write',$db,'visualiserscreen',$_POST['visualiserscreen']);
		$VolumioDisplayConfig['screens_active']['visualiser'] = $_POST['visualiserscreen'];
	}
	// set UI notify
	$_SESSION['notify']['title'] = 'Display settings';
	if ($_POST['visualiserscreen'] == 1) {
		$_SESSION['notify']['msg'] .= 'Visualiser screen enabled\n';
	} else {
		$_SESSION['notify']['msg'] .= 'Visualiser screen disabled\n';
	}
	// unlock session file
	$displaysettingschanged = True;
	playerSession('unlock');

}//screensaver Screen Display
if (isset($_POST['screensaverscreen']) && $_POST['screensaverscreen'] != $_SESSION['screensaverscreen']){
	// load worker queue
	// start / respawn session
	session_start();
	// save new value on SQLite datastore
	if ($_POST['screensaverscreen'] == 1 OR $_POST['screensaverscreen'] == 0) {
		playerSession('write',$db,'screensaverscreen',$_POST['screensaverscreen']);
		$VolumioDisplayConfig['screens_active']['screensaver'] = $_POST['screensaverscreen'];
	}
	// set UI notify
	$_SESSION['notify']['title'] = 'Display settings';
	if ($_POST['screensaverscreen'] == 1) {
		$_SESSION['notify']['msg'] .= 'Screensaver screen enabled\n';
	} else {
		$_SESSION['notify']['msg'] .= 'Screensaver screen disabled\n';
	}
	// unlock session file
	$displaysettingschanged = True;
	playerSession('unlock');
}
//coverart Screen Display
if (isset($_POST['coverartscreen']) && $_POST['coverartscreen'] != $_SESSION['coverartscreen']){
	// load worker queue
	// start / respawn session
	session_start();
	// save new value on SQLite datastore
	if ($_POST['coverartscreen'] == 1 OR $_POST['coverartscreen'] == 0) {
		playerSession('write',$db,'coverartscreen',$_POST['coverartscreen']);
		$VolumioDisplayConfig['screens_active']['coverart'] = $_POST['coverartscreen'];
	}
	// set UI notify
	$_SESSION['notify']['title'] = 'Display settings';
	if ($_POST['coverartscreen'] == 1) {
		$_SESSION['notify']['msg'] .= 'Coverart screen enabled\n';
	} else {
		$_SESSION['notify']['msg'] .= 'Coverart screen disabled\n';
	}
	// unlock session file
	$displaysettingschanged = True;
	playerSession('unlock');
}
//Screen duration setting
if (isset($_POST['screenduration']) && $_POST['screenduration'] != $_SESSION['screenduration']){
	// load worker queue
	// start / respawn session
	session_start();
	// save new value on SQLite datastore
	$_SESSION['notify']['title'] = 'Display settings';
	if (intval($_POST['screenduration']) > 0 && intval($_POST['screenduration']) < 100) {
		playerSession('write',$db,'screenduration',$_POST['screenduration']);
		$VolumioDisplayConfig['settings']['screen_duration'] = $_POST['screenduration'];
	// set UI notify
		$_SESSION['notify']['msg'] .= 'Screen duration set to '.$_POST['screenduration'].'\n';
	} else {
		$_SESSION['notify']['msg'] .= 'Screen duration invalid (1-99)\n';
	}
	// unlock session file
	$displaysettingschanged = True;
	playerSession('unlock');
}

//check if the display setting have been changed, tell the user and update the config file
if ($displaysettingschanged == True ) {
	//update the config file
	write_php_ini( $VolumioDisplayConfig, $VDconf);

}


//Display options
$_system_select['tracksscreen1'] .= "<input type=\"radio\" name=\"tracksscreen\" id=\"toggletracksscreen1\" value=\"1\" ".(($_SESSION['tracksscreen'] == 1) ? "checked=\"checked\"" : "").">\n";
$_system_select['tracksscreen0'] .= "<input type=\"radio\" name=\"tracksscreen\" id=\"toggletracksscreen2\" value=\"0\" ".(($_SESSION['tracksscreen'] == 0) ? "checked=\"checked\"" : "").">\n";
$_system_select['bitratescreen1'] .= "<input type=\"radio\" name=\"bitratescreen\" id=\"togglebitratescreen1\" value=\"1\" ".(($_SESSION['bitratescreen'] == 1) ? "checked=\"checked\"" : "").">\n";
$_system_select['bitratescreen0'] .= "<input type=\"radio\" name=\"bitratescreen\" id=\"togglebitratescreen2\" value=\"0\" ".(($_SESSION['bitratescreen'] == 0) ? "checked=\"checked\"" : "").">\n";
$_system_select['volumioscreen1'] .= "<input type=\"radio\" name=\"volumioscreen\" id=\"togglevolumioscreen1\" value=\"1\" ".(($_SESSION['volumioscreen'] == 1) ? "checked=\"checked\"" : "").">\n";
$_system_select['volumioscreen0'] .= "<input type=\"radio\" name=\"volumioscreen\" id=\"togglevolumioscreen2\" value=\"0\" ".(($_SESSION['volumioscreen'] == 0) ? "checked=\"checked\"" : "").">\n";
$_system_select['systemscreen1'] .= "<input type=\"radio\" name=\"systemscreen\" id=\"togglesystemscreen1\" value=\"1\" ".(($_SESSION['systemscreen'] == 1) ? "checked=\"checked\"" : "").">\n";
$_system_select['systemscreen0'] .= "<input type=\"radio\" name=\"systemscreen\" id=\"togglesystemscreen2\" value=\"0\" ".(($_SESSION['systemscreen'] == 0) ? "checked=\"checked\"" : "").">\n";
$_system_select['visualiserscreen1'] .= "<input type=\"radio\" name=\"visualiserscreen\" id=\"togglevisualiserscreen1\" value=\"1\" ".(($_SESSION['visualiserscreen'] == 1) ? "checked=\"checked\"" : "").">\n";
$_system_select['visualiserscreen0'] .= "<input type=\"radio\" name=\"visualiserscreen\" id=\"togglevisualiserscreen2\" value=\"0\" ".(($_SESSION['visualiserscreen'] == 0) ? "checked=\"checked\"" : "").">\n";
$_system_select['screensaverscreen1'] .= "<input type=\"radio\" name=\"screensaverscreen\" id=\"togglescreensaverscreen1\" value=\"1\" ".(($_SESSION['screensaverscreen'] == 1) ? "checked=\"checked\"" : "").">\n";
$_system_select['screensaverscreen0'] .= "<input type=\"radio\" name=\"screensaverscreen\" id=\"togglescreensaverscreen2\" value=\"0\" ".(($_SESSION['screensaverscreen'] == 0) ? "checked=\"checked\"" : "").">\n";
$_system_select['coverartscreen1'] .= "<input type=\"radio\" name=\"coverartscreen\" id=\"togglecoverartscreen1\" value=\"1\" ".(($_SESSION['coverartscreen'] == 1) ? "checked=\"checked\"" : "").">\n";
$_system_select['coverartscreen0'] .= "<input type=\"radio\" name=\"coverartscreen\" id=\"togglecoverartscreen2\" value=\"0\" ".(($_SESSION['coverartscreen'] == 0) ? "checked=\"checked\"" : "").">\n";

// Display Help screens
$_SESSION['volumiodisplay']['displayhelp'] .= $VolumioDisplayConfig['settings']['displayhelp'];
//$_SESSION['volumiodisplay']['displayhelp] .= "Display intro text";
$_SESSION['bitratescreen2']['displayhelp'] .= $VolumioDisplayConfig['screens_available']['bitrate'];
$_SESSION['tracksscreen2']['displayhelp'] .= $VolumioDisplayConfig['screens_available']['tracks'];
$_SESSION['volumioscreen2']['displayhelp'] .= $VolumioDisplayConfig['screens_available']['volumio'];
$_SESSION['systemscreen2']['displayhelp'] .= $VolumioDisplayConfig['screens_available']['system'];
$_SESSION['visualiserscreen2']['displayhelp'] .= $VolumioDisplayConfig['screens_available']['visualiser'];
$_SESSION['screensaverscreen2']['displayhelp'] .= $VolumioDisplayConfig['screens_available']['screensaver'];
$_SESSION['coverartscreen2']['displayhelp'] .= $VolumioDisplayConfig['screens_available']['coverart'];

$_system_select['bitratescreen2'] .= "<span class=\"help-block\">".$_SESSION['bitratescreen2']['displayhelp'];
$_system_select['tracksscreen2'] .= "<span class=\"help-block\">".$_SESSION['tracksscreen2']['displayhelp'];
$_system_select['volumioscreen2'] .= "<span class=\"help-block\">".$_SESSION['volumioscreen2']['displayhelp'];
$_system_select['systemscreen2'] .= "<span class=\"help-block\">".$_SESSION['systemscreen2']['displayhelp'];
$_system_select['visualiserscreen2'] .= "<span class=\"help-block\">".$_SESSION['visualiserscreen2']['displayhelp'];
$_system_select['screensaverscreen2'] .= "<span class=\"help-block\">".$_SESSION['screensaverscreen2']['displayhelp'];
$_system_select['coverartscreen2'] .= "<span class=\"help-block\">".$_SESSION['coverartscreen2']['displayhelp'];
$_system_select['volumiodisplay'] .= "<p>" .$_SESSION['volumiodisplay']['displayhelp']. "</p>";
$_screenduration = $_SESSION['screenduration'];

//$_SESSION['debugVD'] = $_system_select['volumiodisplay'];

//debug
$_system_select['debug'] .= "<span class=\"help-block\">".$_SESSION['debugVD'];

// set template
$tpl = "display.html";
?>

<?php
$sezione = basename(__FILE__, '.php');
include('_header.php');
?>

<!-- content -->
<?php
// wait for worker output if $_SESSION['w_active'] = 1
waitWorker(1);
eval("echoTemplate(\"".getTemplate("templates/$tpl")."\");");
?>
<!-- content -->

<?php
debug($_POST);
?>

<?php include('_footer.php'); ?>
