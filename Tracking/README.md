## Locate the Camera relative to the field midpoint

**Step 1: detect the field lines in the image**  
    run `python extract_field_lines.py <path to video file>`

This will produce a file containing the field lines as 2d points with the name "<video filename>.txt".

**Step 2: estimate the camera position**  
    run `python calculate_camera_parameters.py <video filename>.txt`

this line will try to estimate the position of the camera in relation to the field. 
At the moment the results of the calculations are only visualized.

NOTE: for the alignment to work the "starting" position of the camera has to be "good enough".




