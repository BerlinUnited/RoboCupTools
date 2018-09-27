<?php
// required includes
require_once 'php/Event.php';

// global variables
$logPath = './log';
$basepath = __DIR__;
$name = isset($_GET["name"]) ? $_GET["name"] : "new";
$game = NULL;
$events = [];
$errors = [];

// read log directory
try {
    foreach(new DirectoryIterator($logPath) as $file) {
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
