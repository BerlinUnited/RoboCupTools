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
