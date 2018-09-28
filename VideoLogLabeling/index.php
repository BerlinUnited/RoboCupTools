<?php
// required includes
require_once 'php/functions.php';
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

$errors = [];
$events = readLogs(Config::paths(), $errors); // read log directories
$game = isset($_GET["game"]) ? getGame($events, $_GET["game"]) : NULL; // search for a requested game

usort($events, function ($a, $b) { return $a->getDate() < $b->getDate(); });

// if a requested game was found, show the labeling view, otherwise the overview
if (isset($_GET["download"])) {
    switch ($_GET["download"]) {
        case 'all':
            // TODO: 
            break;
        case 'selection':
            // TODO: 
            break;
        case 'game':
            if ($game != NULL) {
                // send data as downloadable json file
                header('Content-Type: application/json');
                header('Content-Disposition: attachment; filename="'.$game->getDateString() . ' - ' . $game->getTeam1() . ' vs. ' . $game->getTeam2() . ' #' . $game->getHalf().'.json"');
                echo $game->getLabelsAsJson();
            } else {
                echo "ERROR: invalid game id!";
            }
            break;
        default:
            echo "ERROR: invalid download request!";
            break;
    }
} elseif ($game != NULL) {
    include 'php/labeling_template.php';
} else {
    include 'php/overview_template.php';
}
