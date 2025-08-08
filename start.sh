xrandr --output HDMI-1 --set "left margin" 70
xrandr --output HDMI-1 --set "right margin" 70
xrandr -s 640x480
cd /home/zlx/RacesowArcade
source bin/activate
bin/python RacesowArcade.pyw
xrandr --output HDMI-1 --set "left margin" 0
xrandr --output HDMI-1 --set "right margin" 0
xrandr -s 1920x1080
