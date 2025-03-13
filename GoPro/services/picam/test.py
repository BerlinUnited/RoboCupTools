from picamera2.encoders import H264Encoder, Quality
from picamera2 import Picamera2, Preview
import time

picam2 = Picamera2()


picam2.start_preview(Preview.NULL)
encoder = H264Encoder()
picam2.configure(picam2.create_video_configuration(raw={"size":(1640,1232)},main={"size": (1640, 1232)}))

picam2.start_recording(encoder, "test.h264", quality=Quality.VERY_HIGH, pts='timestamp.txt')

time.sleep(10)
picam2.stop_recording()