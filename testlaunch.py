import vlc
from time import sleep

# creating vlc media player object
player = vlc.Instance()
media = player.media_player_new("/home/athos/Videos/Library1/DA_Mulan.mp4")

media.set_fullscreen(1)
sleep(1)
media.play()
sleep(1)

while media.is_playing() == 1:
    sleep(1)