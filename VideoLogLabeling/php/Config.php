<?php

class Config
{
    private static $instance = null;

    // configuration for events
    private $event = [];
    // configuration for games
    private $game = [];
    // configuration for logs
    private $log = [];

    private function __construct() {
        $config = json_decode(file_get_contents('config'), true);

        foreach (get_class_vars(__CLASS__) as $k => $v) {
            if(array_key_exists($k, $config)) {
                $this->$k = $config[$k];
            }
        }
    }

    private function __clone() { /* disable copy */ }

    final public static function getInstance() {
        if (self::$instance === null) {
            self::$instance = new Config();
        }
        return self::$instance;
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
     * Shorthand function for accessing the game configuration
     * @param $key
     * @return mixed
     */
    public static function g($key) {
        return self::getInstance()->game[$key];
    }

    /**
     * Shorthand function for accessing the log configuration
     * @param $key
     * @return mixed
     */
    public static function l($key) {
        return self::getInstance()->log[$key];
    }

}