#!/bin/bash

# Place this file in /etc/profile.d
# Ensure it is executable
# Effect: Starts the video player on boot, but in a separate thread

forked_start(){
    source /home/athos/repos/bin/activate
    cd /home/athos/repos/Pi-RFID-Video-Player
    python3 videoEngine.pyw
}

forked_start &