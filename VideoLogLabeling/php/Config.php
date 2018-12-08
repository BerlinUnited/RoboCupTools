<?php

class Config
{
    // the singleton instance variable
    private static $instance = null;

    // directories of the events/log files
    private $paths = [ './log' ];

    // default configuration for events
    private $event = [
        "regex" => "(\\d{4}-\\d{2}-\\d{2})_(\\w+)"
    ];

    // default configuration for games
    private $game = [
        "regex" => "(\\d{4}-\\d{2}-\\d{2}_\\d{2}-\\d{2}-\\d{2})_(\\S+)_vs_(\\S+)_half([1,2])",
        "dirs"  => [
            "nao"   => "game_logs",
            "gc"    => "gc_logs",
            "video" => "videos",
            "data"  => "extracted"
        ],
        "video_file" => "videos.json",
        "video_types" => [ "mp4" ]
    ];

    // default configuration for logs
    private $log = [
        "regex" => "(\\d{1})_(\\d{2})_(\\w+)",
        "name" => "game.log",
        "sync" => "game.log.videoanalyzer.properties",
        "labels" => ["labels", ".json"]
    ];

    private $gc = [
        "file" => "gc.json",
    ];

    /**
     * Private constructor for the singleton pattern.
     * Reads the config file and initializes the config variables.
     */
    private function __construct() {
        // if config file exists, read contents and set available fields.
        if (is_file('config')) {
            $config = json_decode(file_get_contents('config'), true);

            foreach (get_class_vars(__CLASS__) as $k => $v) {
                if($config && array_key_exists($k, $config)) {
                    $this->$k = $config[$k];
                }
            }
        }
    }

    /**
     * Prevent copying this class - it's a singleton!
     */
    private function __clone() {}

    /**
     * Returns the singleton instance of this class.
     * @return Config
     */
    final public static function getInstance() {
        if (self::$instance === null) {
            self::$instance = new Config();
        }
        return self::$instance;
    }

    /**
     * Shorthand function for accessing the log paths configuration
     * @return array
     */
    public static function paths() {
        return self::getInstance()->paths;
    }

    /**
     * Shorthand function for accessing the event configuration
     * @param $key
     * @return mixed
     */
    public static function e($key) {
        return self::getInstance()->event[$key];
    }

    /**
     * Returns the event configuration
     * @return array
     */
    public function getEvent() {
        return $this->event;
    }

    /**
     * Shorthand function for accessing the game configuration
     * @param $key
     * @return mixed
     */
    public static function g($key) {
        return self::getInstance()->game[$key];
    }

    /**
     * Returns the game configuration
     * @return array
     */
    public function getGame() {
        return $this->game;
    }

    /**
     * Shorthand function for accessing the log configuration
     * @param $key
     * @return mixed
     */
    public static function l($key) {
        return self::getInstance()->log[$key];
    }

    /**
     * Returns the log configuration
     * @return array
     */
    public function getLog() {
        return $this->log;
    }

    /**
     * Returns the gamecontroller configuration
     * @return array
     */
    public function getGameController() {
        return $this->gc;
    }

    /**
     * Shorthand function for accessing the gamecontroller configuration
     * @param $key
     * @return mixed
     */
    public static function gc($key) {
        return self::getInstance()->gc[$key];
    }

    /**
     * Returns the current configuration as JSON string.
     * This can be used to create a default configuration file ("config") and adjust the parts necessary for further usage.
     * @return string
     */
    public static function dump() {
        return json_encode([
            'paths' => self::getInstance()->paths,
            'event' => self::getInstance()->event,
            'game' => self::getInstance()->game,
            'log' => self::getInstance()->log,
        ], JSON_PRETTY_PRINT);
    }
}