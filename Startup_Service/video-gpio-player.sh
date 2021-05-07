#!/bin/bash

# Place this file in /etc/profile.d
# Ensure it is executable
# Effect: Starts the video GPIO player on boot, but in a separate thread

forked_start(){
    sudo su pi
    cd ~/repos/Pi-RFID-Video-Player
    sudo python3 videoEngineGPIO.pyw
}

forked_start &