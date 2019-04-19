example usage:

1. This will produce a file containing the field lines as 2d points with the name "./rc18/htwk-naoth-h1-combined.txt".

python extract_field_lines.py "./data/rc18-htwk-naoth-h1-background.jpg"

2. this line will try to estimate the position of the camera in relaton to the field. 
At the moment the results of the calculations are only visualized.
NOTE: for the alighnment to work the "starting" position of the camera has to be "good enough".

python calculate_camera_parameters.py "./data/rc18-htwk-naoth-h1.txt"


