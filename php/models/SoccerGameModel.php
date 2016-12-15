<?php
/**
 * Description of SoccerGameLogModel
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class SoccerGameModel {
    
    private $_directory;
    /* @var $_date DateTimeImmutable */
    private $_date;
    private $_event;
    private $_opponent;
    private $_logs;
    
    public function __construct($date, $event, $opp, $dir) {
        $this->_date = new DateTimeImmutable($date);
        $this->_event = $event;
        $this->_opponent = $opp;
        $this->_directory = $dir;
    }

    /**
     * 
     * @param String $file
     * @return \SoccerGameModel
     */
    public static function checkAndCreate($file) {
        if(is_dir($file) // has to be a directory
            && preg_match('/.*\/?(\d{4}-\d{2}-\d{2})-(\w+)-(\w+)/', $file, $parts) === 1 // directory must look like "yyyy-mm-dd-event-opponent"
            && !empty(glob($file.DIRECTORY_SEPARATOR.'*half*.{MP,mp}4',GLOB_BRACE)) // there should be at least one mp4 half video file
            && !empty(glob($file.DIRECTORY_SEPARATOR.'*half*',GLOB_ONLYDIR)) // and a half time directory
        ) {
            return new SoccerGameModel($parts[1], $parts[2], $parts[3], $file);
        }
        return NULL;
    }
    
    public function getDate($format = 'd.m.Y') {
        return $this->_date->format($format);
    }
    
    public function getOpponent() {
        return $this->_opponent;
    }
    
    public function getEvent() {
        return $this->_event;
    }
    
    public function getDirectory() {
        return $this->_directory;
    }
    
    public function getVideos() {
        return glob($this->_directory.DIRECTORY_SEPARATOR.'*half*.{MP,mp}4',GLOB_BRACE);
    }
    
    public function getLogs() {
        if ($this->_logs === NULL) {
            $this->_logs = [];
            $dirs = glob($this->_directory . DIRECTORY_SEPARATOR . '*half*', GLOB_ONLYDIR);
            
            foreach ($dirs as $dir) {
                $a = scandir($dir);
                foreach ($a as $key => $value) {
                    if ($value == "." || $value == "..") {
                        continue;
                    }

                    $file_path = $dir . "/" . $value;
                
                    //is a log
                    if (is_dir($file_path)) {
                        $json_files = glob($file_path . DIRECTORY_SEPARATOR . '*.json', GLOB_BRACE);
                        $json_files = array_combine(array_map(function($i)use($file_path) {
                            $i = str_replace($file_path . DIRECTORY_SEPARATOR, '', $i);
                                    return ($p = strpos($i, "-")) !== FALSE ? substr($i, $p + 1, -5) : 'blank';
                                }, $json_files), $json_files);
//                        \app\VarDumper::dump($json_files);

                        //$json_path = $file_path . "/labels.json";
                        $sync_data = $file_path . "/game.log.videoanalyzer.properties";

                        //if(!is_file($json_path)) {
                        if (!array_key_exists("blank", $json_files)) {
//                        $errors = $errors . "ERROR: no json file in " . $file_path . "\n";
                            //echo "ERROR: no json file in ".$file_path."\n";
                        } else if (!is_file($sync_data)) {
//                        $errors = $errors . "ERROR: no sync data in " . $file_path . "\n";
                            //echo "ERROR: no sync data in ".$file_path."\n";
                        } else {
                            $this->_logs[] = new SoccerGameLogModel($json_files, $sync_data);
                        }
                    }
                }
            }
        }
        return $this->_logs;
    }

}
