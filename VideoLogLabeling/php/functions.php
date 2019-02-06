<?php

function readLogs($paths, &$errors) {
	$events = [];
	foreach ($paths as $path) {
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
	return $events;
}

function getGame($events, $id) {
	$game = NULL;
    foreach ($events as $event) {
	    /* @var Event $event */
	    if(array_key_exists($id, $event->getGames())) {
	        $game = $event->getGame($id);
	        break;
	    }
	}
	return $game;
}

function sendAsJson($fileName, $content) {
    // send data as downloadable json file
    header('Content-Type: application/json');
    if($fileName !== null) {
        header('Content-Disposition: attachment; filename="'.$fileName.'"');
    }
    echo $content;
}

function createSelectionLabelJson($events) {
    $data = [];
    // retrieve game json data
    foreach ($_POST['games'] as $id) {
        $g = getGame($events, $id);
        if($g !== NULL) {
            // event key
            $key = $g->getEvent()->getDateString('Y-m-d') .'_'. $g->getEvent()->getName();
            // add event to data list
            if(!array_key_exists($key, $data)) { $data[$key] = []; }
            // add game json to data list
            $data[$key][] = $g->getLabelsAsJson();
        }
    }
    // construct json string
    $json = '{';
    for ($i=0; $i < count($data); $i++) {
        $key = array_keys($data)[$i];
        $json_arr = $data[$key];
        $json .= '"'.$key.'": [' . "\n";
        for ($j=0; $j < count($json_arr); $j++) { 
            $json .= $json_arr[$j] . ($j !== count($json_arr)-1 ? ',' : '') . "\n";
        }
        $json .= "]" . ($i != count($data)-1 ? ',':'') . "\n";
    }
    $json .= '}';

    return $json;
}