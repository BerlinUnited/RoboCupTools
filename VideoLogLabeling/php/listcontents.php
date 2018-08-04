<?php
require_once 'Event.php';

function is_video($name)
{
  $ext = strtolower (pathinfo($name, PATHINFO_EXTENSION));
  $video = array("mp4", "webm");
  return in_array($ext, $video);
}

function show_game($path, $game_name, &$games) {
  $game_logs = $path . '/game_logs/';
  $game_videos = $path . '/videos/';
  $game_data = $path . '/extracted/';

  if (is_dir($game_logs) && is_dir($game_videos) && is_dir($game_data)) {
    // create Game object
    $g = new Game();
    $scanner = scandir($game_logs);
    foreach ($scanner as $key => $value) {
      if($value == "." || $value == "..") {
        continue;
      }
      
      $file_path = $path . "/" . $value . '/game.log';
      if (is_file($file_path)) {
        # code...
      }
      echo $file_path;
      //is a video
      /*
      if(!is_dir($file_path) && is_video($value))
      {
        $video_name = pathinfo($value, PATHINFO_FILENAME);
        
        // there is already a game with this name
        if(array_key_exists($video_name, $tmp_games)) {
          $g = $tmp_games[$video_name];
          array_push($g->video_paths, $file_path);
          continue;
        }
        
        // create a new game
        $g = new Game();
        $g->name = $game_name;
        $g->half = $video_name;
        $g->video_path = $file_path;
        $g->video_paths = array($file_path); // in case there are several
        
        $log_path = $path . "/" . $g->half;
        if(is_dir($log_path)) {
          list_logs($log_path, $g);
        } else {
          $g->allErrors .= "ERROR: no logs in \"" . $log_path . "\"\n";
          //echo "no logs!!!";
        }
        
        // add to the returned list
        array_push($games, $g);
        
        // store locally for later use in this loop
        $tmp_games[$video_name] = $g;
        //print_r($games);
      }
      */
    }
  }

  $a = scandir($path);
  
  // store all games found in this directory (game halves)
  $tmp_games = array();
  
}

function list_games($path) {
  $games = [];
  $a = scandir($path);
  
  foreach ($a as $key => $value) 
  {
    if($value == "." || $value == "..") {
      continue;
    }
    
    $file_path = $path . "/" . $value;
    if(is_dir($file_path))
    {
      //echo($file_path . "\n");
      show_game($file_path, $value, $games);
    }
  }
  return $games;
}

function list_events($path) {
    $events = [];
    $it = new DirectoryIterator($path);
    foreach($it as $file) {
        if (!$file->isDot() && $file->isDir()) {
            $event = new \Event($file);
            if ($event->isValid()) {
                $events[] = $event;
            }
        }
    }
    return $events;
}



// import 
$events = list_events('./log');
usort($events, function ($a, $b) { return $a->getDate() < $b->getDate(); });
