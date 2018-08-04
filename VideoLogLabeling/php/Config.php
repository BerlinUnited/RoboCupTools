<?php

class Config
{
    // configuration for events
    public static $event = [
        // the regular expression, identifying the event directory
        'regex' => "/(\d{4}-\d{2}-\d{2})_(\w+)/"
    ];

    // configuration for games
    public static $game = [
        // the regular expression, identifying the game(half) directory inside a event directory
        'regex' => "/(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_(\S+)_vs_(\S+)_half([1,2])/",
        'dirs' => [
            'nao'  => 'game_logs',
            'gc'   => 'gc_logs',
            'video'=> 'videos',
            'data' => 'extracted'
        ],
        'video_types' => [ "mp4", "webm" ],
    ];

    // configuration for logs
    public static $log = [
        // the regular expression, identify the robots game log directory inside a game directroy
        'regex' => "/(\d{1})_(\d{2})_(\w+)/",
        'sync' => 'game.log.videoanalyzer.properties',
        'labels' => ['labels', '.json'],
    ];


    /**
     * Shorthand function for accessing the event configuration
     * @param $key
     * @return mixed
     */
    public static function e($key) {
        return self::$event[$key];
    }

    /**
     * Shorthand function for accessing the game configuration
     * @param $key
     * @return mixed
     */
    public static function g($key) {
        return self::$game[$key];
    }

    /**
     * Shorthand function for accessing the log configuration
     * @param $key
     * @return mixed
     */
    public static function l($key) {
        return self::$log[$key];
    }

}