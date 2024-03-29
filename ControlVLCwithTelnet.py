# First Run this command in the command line to make vlc run with telnet interface listening
# So that we can connect to it via telnet
# &"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe" --extraintf telnet --telnet-password admin --telnet-host 127.0.0.1 --telnet-port 1000
# For list of available commands you can connect to the telnet ie. -> telnet 127.0.0.1 1000
# and Run the command "help"

import datetime
from os import system
from pysubparser import parser
import telnetlib
from time import sleep


def seconds(t: datetime.time) -> int:
    return (t.hour * 60 + t.minute) * 60 + t.second


def encode(s: str) -> str:
    return s.encode('ascii')+b'\n'


host = "127.0.0.1"
port = 1000
timeout = 1
password = "admin"
tn = telnetlib.Telnet(host=host, port=port, timeout=timeout)
# Wait until the password is asked
tn.read_until("Password:".encode("ascii"))
# Enter the Password
tn.write(encode(password))
tn.read_until(encode(">"), timeout=1)

# =============================================
# To run any command in VLC using telnet
# tn.write(encode("Put Command Here))
tn.write(encode("volup 2"))
# =============================================

# Exit the telnet session
tn.write(encode("exit"))


# Full List of Commands
"""
+----[ VLM commands ]
|help
|    Commands Syntax:
|        new (name) vod|broadcast|schedule [properties]
|        setup (name) (properties)
|        show [(name)|media|schedule]
|        del (name)|all|media|schedule
|        control (name) [instance_name] (command)
|        save (config_file)
|        export
|        load (config_file)
|    Media Proprieties Syntax:
|        input (input_name)
|        inputdel (input_name)|all
|        inputdeln input_number
|        output (output_name)
|        option (option_name)[=value]
|        enabled|disabled
|        loop|unloop (broadcast only)
|        mux (mux_name)
|    Schedule Proprieties Syntax:
|        enabled|disabled
|        append (command_until_rest_of_the_line)
|        date (year)/(month)/(day)-(hour):(minutes):(seconds)|now
|        period (years_aka_12_months)/(months_aka_30_days)/(days)-(hours):(minutes):(seconds)
|        repeat (number_of_repetitions)
|    Control Commands Syntax:
|        play [input_number]
|        pause
|        stop
|        seek [+-](percentage) | [+-](seconds)s | [+-](milliseconds)ms
+----[ CLI commands ]
| add XYZ  . . . . . . . . . . . . . . . . . . . . add XYZ to playlist
| enqueue XYZ  . . . . . . . . . . . . . . . . . queue XYZ to playlist
| playlist . . . . . . . . . . . . .  show items currently in playlist
| search [string]  . .  search for items in playlist (or reset search)
| delete [X] . . . . . . . . . . . . . . . . delete item X in playlist
| move [X][Y]  . . . . . . . . . . . . move item X in playlist after Y
| sort key . . . . . . . . . . . . . . . . . . . . . sort the playlist
| sd [sd]  . . . . . . . . . . . . . show services discovery or toggle
| play . . . . . . . . . . . . . . . . . . . . . . . . . . play stream
| stop . . . . . . . . . . . . . . . . . . . . . . . . . . stop stream
| next . . . . . . . . . . . . . . . . . . . . . .  next playlist item
| prev . . . . . . . . . . . . . . . . . . . .  previous playlist item
| goto, gotoitem . . . . . . . . . . . . . . . . .  goto item at index
| repeat [on|off]  . . . . . . . . . . . . . .  toggle playlist repeat
| loop [on|off]  . . . . . . . . . . . . . . . .  toggle playlist loop
| random [on|off]  . . . . . . . . . . . . . .  toggle playlist random
| clear  . . . . . . . . . . . . . . . . . . . . .  clear the playlist
| status . . . . . . . . . . . . . . . . . . . current playlist status
| title [X]  . . . . . . . . . . . . . . set/get title in current item
| title_n  . . . . . . . . . . . . . . . .  next title in current item
| title_p  . . . . . . . . . . . . . .  previous title in current item
| chapter [X]  . . . . . . . . . . . . set/get chapter in current item
| chapter_n  . . . . . . . . . . . . . .  next chapter in current item
| chapter_p  . . . . . . . . . . . .  previous chapter in current item
|
| seek X . . . . . . . . . . . seek in seconds, for instance `seek 12'
| pause  . . . . . . . . . . . . . . . . . . . . . . . .  toggle pause
| fastforward  . . . . . . . . . . . . . . . . . . set to maximum rate
| rewind . . . . . . . . . . . . . . . . . . . . . set to minimum rate
| faster . . . . . . . . . . . . . . . . . .  faster playing of stream
| slower . . . . . . . . . . . . . . . . . .  slower playing of stream
| normal . . . . . . . . . . . . . . . . . .  normal playing of stream
| rate [playback rate] . . . . . . . . . .  set playback rate to value
| frame  . . . . . . . . . . . . . . . . . . . . . play frame by frame
| fullscreen, f, F [on|off]  . . . . . . . . . . . . toggle fullscreen
| info [X] . .  information about the current stream (or specified id)
| stats  . . . . . . . . . . . . . . . .  show statistical information
| get_time . . . . . . . . .  seconds elapsed since stream's beginning
| is_playing . . . . . . . . . . . .  1 if a stream plays, 0 otherwise
| get_title  . . . . . . . . . . . . . the title of the current stream
| get_length . . . . . . . . . . . .  the length of the current stream
|
| volume [X] . . . . . . . . . . . . . . . . . .  set/get audio volume
| volup [X]  . . . . . . . . . . . . . . .  raise audio volume X steps
| voldown [X]  . . . . . . . . . . . . . .  lower audio volume X steps
| achan [X]  . . . . . . . . . . . .  set/get stereo audio output mode
| atrack [X] . . . . . . . . . . . . . . . . . . . set/get audio track
| vtrack [X] . . . . . . . . . . . . . . . . . . . set/get video track
| vratio [X] . . . . . . . . . . . . . . .  set/get video aspect ratio
| vcrop, crop [X]  . . . . . . . . . . . . . . . .  set/get video crop
| vzoom, zoom [X]  . . . . . . . . . . . . . . . .  set/get video zoom
| vdeinterlace [X] . . . . . . . . . . . . . set/get video deinterlace
| vdeinterlace_mode [X]  . . . . . . .  set/get video deinterlace mode
| snapshot . . . . . . . . . . . . . . . . . . . . take video snapshot
| strack [X] . . . . . . . . . . . . . . . . .  set/get subtitle track
|
| vlm  . . . . . . . . . . . . . . . . . . . . . . . . .  load the VLM
| description  . . . . . . . . . . . . . . . . .  describe this module
| help, ? [pattern]  . . . . . . . . . . . . . . . . .  a help message
| longhelp [pattern] . . . . . . . . . . . . . . a longer help message
| lock . . . . . . . . . . . . . . . . . . . .  lock the telnet prompt
| logout . . . . . . . . . . . . . .  exit (if in a socket connection)
| quit . . . . . . . .  quit VLC (or logout if in a socket connection)
| shutdown . . . . . . . . . . . . . . . . . . . . . . .  shutdown VLC
+----[ end of help ]
"""
