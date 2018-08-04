<?php

include 'php/listcontents.php';

$basepath = __DIR__;
$name = isset($_GET["name"]) ? $_GET["name"] : "new";
$game = NULL;

if (isset($_GET["game"])) {
    foreach ($events as $event) {
        /* @var Event $event */
        if(array_key_exists($_GET["game"], $event->getGames())) {
            $game = $event->getGame($_GET["game"]);
            break;
        }
    }
}

if ($game != NULL) {
    include 'php/labeling_template.php';
} else {
    include 'php/overview_template.php';
}
