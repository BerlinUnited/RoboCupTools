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
$name = isset($_GET["name"]) ? $_GET["name"] : null;

$errors = [];
$events = readLogs(Config::paths(), $errors); // read log directories
$game = isset($_GET["game"]) ? getGame($events, $_GET["game"]) : NULL; // search for a requested game

usort($events, function ($a, $b) { return $a->getDate() < $b->getDate(); });

// if a requested game was found, show the labeling view, otherwise the overview
if (isset($_GET["download"])) {
    switch ($_GET["download"]) {
        case 'selected':
            if(isset($_POST['games']) && is_array($_POST['games'])) {
                sendAsJson('selected_game_data.json', createSelectionLabelJson($events));
            } else {
                echo "ERROR: invalid game selection!";
            }
            break;
        case 'game':
            if ($game != NULL) {
                $fileName = $game->getDateString() . ' - ' . $game->getTeam1() . ' vs. ' . $game->getTeam2() . ' #' . $game->getHalf().'.json';
                sendAsJson($fileName, $game->getLabelsAsJson());
            } else {
                echo "ERROR: invalid game id!";
            }
            break;
        default:
            echo "ERROR: invalid download request!";
            break;
    }
} elseif ($game != NULL) {
    $request = isset($_SERVER['REQUEST_METHOD']) ? strtoupper($_SERVER['REQUEST_METHOD']) : 'GET';
    // save the posted labels
    if($request === 'POST') {
        // TODO: we need some kind of authentication/authorization
        if (isset($_POST['tag']) && isset($_POST['data'])) {
            $result = $game->saveLabels($_POST['tag'], $_POST['data']);
            // return the result of saving labels
            echo $result !== true ? $result : 'SUCCESS';
        } else {
            echo 'ERROR: missing tag or label data!';
        }
    } else {
        include 'php/template_labeling.php';
    }
} else {
    include 'php/template_overview.php';
}
