<?php
require_once 'Config.php';

class NaoLog
{
    /** @var bool */
    private $is_valid = false;
    /** @var string */
    private $id;
    /** @var string */
    private $path;
    /** @var int */
    private $player;
    /** @var string */
    private $head;
    /** @var string */
    private $body;
    /** @var string */
    private $sync_file_old;
    /** @var string */
    private $info_file;
    /** @var string */
    private $info = null;
    /** @var array */
    private $labels = [];
    /** @var array */
    private $errors = [];

    function __construct(SplFileInfo $path, $game_path, $data_dir) {
        $this->is_valid = preg_match('/'.Config::l('regex').'/', $path->getFilename(), $matches) === 1;
        if ($this->is_valid && $path->isReadable()) {
            $this->path = $path->getRealPath();
            $this->id = sha1($this->path);
            $this->player = intval($matches[1]);
            $this->head = $matches[2];
            $this->body = $matches[3];

            $data_path = $game_path . DIRECTORY_SEPARATOR . $data_dir;
            if(is_dir($game_path) && is_dir($data_path)) {
                $log_data_path = $data_path . DIRECTORY_SEPARATOR . $path->getFilename();
                if(is_dir($log_data_path)) {

                    $log_info_file = $log_data_path . DIRECTORY_SEPARATOR . Config::l('info');
                    if(is_file($log_info_file)) {
                        $this->info_file = $log_info_file;
                        foreach (glob($log_data_path . DIRECTORY_SEPARATOR . implode('*',Config::l('labels'))) as $label) {
                            // extract label name
                            if(preg_match('/'.Config::l('labels')[0].'-(.+)'.Config::l('labels')[1].'/', basename($label), $matches) === 1) {
                                $this->labels[$matches[1]] = $label;
                            }
                        }
                    } else {
                        $this->addError('Missing log info file!');
                    }

                } else {
                    $this->addError('Missing data directory!');
                }
            } else {
                $this->addError('Invalid path to meta data!');
            }
        } else {
            $this->addError('Invalid or not readable log path');
        }
    }

    /**
     * @param $msg
     */
    private function addError($msg) {
        $this->errors[] = $msg;
        $this->is_valid = false;
    }

    /**
     * @deprecated
     */
    private function parseOldSync() {
        $log_data_file = dirname($this->info_file) . DIRECTORY_SEPARATOR . Config::l('sync');
        if(is_file($log_data_file)) {
            $this->sync_file_old = $log_data_file;
            $syncings = parse_ini_file($this->sync_file_old);
            // only add missing sync info
            if(!empty($syncings['video-file']) && !isset($this->info['sync'][$syncings['video-file']])) {
                $this->info['sync'][$syncings['video-file']] = [
                    'log' => empty($syncings['sync-time-log'])?0:floatval($syncings['sync-time-log']),
                    'video' => empty($syncings['sync-time-video'])?0:floatval($syncings['sync-time-video'])
                ];
            }
        } else {
            $this->addError('Missing OLD sync file!');
        }
    }

    /**
     * @return array|null
     */
    private function getInfo() {
        if($this->info === null && is_file($this->info_file)) {
            $this->info = json_decode(file_get_contents($this->info_file), true);
        }
        return $this->info;
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

    /**
     * @return string
     */
    public function getId()
    {
        return $this->id;
    }

    /**
     * @return string
     */
    public function getInfoFile()
    {
        return $this->info_file;
    }

    /**
     * @return bool
     */
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
     * @return array
     */
    public function getLabelsName()
    {
        return array_keys($this->labels);
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
     * @return array
     */
    public function getSyncInfo($name)
    {
        if($this->getInfo() !== null && isset($this->getInfo()['sync'][$name])) {
            return $this->getInfo()['sync'][$name];
        }
        return [ 'log' => 0.0, 'video' => 0.0 ];
    }

    /**
     * Returns the event data as JSON string.
     * @return string
     */
    public function getLabelsAsJson() {
        // add the label entry if not already set
        if(!isset($this->info['labels'])) { $this->info['labels'] = []; }
        // add all labels
        foreach ($this->labels as $key => $value) {
            $this->info['labels'][$key] = json_decode(file_get_contents($value), true);
        }
        return json_encode($this->info);
    }

    /**
     * Saves the given labels as json file under the given name.
     * If saving was successfull, 'true' is returned, otherwise an error string is returned.
     * 
     * @param $name the name of the json label file
     * @param $labels the labels to save
     * @return true|string
     */
    public function saveLabels($name, $labels) {
        // prepate the save path
        $path = dirname($this->info_file) . DIRECTORY_SEPARATOR . Config::l('labels')[0] . '-' . $name . Config::l('labels')[1];
        if ( @file_put_contents($path, $labels) === FALSE ) {
            return "ERROR: writing labels file!";
        }
        return true;
    }
}