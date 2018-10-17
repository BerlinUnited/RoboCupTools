<?php
require_once 'Config.php';
require_once 'NaoLog.php';
require_once 'Video.php';

class Game
{
    private $is_valid = false;
    private $id;
    private $path;
    private $date;
    private $team1;
    private $team2;
    private $half;
    private $event;

    private $logs = [];
    private $videos = [];

    private $errors = [];
    private $warnings = [];

    /**
     * Game constructor.
     *
     * @param SplFileInfo $path
     * @param Event $event
     */
    function __construct(SplFileInfo $path, Event $event) {
        $this->is_valid = preg_match('/'.Config::g('regex').'/', $path->getFilename(), $matches) === 1;
        if ($this->is_valid && $path->isReadable()) {
            $this->path = $path->getRealPath();
            $this->date = DateTimeImmutable::createFromFormat('Y-m-d_H-i-s',$matches[1]);
            $this->team1 = str_replace('_', ' ', $matches[2]);
            $this->team2 = str_replace('_', ' ', $matches[3]);
            $this->half = intval($matches[4]);
            $this->id = sha1($this->path);
            $this->event = $event;

            $this->init();
        } else {
            $this->errors[] = 'Game log path not valid or not readable!';
        }
    }

    /**
     *
     */
    private function init() {
        $path = $this->path . DIRECTORY_SEPARATOR . Config::g('dirs')['nao'];
        if (is_dir($path)) {
            $it = new DirectoryIterator($path);
            foreach($it as $file) {
                if (!$file->isDot() && $file->isDir()) {
                    $log = new NaoLog($file, $this->path, Config::g('dirs')['data']);
                    if ($log->isValid()) {
                        $this->logs[$log->getId()] = $log;
                    } else {
                        foreach ($log->getErrors() as $error) {
                            $this->errors[] = $this->getTeam1() . ' vs. ' . $this->getTeam2() . ', #' . $this->getHalf() . '/' . $log->getPlayer() . ': ' . $error;
                        }
                    }
                }
            }
            uasort($this->logs, function($a, $b){ return $a->getPlayer() - $b->getPlayer(); });
        } else {
            $this->errors[] = 'No log files!';
        }

        // read video infos from video json file
        $path = $this->path . DIRECTORY_SEPARATOR . Config::g('dirs')['data'] . DIRECTORY_SEPARATOR . Config::g('video_file');
        if(is_file($path)) {
            $video_data = json_decode(file_get_contents($path), true);
            if(!empty($video_data)) {
                foreach ($video_data as $name => $value) {
                    $this->videos[$name] = new Video($this, $value);
                }
            }
        }

        // read the "real" video files
        $path = $this->path . DIRECTORY_SEPARATOR . Config::g('dirs')['video'];
        if (is_dir($path)) {
            $it = new DirectoryIterator($path);
            foreach($it as $file) {
                if (!$file->isDot() && $file->isFile() && in_array(strtolower($file->getExtension()),Config::g('video_types'))) {
                    // check if we have this source already
                    foreach ($this->videos as $video) {
                        /* @var Video $video */
                        if ($video->hasSource($file->getFilename())) {
                            // we already have this source as video, skip it
                            continue 2;
                        }
                    }
                    // each video file is assumed to be different from the others
                    if(isset($this->videos[$file->getBasename()])) {
                        $this->videos[$file->getBasename()].addSource($file->getRealPath());
                    } else {
                        $this->videos[$file->getBasename()] = new Video($this, $file->getRealPath());
                    }
                }
            }
        }

        // add error message if no videos are available
        if(empty($this->videos)){
            $this->errors[] = 'No video files!';
        }

        if (is_dir($this->path . DIRECTORY_SEPARATOR . Config::g('dirs')['gc'])) {
            // TODO: read gamecontroller files
        } else {
            $this->warnings[] = 'No gamecontroller files!';
        }
    }

    /**
     * @return string
     */
    public function getPath()
    {
        return $this->path;
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
     * @return DateTimeImmutable
     */
    public function getDate()
    {
        return $this->date;
    }

    /**
     * @return string
     */
    public function getDateString($format='d.m.Y, H:i:s')
    {
        return $this->date->format($format);
    }

    /**
     * @return string
     */
    public function getTeam1()
    {
        return $this->team1;
    }

    /**
     * @return string
     */
    public function getTeam2()
    {
        return $this->team2;
    }

    /**
     * @return int
     */
    public function getHalf()
    {
        return $this->half;
    }

    /**
     * @return array
     */
    public function hasLogs()
    {
        return count($this->logs) > 0;
    }

    /**
     * @return array
     */
    public function getLogs()
    {
        return $this->logs;
    }

    /**
     * @return array
     */
    public function getSize()
    {
        return count($this->logs);
    }

    /**
     * @return Event
     */
    public function getEvent()
    {
        return $this->event;
    }

    /**
     * @return bool
     */
    public function hasVideos()
    {
        return count($this->videos) > 0;
    }

    /**
     * @return array
     */
    public function getVideos()
    {
        return $this->videos;
    }

    /**
     * @return bool
     */
    public function hasLabels() {
        return $this->hasLogs() && array_filter($this->logs, function ($l) { return $l->hasLabels(); });
    }

    /**
     * @return array
     */
    public function getLabels() {
        $result = [];
        foreach ($this->logs as $log) {
            $result = array_merge($result, $log->getLabelsName());
        }
        return array_unique($result);
    }

    /**
     * Returns the label/event data as JSON string.
     * @return string
     */
    public function getLabelsAsJson() {
        $json = '{';
        $keys = array_keys($this->logs);
        for ($i=0; $i < count($keys); $i++) { 
            $json .= '"' . $this->logs[$keys[$i]]->getPlayer() . '": ' . $this->logs[$keys[$i]]->getLabelsAsJson() . ($i === count($keys)-1 ? "\n" : ", \n");
        }
        $json .= '}';
        return $json;
    }

    /**
     * Saves the given labels for each log as json file under the given name.
     * If saving was successfull, 'true' is returned, otherwise an error string is returned.
     *
     * @param $name the name of the json label file
     * @param $labels the labels to save
     * @return true|string
     */
    public function saveLabels($name, $labels) {
        // make sure we got the right format
        if (!is_array($labels)) {
            return 'ERROR: invalid labels data!';
        }
        // replace umlaute & remove invalid characters
        $name = str_replace(["Ä", "Ö", "Ü", "ä", "ö", "ü", "ß"], ["Ae", "Oe", "Ue", "ae", "oe", "ue", "ss"], $name);
        $name = preg_replace(['/\s+/', '/[^a-zA-Z0-9_-]/'], ['-', ''], $name);
        // prevent overwriting existing names
        // TODO: still not 100% save, could still be overwritten!
        if (!isset($_GET['name']) && in_array($name, $this->getLabels())) {
            return 'ERROR: Label name already exists!';
        }
        // iterate through logs
        foreach ($labels as $value) {
            // check each log labels entry
            if (isset($value['id']) && is_string($value['id']) && isset($value['labels']) && is_string($value['labels'])) {
                // is the log id correct
                if (preg_match("/\w+/i", $value['id']) && array_key_exists($value['id'], $this->logs)) {
                    // let the log handle the actual saving
                    $result = $this->logs[$value['id']]->saveLabels($name, $value['labels']);
                    // report errors if there were some
                    if ($result !== true) {
                        return $result;
                    }
                } else {
                    return 'ERROR: invalid log id!';
                }
            } else {
                return 'ERROR: invalid log labels data!';
            }
        }

        return true;
    }
}