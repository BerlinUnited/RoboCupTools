<?php
// required includes
require_once 'php/Config.php';
require_once 'php/Event.php';

// was the script called by commandline?
if (PHP_SAPI === 'cli') {
    if($argv[1] === 'dumpconfig') {
        echo Config::dump();
    } else {
        echo "ERROR: Unknown argument!\n";
    }
    exit(0);
}

// global variables
$basepath = __DIR__;
$name = isset($_GET["name"]) ? $_GET["name"] : "new";
$game = NULL;
$events = [];
$errors = [];

// read log directories
foreach (Config::paths() as $path) {
    if (is_dir($path) && is_readable($path)) {
        try {
            foreach(new DirectoryIterator($path) as $file) {
                if (!$file->isDot() && $file->isDir()) {
                    $event = new \Event($file);
                    if ($event->isValid()) {
                        $events[] = $event;
                    }
                }
            }
        } catch (Exception $e) {
            $errors[] = 'reading log directory: ' . $e->getMessage();
        }
    }
}

usort($events, function ($a, $b) { return $a->getDate() < $b->getDate(); });

// search for a requested game
if (isset($_GET["game"])) {
    foreach ($events as $event) {
        /* @var Event $event */
        if(array_key_exists($_GET["game"], $event->getGames())) {
            $game = $event->getGame($_GET["game"]);
            break;
        }
    }
}

// if a requested game was found, show the labeling view, otherwise the overview
if ($game != NULL) {
    include 'php/labeling_template.php';
} else {
    include 'php/overview_template.php';
}
