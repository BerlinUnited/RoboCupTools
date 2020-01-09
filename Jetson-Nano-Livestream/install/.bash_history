arecord -D plughw:1 --duration=10 -f cd -vv ~/test.wav 
arecord -D plughw:2 --duration=10 -f cd -vv ~/test.wav 
clear
gst-launch-1.0 v4l2src ! "video/x-raw, framerate=25/1, width=1280, height=720" ! omxh264enc target-bitrate=300000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
gst-launch-1.0 v4l2src ! "video/x-raw, framerate=25/1, width=1280, height=720" ! omxh264enc bitrate=300000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
gst-launch-1.0 videotestsrc is-live=1 ! videoconvert ! "video/x-raw, framerate=25/1, width=1280, height=720" ! omxh264enc bitrate=300000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
gst-launch-1.0 nvarguscamerasrc timeout=120 ! nvvidconv
clear
gst-launch-1.0 nvarguscamerasrc timeout=120 ! nvvidconv ! "video/x-raw, framerate=25/1, width=1280, height=720" ! omxh264enc bitrate=300000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc timeout=120 ! nvvidconv ! "video/x-raw, framerate=25/1, width=1280, height=720" ! omxh264enc bitrate=300000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 videotestsrc is-live=1 ! videoconvert ! "video/x-raw, framerate=25/1, width=1280, height=720" ! omxh264enc bitrate=300000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 videotestsrc is-live=1 ! videoconvert ! "video/x-raw, framerate=25/1, width=1280, height=720" ! omxh264enc bitrate=300000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. \
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 videotestsrc is-live=1 ! videoconvert ! "video/x-raw, framerate=25/1, width=1280, height=720" ! omxh264enc bitrate=300000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
gst-inspect-1.0 nvarguscamera
gst-inspect-1.0 nvarguscamerasrc
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 videotestsrc is-live=1 ! videoconvert ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=300000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 videotestsrc is-live=1 ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=300000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 videotestsrc is-live=1 ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=300000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 videotestsrc is-live=1 ! "video/x-raw, width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=300000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc timeout=120 silent=false ! "video/x-raw, width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=300000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc timeout=120 silent=false ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=300000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc timeout=120 silent=true ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=300000 control-rate=2 ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc timeout=120 silent=false ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=300000 control-rate=2 ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. \
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc timeout=120 silent=false ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=300000 control-rate=2 ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
gst-inspect-1.0 nvarguscamerasrc
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc timeout=120 silent=true ! 'video/x-raw(memory:NVMM), width=(int)3820, height=(int)1848, format=(string)NV12, framerate=(fraction)25/1' ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=300000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc timeout=120 silent=true ! 'video/x-raw(memory:NVMM), width=(int)3820, height=(int)1848, format=(string)NV12, framerate=(fraction)25/1' ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=4000000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
gst-launch-1.0 nvarguscamerasrc silent=true ! 'video/x-raw(memory:NVMM), width=(int)3820, height=(int)1848, format=(string)NV12, framerate=(fraction)25/1' ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=4500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
gst-launch-1.0 nvarguscamerasrc timeout=120 silent=true ! 'video/x-raw(memory:NVMM), width=(int)3820, height=(int)1848, format=(string)NV12, framerate=(fraction)28/1' ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=4500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
gst-launch-1.0 nvarguscamerasrc timeout=120 silent=true ! 'video/x-raw(memory:NVMM), width=(int)3820, height=(int)1848, format=(string)NV12, framerate=(fraction)28/1' ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)28/1" ! omxh264enc bitrate=4500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
gst-launch-1.0 nvarguscamerasrc timeout=120 silent=true ! 'video/x-raw(memory:NVMM), width=(int)3820, height=(int)1848, format=(string)NV12, framerate=(fraction)25/1' ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=4500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clea4r
clear
gst-launch-1.0 nvarguscamerasrc silent=true ! 'video/x-raw(memory:NVMM), width=(int)3820, height=(int)1848, format=(string)NV12, framerate=(fraction)25/1' ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=4500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
sudo reboot
htop
cat /sys/devices/virtual/thermal/thermal_zone*/temp
sudo apt-get install lm-sensors -y
sudo sensors-detect 
sensors 
sudo sensors-detect
sensors 
sudo sensors-detect
cleare
clear
sudo apt-get install sensors
cat /sys/devices/virtual/thermal/thermal_zone*/temp
37000
cat /sys/devices/virtual/thermal/thermal_zone*/type
cat /sys/devices/virtual/thermal/thermal_zone*/temp
cat /sys/devices/virtual/thermal/thermal_zone*
cat /sys/devices/virtual/thermal/thermal_zone1
cat /sys/devices/virtual/thermal/thermal_zone*/temp
cat /sys/devices/virtual/thermal/thermal_zone1/temp
cat /sys/devices/virtual/thermal/thermal_zone2/temp
cat /sys/devices/virtual/thermal/thermal_zone3/temp
cat /sys/devices/virtual/thermal/thermal_zone*/temp
sudo apt-get uninstall lm-sensors -y
sudo apt-get remove lm-sensors -y
sudo apt autoremove
cat /sys/devices/virtual/thermal/thermal_zone*/temp
gst-launch-1.0 nvarguscamerasrc silent=true ! 'video/x-raw(memory:NVMM), width=(int)3820, height=(int)1848, format=(string)NV12, framerate=(fraction)25/1' ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=4500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
gst-launch-1.0 nvarguscamerasrc silent=true ! 'video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1' ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=4500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
gst-launch-1.0 nvarguscamerasrc silent=true ! 'video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1' ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=4500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
sudo reboot
gst-launch-1.0 nvarguscamerasrc silent=true ! 'video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1' ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=4500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
sudo shutdown now
cd /tmp/pycharm_project_220/
ls
export GST_PLUGIN_PATH=$PWD
$PWD
PWD
cd ~
ls
2
3
4
5
6
7
8
9
10
11
12
13
git clone git://anongit.freedesktop.org/git/gstreamer/gst-pythonclear
clear
git clone git://anongit.freedesktop.org/git/gstreamer/gst-python
printenv
clear
export PYTHON=/usr/bin/python3
cd gst-python
./autogen.sh --disable-gtk-doc --noconfigure
./configure --with-libpython-dir="/usr/lib/aarch64-linux-gnu"
make
clear
cd ..
sudo rm -r gst-python/
git clone git://anongit.freedesktop.org/git/gstreamer/gst-python
export PYTHON=/usr/bin/python3
cd gst-python
git checkout 1.14
git pull
./autogen.sh --disable-gtk-doc --noconfigure
./configure --with-libpython-dir="/usr/lib/aarch64-linux-gnu"
ls
cd ..
sudo rm -r gst-python/
git clone git://anongit.freedesktop.org/git/gstreamer/gst-python
export PYTHON=/usr/bin/python3
cd gst-python
git checkout 1.14.1
./autogen.sh --disable-gtk-doc --noconfigure
./configure --with-libpython-dir="/usr/lib/aarch64-linux-gnu"
pip3 install pygobject-3.0
sudo apt-get install -y python-gi-dev
clear
./autogen.sh --disable-gtk-doc --noconfigure
./configure --with-libpython-dir="/usr/lib/aarch64-linux-gnu"
clear
sudo apt-get install -y python-gi-dev python3-dev gir1.2-gst-plugins-base-1.0
clear
./autogen.sh --disable-gtk-doc --noconfigure
./configure --with-libpython-dir="/usr/lib/aarch64-linux-gnu"
make
sudo make install
cd ..
wget https://gist.githubusercontent.com/jackersson/7baaff902d9f6c722460303f13cba289/raw/486758baeb71695291e3a49a98dc7395d064bfd3/gstreamer_empty_plugin_test_case.py
python3 gstreamer_empty_plugin_test_case.py
python3
clear
export GI_PATH=/usr/lib/python3/dist-packages/gi
python3 gstreamer_empty_plugin_test_case.py
cd gst-python/
ls
cd gi/
ls
cd overrides/
ls
clear
cd ~
export GI_PATH=/usr/lib/python3/dist-packages/gi
sudo cp ~/gst-python/gi/overrides/Gst.py $GI_PATH/overrides
sudo cp ~/gst-python/gi/overrides/GstPbutils.py $GI_PATH/overrides
sudo cp ~/gst-python/gi/overrides/_gi_gst.la $GI_PATH/overrides
sudo cp ~/gst-python/gi/overrides/_gi_gst.cpython-*m-*-linux-gnu.so $GI_PATH/overrides
python3 gstreamer_empty_plugin_test_case.py
clear
sudo ldconfig
sudo reboot
htop
python3 gstreamer_empty_plugin_test_case.py
cd /tmp/pycharm_project_220/
ls
export GST_PLUGIN_PATH=$PWD
python3 run.py -f example/car.mpg --images example/cat --cairo --fps
pip3
sudo apt-get install python3-pip
pip3
pip3 freeze
pip3 install numpy
htop
cd ..
cd pycharm_project_818/
ls
python3 run.py -f example/car.mpg --images example/cat --cairo --fps
python3 run.py -f example/car.mpg --images example/cat --cairo
pip3 freeze
pip3 install opencv-python
python3
clear
gst-inspect-1.0 gtksink
gst-inspect-1.0 gstoverlaycairo
htop
gst-inspect-1.0 gstoverlaycairo
gst-inspect-1.0 gstoverlayopencv
clear
gst-launch-1.0 nvarguscamerasrc silent=true ! 'video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1' ! nvvidconv ! 'video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1' ! omxh264enc bitrate=4500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! 'audio/x-raw,rate=48000' ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
export GST_DEBUG_DUMP_DOT_DIR=/home/arne
gst-launch-1.0 videotestsrc is-live=1 ! videoconvert ! "video/x-raw, width=1280, height=720, framerate=25/1" ! queue ! x264enc bitrate=2000 byte-stream=false key-int-max=60 bframes=0 aud=true tune=zerolatency ! "video/x-h264,profile=main" ! flvmux streamable=true name=mux ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs' audiotestsrc ! voaacenc bitrate=128000 ! mux.
sudo reboot
gst-launch-1.0 nvarguscamerasrc silent=true ! 'video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1' ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=4500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
gst-launch-1.0 nvarguscamerasrc silent=true ! 'video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1' ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=4500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer audiotestsrc ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
pacmd dump
clear
export GST_DEBUG_DUMP_DOT_DIR=/home/arne
gst-launch-1.0 nvarguscamerasrc silent=true ! 'video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1' ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=4500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioresample ! "audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location='rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs'
clear
sudo shutdown now
export GST_PLUGIN_PATH=/tmp/pycharm_project_818
gst-inspect-1.0 nvvidconv
cd /tmp/pycharm_project_818/
ls
cd ..
cd ~
mkdir Livestream
ls
cd Livestream/
ls
pip3 install Pillow
pip3 install wheel
pip install Pillow
pip3 install Pillow
clear
sudo apt install python3-pil
pip3 freeze
clear
htop
clear
gst-inspect-1.0 nvarguscamerasrc
sudo shutdown now
gst-inspect-1.0 nvarguscamerasrc
ls
cd Livestream/
ls
nano livestream.py 
ls
cd Livestream/
ls
python3 livestream.py 
sudo shutdown now
ifconfig
wpa_cli --info
wpa_cli status
sudo wpa_cli status
clear
sudo wpa_cli status
sudo nano /etc/network/interfaces
sudo wpa_cli status
ifconfig
sudo nano /etc/network/interfaces
sudo wpa_cli status
ls
htop
cd Livestream/
ls
nano livestream.py 
ls
cd Livestream/
ls
nano livestream.py 
ls
cd Livestream/
ls
nano livestream.py 
python3 livestream.py 
nano livestream.py 
python3 livestream.py 
sudo shutdown now
sudo chmod 664 /var/nvidia/nvcam/settings/camera_overrides.isp
sudo chown root:root /var/nvidia/nvcam/settings/camera_overrides.isp
ls
cd Livestream/
ls
python3 livestream.py 
sudo shutdown now
ls
cd Livestream/
python3 livestream.py 
gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM),width=3820, height=2464, framerate=21/1, format=NV12' ! nvvidconv flip-method=0 ! 'video/x-raw,width=960, height=616' ! nvvidconv ! nvegltransform ! nveglglessink -e
clear
gst-launch-1.0 nvarguscamerasrc sensor-id=0 ! 'video/x-raw(memory:NVMM), width=(int)3280, height=(int)2464'  ! nvvidconv flip-method=0 ! 'video/x-raw, format=(string)I420' ! xvimagesink -e
gst-launch-1.0 nvarguscamerasrc wbmode=0 awblock=true gainrange="8 8" ispdigitalgainrange="4 4" exposuretimerange="5000000 5000000" aelock=true ! nvvidconv ! xvimagesink
clear
gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM),width=3820, height=2464, framerate=21/1, format=NV12' ! nvvidconv flip-method=2 ! 'video/x-raw,width=1920, height=1080' ! nvvidconv ! nvegltransform ! nveglglessink -e
sudo reboot
gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM),width=3820, height=2464, framerate=21/1, format=NV12' ! nvvidconv flip-method=2 ! 'video/x-raw,width=1920, height=1080' ! nvvidconv ! nvegltransform ! nveglglessink -e
export DISPLAY=:0
gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM),width=3820, height=2464, f
cd Livestream/
ls
sudo nano preview.sh
chmod +777 preview.sh 
sudo chmod +777 preview.sh 
ls
./preview.sh 
sudo shutdown now
cd Livestream/
ls
python3 livestream.py 
sudo reboot
cd Livestream/
ls
python3 livestream.py 
ls
cd Livestream/
ls
python livestream.py 
sudo nano livestream.py 
python3 livestream.py 
sudo shutdown now
python3 livestream.py 
clear
exit
ls
python3 livestream.py 
exit
cd Livestream/
python3 livestream.py 
exit
screen
screen -r 
screen -r 7879.pts-0.arne-nano
screen -r 
ls
screen
ls
cd Livestream/
ls
python3 livestream.py 
screen
sudo apt-get install screen
screen
screen -r
sudo apt-get install screen
screen
psensor
sudo apt-get install psensor
psensor
sudo apt-get remove psensor
lmsensors 
sudo apt-get install lmsensors 
lmsensors 
lmsensors
sensors
clear
sudo apt-get install lm-sensors 
sensors
sudo sensors-detect 
sensors
cat /sys/devices/virtual/thermal/thermal_zone*/temp
cat /sys/devices/virtual/thermal/thermal_zone*/type
cat /sys/devices/virtual/thermal/thermal_zone*/temp
cd Livestream/
python3 livestream.py 
clear
python3 livestream.py 
sudo shutdown now
screen -r
exit
screen -r
screen
ls
sudo reboot
screen
cd Livestream/
python3 livestream.py 
cd Livestream/
ls
screen
sudo shutdown now
screen
python3 livestream.py 
exit
ls
cd Livestream/
ls
screen
screen -r
cd Livestream/
python3 livestream.py 
sudo reboot
screen -r
cd Livestream/
screen
screen -r
python3 livestream.py 
cd Livestream/
ls
screen
nano livestream.py 
screen -r
scree -r
screen -r
ls
screen -r
sudo reboot
ls
screen -r
screen
screen -r
screen
screen -r
cd Livestream/
nano livestream.py 
screen -r
nano livestream.py 
screen -r
nano livestream.py 
screen -r
nano livestream.py 
screen -r
nano livestream.py 
screen -r
nano livestream.py 
screen -r
nano livestream.py 
screen -r
nano livestream.py 
screen -r
ls
cd Livestream/
ls
python3 livestream.py 
sudo shutdown now
python3 livestream.py 
sudo shutdown now
ls
cd Livestream/
ls
screen
screen -r
python3 livestream.py 
ls
cd Livestream/
ls
screen
sudo reboot
exit
screen
screen -r
screen 
sudo shutdown now
cd Livestream/
python3 livestream.py 
test
cd Livestream/
ls
python3 livestream.py 
gst-inspect1.0
gst-inspect-1.0
gst-inspect-1.0 nvarguscamerasrc
python3 livestream.py 
sudo shutdown now
htop
nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 
! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" 
! nvvidconv 
! capsfilter caps="video/x-raw, width=(int)2560, height=(int)1440, format=(string)RGBA, framerate=(fraction)25/1" 
! gstoverlaycairo name=overlay 
! tee name=t 
clear
nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 
! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" 
! tee name=t 
clear
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 
! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" 
! tee name=t 
clear
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 !  capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" !  tee name=t !  t. !  queue !  jpegenc !  multipartmux!  tcpserversink port=3001 !  t. !  queue !  nvvidconv !  capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" !  omxh264enc bitrate=9500000 control-rate=variable !  h264parse !  queue !  flvmux name=muxer alsasrc device=hw:2 !  audioconvert !  audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman !  audioamplify amplification=2.5 clipping-method=wrap-positive !  audioconvert !  audioresample !  capsfilter caps="audio/x-raw,rate=48000" !  queue !  voaacenc bitrate=128000 !  aacparse !  queue !  muxer. muxer. !  rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs"
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 !  capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" !  tee name=t !  t. !  queue !  jpegenc !  multipartmux!  tcpserversink port=3001 !  t. !  queue !  nvvidconv !  capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" !  omxh264enc bitrate=9500000 control-rate=variable !  h264parse !  queue !  flvmux name=muxer alsasrc device=hw:2 !  audioconvert !  audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman !  audioamplify amplification=2.5 clipping-method=wrap-positive !  audioconvert !  audioresample !  capsfilter caps="audio/x-raw,rate=48000" !  queue !  voaacenc bitrate=128000 !  aacparse !  queue !  muxer. muxer. !  rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs"
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=false name=nvarguscamerasrc0 !  "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" !  tee name=t !  t. !  queue !  jpegenc !  multipartmux!  tcpserversink port=3001 !  t. !  queue !  nvvidconv !  "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" !  omxh264enc bitrate=9500000 control-rate=variable !  h264parse !  queue !  flvmux name=muxer alsasrc device=hw:2 !  audioconvert !  audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman !  audioamplify amplification=2.5 clipping-method=wrap-positive !  audioconvert !  audioresample !  capsfilter caps="audio/x-raw,rate=48000" !  queue !  voaacenc bitrate=128000 !  aacparse !  queue !  muxer. muxer. !  rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs"
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=false name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! tee name=t ! t. ! queue ! jpegenc ! multipartmux! tcpserversink port=3001 ! t. ! queue ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs"
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=false name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! tee name=t ! t. ! queue ! jpegenc ! multipartmux! tcpserversink port=3001 ! t. ! queue ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" -e
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=false name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs"
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=false name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! tee name=t t. ! queue ! jpegenc ! multipartmux! tcpserversink port=3001 t. ! queue ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs"
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=false name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! tee name=t t. ! queue ! ffmpegcolorspace ! jpegenc ! multipartmux! tcpserversink port=3001 t. ! queue ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs"
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=false name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! tee name=t t. ! queue ! multipartmux! tcpserversink port=3001 t. ! queue ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs"
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! tee name=t t. ! queue ! nvjpegenc ! multipartmux! tcpserversink port=3001 t. ! queue ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs"
iwconfig
ipconfig
ifconfig
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! tee name=t t. ! queue ! nvjpegenc ! multipartmux! tcpserversink port=3001 t. ! queue ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs"
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! tee name=t t. ! queue ! nvjpegenc ! multipartmux! tcpserversink host=192.168.0.111 port=3001 t. ! queue ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs"
htop
sudo shutdown now
htop
69hguz
gst-inspect-1.0 udpsink
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs"
gst-inspect-1.0 udpsink 
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! tee name=t t. ! queue ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs"
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! tee name=t t. ! queue ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! udpsink host=0.0.0.0 port=3001 
gst-inspect-1.0 rtph264pay 
gst-inspect-1.0 mpegtsmux 
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! mpegtsmux name=muxer2 ! udpsink host=0.0.0.0 port=3001
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! mpegtsmux name=muxer ! tcpserversink host=0.0.0.0 port=3001
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! mpegtsmux name=muxer2 ! tcpserversink host=0.0.0.0 port=3001
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! tee name=t t. ! queue ! theoraenc ! oggmux ! tcpserversink host=0.0.0.0 port=3001 t. ! queue ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs"
gst-inspect-1.0 theoraenc
gst-inspect-1.0 nvvidconv
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! tee name=t t. ! queue ! nvvidconv ! theoraenc ! oggmux ! tcpserversink host=0.0.0.0 port=3001 t. ! queue ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs"
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! tee name=t t. ! queue ! nvjpegenc ! multipartmux ! tcpserversink host=0.0.0.0 port=3001 t. ! queue ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs"
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! tee name=t t. ! queue ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs"
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! tee name=t t. ! queue ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! rtph264pay config-interval=10 pt=96 ! udpsink host=0.0.0.0 port=3001
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! rtph264pay config-interval=10 pt=96 ! udpsink host=0.0.0.0 port=3001
clear
gst-launch-1.0 videotestsrc ! vtenc_h264 ! rtph264pay config-interval=10 pt=96 ! udpsink host=0.0.0.0 port=3001
clear
gst-launch-1.0 videotestsrc ! omxh264enc ! rtph264pay config-interval=10 pt=96 ! udpsink host=0.0.0.0 port=3001
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 videotestsrc ! omxh264enc ! rtph264pay config-interval=10 pt=96 ! udpsink host=192.168.0.18 port=3001
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 videotestsrc ! omxh264enc ! rtph264pay config-interval=10 pt=96 ! udpsink host=192.168.0.18 port=5000
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 videotestsrc ! omxh264enc ! rtph264pay send-config=true config-interval=10 pt=96 ! udpsink host=192.168.0.18 port=5000
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 videotestsrc ! omxh264enc ! rtph264pay config-interval=10 pt=96 ! udpsink host=192.168.0.18 port=5000
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 videotestsrc ! omxh264enc ! rtph264pay config-interval=10 pt=96 ! udpsink host=0.0.0.0 port=5000
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 -vv -e autovideosrc ! queue ! omxh264enc ! h264parse ! mpegtsmux ! rtpmp2tpay ! udpsink host=127.0.0.1 port=5004
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 -vv -e autovideosrc ! queue ! omxh264enc ! h264parse ! mpegtsmux ! rtpmp2tpay ! udpsink host=0.0.0.0 port=5004
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 -vv -e videotestsrc ! queue ! omxh264enc ! h264parse ! mpegtsmux ! rtpmp2tpay ! udpsink host=0.0.0.0 port=5004
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! h264parse ! mpegtsmux ! rtpmp2tpay ! udpsink host=0.0.0.0 port=5004
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! h264parse ! mpegtsmux ! rtpmp2tpay ! udpsink host=192.168.0.18 port=5004
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 -vv -e nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! h264parse ! mpegtsmux ! rtpmp2tpay ! udpsink host=192.168.0.18 port=5004
cleat
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! h264parse ! mpegtsmux ! rtpmp2tpay ! udpsink host=192.168.0.18 port=5004 -v
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! h264parse ! rtph264pay ! udpsink host=192.168.0.18 port=5004 -v
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! h264parse ! mpegtsmux ! rtpmp2tpay ! udpsink host=192.168.0.18 port=5004 -v
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.0.18 port=5004 -v
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.0.18 port=5004 -v
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=0.0.0.0 port=3001 -v
cleart
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! rtph264pay config-interval=1 pt=96 ! udpsink host=0.0.0.0 port=3001
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.0.103 port=3001 sync=false async=false
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! rtph264pay config-interval=1 pt=98 ! udpsink host=0.0.0.0 port=3001 -v
gst-inspect-1.0 mpegtsmux
gst-inspect-1.0 rtpmp2tpay
gst-inspect-1.0 h264parse
htop
gst-inspect-1.0 rtmpsink
nvvidconv
gst-inspect-1.0 nvvidconv
htop
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! rtph264pay config-interval=1 pt=98 ! udpsink host=255.255.255.255 port=3001
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! rtph264pay config-interval=1 pt=98 ! udpsink host=192.168.0.103 port=3001
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.0.103 port=5000 -v
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.0.255 port=5000
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! rtph264pay config-interval=1 pt=96 ! udpsink host=0.0.0.0 port=5000
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! rtph264pay config-interval=1 pt=96 ! udpsink host=255.255.255.255 port=5000
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! mpegtsmux name=muxer2 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 -v
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! mpegtsmux name=muxer2 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 -v
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! h264parse ! mpegtsmux ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 -v
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! h264parse ! mpegtsmux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! h264parse config-interval=1 ! mpegtsmux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! h264parse config-interval=-1 ! mpegtsmux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000
sudo shutdown now
gst-inspect-1.0 MpegTsMux
gst-inspect-1.0 mpegtsmux
clear
gst-inspect-1.0 mpegtsmux
gst-inspect-1.0 flvmux
clear
gst-inspect-1.0 mpegtsmux
gst-inspect-1.0 flvmux
gst-inspect-1.0 rndbuffersize
gst-inspect-1.0 rtmpsink
ls
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! h264parse config-interval=-1 ! mpegtsmux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 -v
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! h264parse config-interval=-1 ! mpegtsmux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 -v
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=v v. ! queue ! flvmux name=muxerv alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! tee name=a a. ! queue ! muxera. muxera. a. ! queue ! muxerv. muxerv. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" v. ! queue ! h264parse config-interval=-1 ! mpegtsmux alignment=7 name=muxera ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=v v. ! queue ! flvmux name=muxerv 
! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" v. ! queue ! h264parse config-interval=-1 
! mpegtsmux alignment=7 name=muxera 
! rndbuffersize max=1316 min=1316 
! rtpmp2tpay 
! udpsink host=255.255.255.255 port=5000 alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! tee name=a a. ! queue ! muxera. muxera. a. ! queue \
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=v v. ! queue ! flvmux name=muxerv 
! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" v. ! queue ! h264parse config-interval=-1 ! mpegtsmux alignment=7 name=muxera \ 
! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! tee name=a a. ! queue ! muxera. muxera. a. ! queue \
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=v v. ! queue ! flvmux name=muxerv ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" v. ! queue ! h264parse config-interval=-1 ! mpegtsmux alignment=7 name=muxera \ 
! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! tee name=a a. ! queue ! muxera. muxera. a. ! queue \
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=v v. ! queue ! flvmux name=muxerv ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" \v. ! queue ! h264parse config-interval=-1 ! mpegtsmux name=muxera alignment=7 \ 
! rndbuffersize max=1316 min=1316 ! rtpmp2tpay \
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=v v. ! queue ! flvmux name=muxerv ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" v. ! queue ! h264parse config-interval=-1 ! mpegtsmux name=muxera alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! tee name=a a. ! queue ! muxera. muxera. a. ! queue ! muxerv. muxerv.
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! tee name=audiotee 
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse config-interval=-1 ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! tee name=audiotee ! queue ! videotee. audiotee. ! flvmux name=muxer ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" ! queue ! videotee. audiotee. ! mpegtsmux name=muxerb alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse config-interval=-1 ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! tee name=audiotee videotee.
! queue audiotee. ! queue ! flvmux name=muxer ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" videotee.
! queue audiotee. ! queue ! mpegtsmux name=muxerb alignment=7 ! muxerb. muxerb. ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay \
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse config-interval=-1 ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! tee name=audiotee videotee. ! queue audiotee. ! queue ! flvmux name=muxer ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" videotee. ! queue audiotee. ! queue ! mpegtsmux name=muxerb alignment=7 ! muxerb. muxerb. ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse config-interval=-1 ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! tee name=audiotee videotee. ! queue audiotee. ! queue ! flvmux name=muxer ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" videotee. ! queue audiotee. ! queue ! mpegtsmux name=muxerb alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse config-interval=-1 ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! tee name=audiotee videotee. audiotee.! queue ! flvmux name=muxer ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" videotee. audiotee.! queue ! mpegtsmux name=muxerb alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse config-interval=-1 ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! flvMux. audiotee. ! queue ! mp2tMux. videotee. ! queue ! flvMux. videotee. ! queue ! mp2tMux.
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse config-interval=-1 ! queue ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! flvMux. audiotee. ! queue ! mp2tMux. videotee. ! queue ! flvMux. videotee. ! queue ! mp2tMux.
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse config-interval=-1 ! queue ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! aacparse ! queue ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! flvMux. audiotee. ! queue ! mp2tMux. videotee. ! queue ! flvMux. videotee. ! queue ! mp2tMux.
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse config-interval=-1 ! queue ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! aacparse ! queue ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! flvMux. audiotee. ! queue ! mp2tMux. videotee. ! queue ! flvMux. videotee. ! queue ! mp2tMux. -v -e
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse ! tee name=t t. ! queue ! flvmux name=muxer alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! queue ! voaacenc bitrate=128000 ! aacparse ! queue ! muxer. muxer. ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" t. ! queue ! h264parse config-interval=-1 ! mpegtsmux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse config-interval=-1 ! queue ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! aacparse ! queue ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! flvMux. audiotee. ! queue ! mp2tMux. videotee. ! queue ! flvMux. videotee. ! queue ! mp2tMux. -v
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable \ 
! "video/x-h264, profile=(string)baseline, width=(int)2560, height=(int)1440, framerate=(fraction)25/1" ! h264parse config-interval=-1 ! queue ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! aacparse ! queue ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! flvMux. audiotee. ! queue ! mp2tMux. videotee. ! queue ! flvMux. videotee. ! queue ! mp2tMux. -v
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! "video/x-h264, profile=(string)baseline, width=(int)2560, height=(int)1440, framerate=(fraction)25/1" ! h264parse config-interval=-1 ! queue ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! aacparse ! queue ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! flvMux. audiotee. ! queue ! mp2tMux. videotee. ! queue ! flvMux. videotee. ! queue ! mp2tMux. -v 
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! "video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse config-interval=-1 ! queue ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! aacparse ! queue ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! flvMux. videotee. ! queue ! flvMux.
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse config-interval=-1 ! capsfilter caps="video/x-h264, width=(int)2560, height=(int)1440, alignment=au, stream-format=avc, framerate=(fraction)25/1" ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! aacparse ! capsfilter caps="audio/mpeg, rate=48000" ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! flvMux. videotee. ! queue ! flvMux. audiotee. ! queue ! mp2tMux. videotee. ! queue ! mp2tMux. -v
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse config-interval=-1 ! capsfilter caps="video/x-h264, width=(int)2560, height=(int)1440, alignment=au, stream-format=avc, framerate=(fraction)25/1" ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! aacparse ! capsfilter caps="audio/mpeg, rate=48000, mpegversion=(int)4, stream-format=raw" ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! flvMux. videotee. ! queue ! flvMux. audiotee. ! queue ! mp2tMux. videotee. ! queue ! mp2tMux. -v
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse config-interval=-1 ! capsfilter caps="video/x-h264, width=(int)2560, height=(int)1440, alignment=au, stream-format=avc, framerate=(fraction)25/1" ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! aacparse ! capsfilter caps="audio/mpeg, rate=48000, mpegversion=(int)4, stream-format=raw" ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! flvMux. videotee. ! queue ! flvMux. audiotee. ! queue ! mp2tMux. videotee. ! queue ! mp2tMux. -v -e
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! h264parse config-interval=-1 ! capsfilter caps="video/x-h264, width=(int)2560, height=(int)1440, alignment=au, stream-format=avc, framerate=(fraction)25/1" ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! aacparse ! capsfilter caps="audio/mpeg, rate=48000, mpegversion=(int)4, stream-format=raw" ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! flvMux. videotee. ! queue ! flvMux.
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rndbuffersize max=1316 min=1316 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux. -v -e
clear
htop
sudo systemctl set-default multi-user.target
sudo reboot
ls
clear
ifconfig
htop
gst-inspect-1.0
cd Livestream/
ls
python3 livestream.py 
sudo reboot
ls
htop
sudo reboot
gst-inspect-1.0 webrtcdsp
gst-inspect-1.0 audiowsincband
ifconfig
dpkg -l | grep gstreamer
gst-launch-1.0 --gst-version
gst-instpect-1.0 webrtcdsp
gst-inspect-1.0 webrtcdsp
gst-inspect-1.0 alsasrc
gst-inspect-1.0 webrtcdsp
audio/x-raw
clear
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! capsfilter caps="audio/x-raw,format=(string)S16LE,rate=48000" ! webrtcdsp ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! capsfilter caps="audio/x-raw,format=(string)S16LE,rate=48000" ! webrtcdsp ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! capsfilter caps="audio/x-raw,format=(string)S16LE,rate=48000" ! webrtcdsp ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! capsfilter caps="audio/x-raw,format=(string)S16LE,rate=48000" ! webrtcdsp ! webrtcechoprobe ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
clear
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! capsfilter caps="audio/x-raw,format=(string)S16LE,rate=48000" ! webrtcdsp noise-suppression-level=3 echo-cancel=false ! webrtcechoprobe ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! capsfilter caps="audio/x-raw,format=(string)S16LE,rate=48000" ! webrtcdsp noise-suppression-level=3 echo-cancel=false voice-detection=true ! webrtcechoprobe ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! capsfilter caps="audio/x-raw,format=(string)S16LE,rate=48000" ! webrtcdsp noise-suppression-level=3 echo-cancel=false voice-detection=true experimental-agc=true ! webrtcechoprobe ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
clear
GST_DEBUG_DUMP_DOT_DIR=/home/arne gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! capsfilter caps="audio/x-raw,format=(string)S16LE,rate=48000" ! webrtcdsp noise-suppression-level=3 echo-cancel=false voice-detection=true high-pass-filter=false ! webrtcechoprobe ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
clear
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=101 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert noise-shaping=4 ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=900 upper-frequency=8000 length=201 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert noise-shaping=4 ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=201 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert noise-shaping=4 ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=600 upper-frequency=9000 length=201 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert noise-shaping=4 ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=600 upper-frequency=9000 length=21 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert noise-shaping=4 ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=500 upper-frequency=9000 length=21 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert noise-shaping=4 ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=12000 length=21 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert noise-shaping=4 ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 \´
! audioconvert noise-shaping=4 ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
clear
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! audioconvert noise-shaping=4 ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=12000 length=31 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert noise-shaping=4 ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=9000 length=31 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert noise-shaping=4 ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=20000 length=31 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert noise-shaping=4 ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=200 upper-frequency=10000 length=31 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert noise-shaping=4 ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
gst-launch-1.0 nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name=nvarguscamerasrc0 ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! nvvidconv ! capsfilter caps="video/x-raw(memory:NVMM), width=(int)2560, height=(int)1440, format=(string)NV12, framerate=(fraction)25/1" ! omxh264enc bitrate=9500000 control-rate=variable ! tee name=videotee alsasrc device=hw:2 ! audioconvert ! audiowsincband mode=band-pass lower-frequency=300 upper-frequency=12000 length=41 window=blackman ! audioamplify amplification=2.5 clipping-method=wrap-positive ! audioconvert noise-shaping=4 ! audioresample ! capsfilter caps="audio/x-raw,rate=48000" ! voaacenc bitrate=128000 ! tee name=audiotee flvmux name=flvMux ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/rbw6-bq12-1bg9-3pbs" mpegtsmux name=mp2tMux alignment=7 ! rtpmp2tpay ! udpsink host=255.255.255.255 port=5000 audiotee. ! queue ! aacparse ! flvMux. audiotee. ! queue ! aacparse ! mp2tMux. videotee. ! queue ! h264parse ! flvMux. videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.
sudo shutdown now
ls
cd Livestream/
ls
screen
ls
python3 livestream.py 
nano livestream.py 
python3 livestream.py 
sudo shutdown now
arne
sudo shutdown now
ls
cd Livestream/
screen
ls
exit
python3 livestream.py 
screen -r
ls
screen -r 
screen -r 6101
sudo reboot
ls
screen
screen -r
cd Livestream/
ls
screen 
ls
screen -r
python3 livestream.py 
clear
python3 livestream.py 
clear
python3 livestream.py 
sudo reboot
cd Livestream/
ls
nano livestream.py 
ifconfig
nano livestream.py 
python3 livestream.py 
netstat -lt
netstat -ltn
netstat -ltnp
htop
python3 livestream.py 
screen -r
ls
htop
cd Livestream/
nano livestream.
nano livestream.py 
screen
htop
cd Livestream/
ls
python3 livestream.py 
clear
ls
clear
sudo shutdown now
python3 livestream.py 
clear
python3 livestream.py 
cd Livestream/
screen
cd Livestream/
python3 livestream.py 
clear
nano livestream.py 
ifconfig
nano livestream.py 
python3 livestream.py 
nano livestream.py 
python3 livestream.py 
sudo shutdown now
ls
screen
screen -r
scree -r
screen -r
sudo shutdown now
cd Livestream/
python3 livestream.py 
clear
python3 livestream.py 
clear
python3 livestream.py 
sudo sh -c 'echo 255 > /sys/devices/pwm-fan/target_pwm' 
sudo sh -c 'echo 0 > /sys/devices/pwm-fan/target_pwm' 
sudo sh -c 'echo 255 > /sys/devices/pwm-fan/target_pwm' 
sudo /usr/bin/jetson_clocks
sudo sh -c 'echo 255 > /sys/devices/pwm-fan/target_pwm'
sudo sh -c 'echo 0 > /sys/devices/pwm-fan/target_pwm' 
sudo sh -c 'echo 255 > /sys/devices/pwm-fan/target_pwm'
sudo /usr/bin/jetson_clocks
sudo shutdown now
screen
screen -r
cd Livestream/
python3 livestream.py 
clear
python3 livestream.py 
sudo reboot
cd Livestream/
python3 livestream.py 
sudo shutdown now
screen
cd Livestream/
ls
screen
jtop
sudo -H pip install jetson-stats
sudo -H pip3 install jetson-stats
jtop
sudo jtop
nano livestream.py 
python3 livestream.py 
exit
jtop
screen -r
cd Livestream/
nano livestream.py 
screen -r
jtop
screen -r
ls
jtop
ls
clear
gst-inspect-1.0 dewarp
dpkg -l | grep gstreamer
clear
dpkg -l | grep gstreamer
gst-inspect-1.0 dewarp
gst-inspect-1.0 circle
gst-inspect-1.0 dewarp
gst-inspect-1.0 edgedetect
gst-inspect-1.0 nvdewarp
gst-inspect-1.0 gst-nvdewarp
gst-inspect-1.0 nvvidconv
nvdewarp
gst-inspect-1.0 nvdewarp
clear
sudo shutdown now
ifconfig
sudo shutdown now
hostname
hostname livestream_nano_1
hostname livestream-nano-1
sudo hostname livestream-nano-1
hostname
sudo reboot
hostname
sudo hostnamectl set-hostname livestream-nano-1
hostname
sudo reboot
cut -d: -f1 /etc/passwd
cd Livestream/
ls
python livestream.py 
python3 livestream.py 
clear
python3 livestream.py 
nano livestream.
nano livestream.py 
python3 livestream.py 
sudo shutdown now
sudo hostnamectl livestream-nano-2
sudo hostnamectl set-hostname livestream-nano-2
hostname
cd Livestream/
pythn
python3 livestream.py 
ifconfig
sudo shutdown now
cd Livestream/
rm -r preview.sh 
cd /etc/
su - arne -c "/usr/bin/screen -dmS test bash -c '/home/arne/Livestream/livestream.sh'"
screen -r
su - arne -c "/usr/bin/screen -dmS test bash -c '/home/arne/Livestream/livestream.sh'"
screen -r
gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM),width=3820, height=2464, framerate=21/1, format=NV12' ! nvvidconv flip-method=0 ! 'video/x-raw,width=960, height=616' ! nvvidconv ! nvegltransform ! nveglglessink -e
clear
gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM),width=3820, height=2464, framerate=21/1, format=NV12' ! nvvidconv flip-method=0 ! 'video/x-raw,width=960, height=616' ! nvvidconv ! nvegltransform ! fakesink
gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM),width=3820, height=2464, framerate=21/1, format=NV12' ! nvvidconv flip-method=0 ! 'video/x-raw,width=960, height=616' ! nvvidconv ! fakesink
clear
sudo reboot
clear
gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM),width=3820, height=2464, framerate=21/1, format=NV12' ! nvvidconv flip-method=0 ! 'video/x-raw,width=960, height=616' ! nvvidconv ! fakesink
cd /etc/
su - arne -c "/usr/bin/screen -dmS test bash -c '/home/arne/Livestream/livestream.sh'"
screen -r
su - arne -c "/usr/bin/screen -dmS test bash -c '/home/arne/Livestream/livestream.sh'"
screen -r
/home/arne/Livestream/livestream.sh
cd ~/Livestream/
python3 livestream.py & echo $!
kill 6422
htop
clear
ls
/home/arne/Livestream/livestream.sh
sudo reboot
/home/arne/Livestream/livestream.sh
clear
cd /etc/init
ls
cd ..
ls
crontab -e
sudo reboot
screen -r
crontab -e
sudo reboot
screen -r
jtop
sudo nano /etc/network/interfaces
sudo reboot
screen -r
sudo reboot
ifconfig
screen -r
sudo shutdown now
crontab -l
crontab -e
(crontab -l ; echo "@reboot /usr/bin/screen -dmS test bash -c '/home/arne/Livestream/livestream.sh'") | crontab -
crontab -l
clear
sudo bash -c 'cat > /etc/network/interfaces << "EOF"
# interfaces(5) file used by ifup(8) and ifdown(8)
# Include files from /etc/network/interfaces.d:
source-directory /etc/network/interfaces.d 

