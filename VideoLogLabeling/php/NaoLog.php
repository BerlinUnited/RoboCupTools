<?php
require_once 'Config.php';

class NaoLog
{
    /** @var bool */
    private $is_valid = false;
    /** @var string */
    private $path;
    /** @var int */
    private $player;
    /** @var string */
    private $head;
    /** @var string */
    private $body;
    /** @var string */
    private $sync_file;
    /** @var array */
    private $sync_info = [];
    /** @var string */
    private $events;
    /** @var array */
    private $labels = [];
    /** @var array */
    private $errors = [];

    function __construct(SplFileInfo $path, $game_path, $data_dir) {
        $this->is_valid = preg_match(Config::l('regex'), $path->getFilename(), $matches) === 1;
        if ($this->is_valid) {
            $this->path = $path->getRealPath();
            $this->player = intval($matches[1]);
            $this->head = $matches[2];
            $this->body = $matches[3];

            $data_path = $game_path . DIRECTORY_SEPARATOR . $data_dir;
            if(is_dir($game_path) && is_dir($data_path)) {
                $log_data_path = $data_path . DIRECTORY_SEPARATOR . $path->getFilename();
                if(is_dir($log_data_path)) {
                    $log_data_file = $log_data_path . DIRECTORY_SEPARATOR . Config::l('sync');
                    if(is_file($log_data_file)) {
                        $this->sync_file = $log_data_file;
                        $log_label_file = $log_data_path . DIRECTORY_SEPARATOR . implode('',Config::l('labels'));
                        if(is_file($log_label_file)) {
                            $this->parseSync();
                            $this->events = $log_label_file;
                            foreach (glob($log_data_path . DIRECTORY_SEPARATOR . implode('*',Config::l('labels'))) as $label) {
                                // skip the base label file
                                if($label === $log_label_file) { continue; }
                                // extract label name
                                if(preg_match('/'.Config::l('labels')[0].'-(.+)'.Config::l('labels')[1].'/', basename($label), $matches) === 1) {
                                    $this->labels[$matches[1]] = $label;
                                }
                            }
                        } else {
                            $this->addError('Missing event json file!');
                        }
                    } else {
                        $this->addError('Missing video sync file!');
                    }
                } else {
                    $this->addError('Missing data directory!');
                }
            } else {
                $this->addError('Invalid path to meta data!');
            }
        }
    }

    private function addError($msg) {
        $this->errors[] = $msg;
        $this->is_valid = false;
    }

    private function parseSync() {
        $lines = file($this->sync_file);
        foreach ($lines as $line_num => $line) {
            if(strcmp(substr($line,0,16),'sync-time-video=') == 0) {
                $this->sync_info['video_offset'] = substr($line,16);
            } elseif(strcmp(substr($line,0,14),'sync-time-log=') == 0) {
                $this->sync_info['log_offset'] = substr($line,14);
            } elseif(strcmp(substr($line,0,11),'video-file=') == 0) {
                $this->sync_info['video'] = substr($line,11);
            }
        }
    }

    /**
     * @return bool
     */
    public function isValid()
    {
        return $this->is_valid;
    }

    /**
     * @return bool
     */
    public function hasErrors()
    {
        return count($this->errors) > 0;
    }

    /**
     * @return array
     */
    public function getErrors()
    {
        return $this->errors;
    }

    public function hasLabels() {
        return count($this->labels) > 0;
    }

    /**
     * @return array
     */
    public function getLabels()
    {
        return $this->labels;
    }

    /**
     * @return string
     */
    public function getLabel($name)
    {
        if (array_key_exists($name ,$this->labels)) {
            return $this->labels[$name];
        }
        return null;
    }

    /**
     * @return int
     */
    public function getPlayer()
    {
        return $this->player;
    }

    /**
     * @return mixed|false
     */
    public function getSyncInfo($name)
    {
        if(array_key_exists($name, $this->sync_info)) {
            return $this->sync_info[$name];
        }
        return false;
    }
}