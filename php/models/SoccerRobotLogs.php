<?php
namespace app\models;

/**
 * Description of SoccerRobotLogs
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class SoccerRobotLogs
{
    public static $regex_json = '/labels(-(?P<id>\S+))?.json/';
    
    public $id;
    public $errors = [];
    public $labels = [];
    public $sync = '';
    public $video_offset = 0;
    public $log_offset = 0;

    function __construct($path) {
        //is a (log) directory
        if (is_dir($path)) {
            // using directory name as id
            $this->id = basename($path);
            // iterate over Nao directories
            foreach (glob($path . DIRECTORY_SEPARATOR . 'labels*.json', GLOB_BRACE) as $file) {
                if(preg_match(static::$regex_json, $file, $match)) {
                    // sets the label json file with the id
                    $this->labels[(isset($match['id']))?$match['id']:'new'] = $file;
                }
            }
            // set error if "labels.json" is missing
            if(!isset($this->labels['new'])) { $this->errors[] = "ERROR: no json file in " . $path; }
            
            // check & read sync file
            $this->sync = $path . "/game.log.videoanalyzer.properties";
            if (!is_file($this->sync) || !$this->parse_sync()) {
                $this->errors[] = "ERROR: no sync data in " . $path;
            }
        } else {
            $this->errors[] = "ERROR: not a directory '" . $path . "'";
        }
    }
    
    public function parse_sync() {
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
        // INFO: could return "FALSE" to indicate an ERROR!
        return TRUE;
    }

    public function isValid() {
        return empty($this->errors);
    }
    
    public function getLabels() {
        return array_keys($this->labels);
    }
    
    public function getLabelFile($label) {
        return isset($this->labels[$label]) ? $this->labels[$label] : NULL;
    }
}