auto wlan0 
allow-hotplug wlan0 
iface wlan0 inet static 
address 10.0.12.234 
netmask 255.255.0.0
wpa-essid SPL_FIELD_2ghz_A
#wpa-essid SPL_FIELD_2ghz_B
#wpa-essid SPL_FIELD_2ghz_C
#wpa-essid SPL_FIELD_2ghz_D
#wpa-essid SPL_FIELD_2ghz_E


wpa-psk Nao?!Nao?!
#wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf

auto eth0 
iface eth0 inet dhcp

auto eth1
iface eth1 inet static
address 192.168.31.3
netmask 255.255.255.0

iface default inet dhcp
EOF'lear
clear
sudo bash -c 'cat > /etc/network/interfaces << "EOF"
# interfaces(5) file used by ifup(8) and ifdown(8)
# Include files from /etc/network/interfaces.d:
source-directory /etc/network/interfaces.d 

auto wlan0 
allow-hotplug wlan0 
iface wlan0 inet static 
address 10.0.12.234 
netmask 255.255.0.0
#wpa-essid SPL_FIELD_2ghz_A
wpa-essid SPL_FIELD_2ghz_B
#wpa-essid SPL_FIELD_2ghz_C
#wpa-essid SPL_FIELD_2ghz_D
#wpa-essid SPL_FIELD_2ghz_E


