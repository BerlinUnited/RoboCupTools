<?php
class Log
{
  public $json = '';
  public $sync = '';
  public $video_offset = 0;
  public $log_offset = 0;
  
  function __construct($json, $sync) {
    $this->json = $json;
    $this->sync = $sync;
    $this->parse_sync();
  }
  
  function parse_sync() {
    // TODO: read and parse the file $this->sync
    $lines = file($this->sync);
    foreach ($lines as $line_num => $line) {  
    if(strcmp(substr($line,0,16),'sync-time-video=') == 0){
      //echo substr($line,16) . "<br />\n";
      $this->video_offset = substr($line,16);
    }
    elseif(strcmp(substr($line,0,14),'sync-time-log=') == 0){
      //echo substr($line,14) . "<br />\n";
      $this->log_offset = substr($line,14);
    }
    /*elseif(strcmp(substr($line,0,11),'video-file=') == 0){
      echo substr($line,11) . "<br />\n";
    }*/
  }
    //$this->video_offset = 12.993253731;
    //$this->log_offset = 270.937;
  }
}

class Game
{
  public $name = 'none';
  public $half = '';
  public $video_path = '';
  public $logs = array();
  public $allErrors = '';
}

//$logfilePath = './log';
//list_content($logfilePath);
/*
function list_content($path){
  
  $a = scandir($path);
  //print_r($a);
  
  for ($i = 0; $i < count($a); ++$i) 
  {
    if($a[$i] == "." || $a[$i] == "..") {
      continue;
    }
    
    $file_path = $path . "/" . $a[$i];
    if(is_dir($file_path))
    {
      echo($file_path . "\n");
      list_content($file_path);
    } 
    else // is file
    {
      echo($file_path . "\n");
    }
    }
}*/

function find_json($path)
{
  $result = Array();
  
  $a = scandir($path);
  foreach($a as $key => $value) 
  {
    if(substr($value, -5) == ".json") 
    {
      $file_path = $path . "/" . $value;
      
      if($p = strpos($value, "-")) {
        $name = substr($value, $p+1, -5);
        $result[$name] = $file_path;
      } else {
        $result["blank"] = $file_path;
      }
    }
  }
  
  return $result;
}

function list_logs($path, $g)
{
  $a = scandir($path);
  $errors = '';
  
  foreach ($a as $key => $value) 
  {
    if($value == "." || $value == "..") {
      continue;
    }
    
    $file_path = $path . "/" . $value;
    //is a log
    if(is_dir($file_path))
    {
      $json_files = find_json($file_path);

      //$json_path = $file_path . "/labels.json";
      $sync_data = $file_path . "/game.log.videoanalyzer.properties";
      
      //if(!is_file($json_path)) {
      if(!array_key_exists("blank", $json_files)) {
        $errors = $errors . "ERROR: no json file in ".$file_path."\n";
        //echo "ERROR: no json file in ".$file_path."\n";
      } else if(!is_file($sync_data)) {
        $errors = $errors . "ERROR: no sync data in ".$file_path."\n";
        //echo "ERROR: no sync data in ".$file_path."\n";
      } else {
        array_push($g->logs, new Log($json_files, $sync_data));
      }
    }
    }
  //echo $errors;
  $g->allErrors = $errors;
}

function is_video($name)
{
  $ext = strtolower (pathinfo($name, PATHINFO_EXTENSION));
  $video = array("mp4", "webm");
  return in_array($ext, $video);
}

function show_game($path, $game_name, &$games) {
  $a = scandir($path);
  
  // store all games found in this directory (game halves)
  $tmp_games = array();
  
  foreach ($a as $key => $value) 
  {
    if($value == "." || $value == "..") {
      continue;
    }
    
    $file_path = $path . "/" . $value;
    //is a video
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
  }
}

function list_games($path) {
  $games = array();
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



// import 
$games = list_games('./log');
?>
