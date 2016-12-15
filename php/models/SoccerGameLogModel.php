<?php

/**
 * Description of SoccerGameLogModel
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class SoccerGameLogModel
{
    public $json = '';
    public $sync = '';
    public $video_offset = 0;
    public $log_offset = 0;

    function __construct($json, $sync) {
        $this->json = $json;
        $this->sync = $sync;
        $this->parse_sync();
    }

    function parse_sync() {
        // TODO: read and parse the file $this->sync
        $lines = file($this->sync);
        foreach ($lines as $line_num => $line) {
            if (strcmp(substr($line, 0, 16), 'sync-time-video=') == 0) {
                //echo substr($line,16) . "<br />\n";
                $this->video_offset = substr($line, 16);
            } elseif (strcmp(substr($line, 0, 14), 'sync-time-log=') == 0) {
                //echo substr($line,14) . "<br />\n";
                $this->log_offset = substr($line, 14);
            }
            /* elseif(strcmp(substr($line,0,11),'video-file=') == 0){
              echo substr($line,11) . "<br />\n";
              } */
        }
        //$this->video_offset = 12.993253731;
        //$this->log_offset = 270.937;
    }

}