wpa-psk Nao?!Nao?!
#wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf

auto eth0 
iface eth0 inet dhcp

auto eth1
iface eth1 inet static
address 192.168.31.3
netmask 255.255.255.0

iface default inet dhcp
EOF'
sudo nano /etc/network/interfaces
clear
sudo shutdown now
ls
screen -r
sudo shutdown now
screen .r
screen -r
sudo reboot
screen -r
sudo shutdown now
sudo reboot
screen -r
sudo shutdown now
screen -r
clear
sudo reboot
screen -r
clear
sudo reboot
screen -r
clear
(echo "@reboot /usr/bin/screen -dmS test -L bash -c '/home/arne/Livestream/livestream.sh'") | crontab -
crontab -l
/home/arne/Livestream/livestream.sh
clear
sudo reboot
screen -r
sudo shutdown now
screen -r
(echo "@reboot /usr/bin/screen -dmS test -L bash -c '/home/arne/Livestream/livestream.sh'") | crontab -
crontab -l
sudo shutdown now
screen -r
(echo "@reboot /usr/bin/screen -dmS test -L bash -c '/home/arne/Livestream/livestream.sh'") | crontab -
crontab -l
sudo bash -c 'cat > /etc/network/interfaces << "EOF"
# interfaces(5) file used by ifup(8) and ifdown(8)
# Include files from /etc/network/interfaces.d:
source-directory /etc/network/interfaces.d 

auto wlan0 
allow-hotplug wlan0 
iface wlan0 inet static 
address 10.0.12.234 
netmask 255.255.0.0
#wpa-essid SPL_FIELD_2ghz_A
wpa-essid SPL_FIELD_2ghz_B
#wpa-essid SPL_FIELD_2ghz_C
#wpa-essid SPL_FIELD_2ghz_D
#wpa-essid SPL_FIELD_2ghz_E


wpa-psk Nao?!Nao?!
#wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf

auto eth0 
iface eth0 inet dhcp

auto eth1
iface eth1 inet static
address 192.168.31.3
netmask 255.255.255.0

iface default inet dhcp
EOF'
sudo shutdown now
screen -r
pip3 install psutil
cd Livestream/
./forever livestream.py
sudo shutdown now
screen -r
exit
