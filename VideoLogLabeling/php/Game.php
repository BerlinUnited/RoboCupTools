<?php

class Game
{
    private static $regex = "/(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_(\S+)_vs_(\S+)_half([1,2])/";
    // 1_91_Nao0379
    private static $regex_log = "/(\d{1})_(\d{2})_(\w+)/";
    private static $directories = [
        'nao'  => 'game_logs',
        'gc'   => 'gc_logs',
        'video'=> 'videos',
        'data' => 'extracted'
    ];

    private $is_valid = false;
    private $path;
    private $date;
    private $team1;
    private $team2;
    private $half;

    private $errors = [];
    private $warnings = [];

    function __construct(SplFileInfo $path) {
        $this->is_valid = preg_match(static::$regex, $path->getFilename(), $matches) === 1;
        if ($this->is_valid) {
            $this->path = $path->getRealPath();
            $this->date = DateTimeImmutable::createFromFormat('Y-m-d_H-i-s',$matches[1]);
            $this->team1 = str_replace('_', ' ', $matches[2]);
            $this->team2 = str_replace('_', ' ', $matches[3]);
            $this->half = intval($matches[4]);

            $this->init();
        }
    }

    private function init() {
        $path = $this->path . DIRECTORY_SEPARATOR . static::$directories['nao'];
        if (is_dir($path)) {
            // TODO: read nao logs
            $it = new DirectoryIterator($path);
            foreach($it as $file) {
                if (!$file->isDot() && $file->isDir()) {
                    
                    //echo  . "\n";
                }
            }
        } else {
            $this->errors[] = 'No log files!';
        }

        if (is_dir($this->path . DIRECTORY_SEPARATOR . static::$directories['video'])) {
            // TODO: read video files
        } else {
            $this->errors[] = 'No video files!';
        }

        if (is_dir($this->path . DIRECTORY_SEPARATOR . static::$directories['data'])) {
            // TODO: read video files
            //var_dump(glob($this->path . DIRECTORY_SEPARATOR . static::$directories['data'] . '*.mp4'));
        } else {
            $this->errors[] = 'No sync & json files!';
        }

        if (is_dir($this->path . DIRECTORY_SEPARATOR . static::$directories['gc'])) {
            // TODO: read gamecontroller files
        } else {
            $this->warnings[] = 'No gamecontroller files!';
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
}