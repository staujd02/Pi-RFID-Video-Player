#!/bin/bash
DISPLAY=:0
export DISPLAY
num=1
attempts=200
while [ 1 == 1 ]; do
    if ! xset q &>/dev/null; then
        num=$(($num+1))
        sleep .5
        if [ $num -gt $attempts ]; then
            echo "Could not find X server at \$DISPLAY [$DISPLAY]" >&2
            exit 1
        fi
    else
        break
    fi
done
source ~/repos/bin/activate
cd ~/repos/Pi-RFID-Video-Player
~/repos/bin/python3 videoEngine.pyw
