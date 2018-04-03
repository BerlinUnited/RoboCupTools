# RoboCupTools
Tools for collection, organization and processing of RoboCup related data.
https://robocup.tools


## GcTeamcommConverter (qick use)
This tool converts the binary logfiles of the GameController to readable json files.
* open the directory `RoboCupTools/GcTeamcommConverter` with NetBeans and compile it with clean and build
* enter the directory `RoboCupTools/GcTeamcommConverter/dist`
* run `java -jar GcTeamcommConverter.jar --tc <path to your logfile, or directory with logfiles>`.
* the resulting json file will be saved next to your original logfile

## WebGameAnalyzer
This is a set of tools visualizing the teamcomm logfiles from different perspectives.
The used logfiles have to be in json format as exported by **GcTeamcommConverter**. 
Open one of the following viewers directly in your browser and select a json file.

* d3_ball_slider.html
* d3_ballmap.html
* d3_heatmap.html
* d3_timeline.html
