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
    $this->video_offset = 12.993253731;
    $this->log_offset = 270.937;
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
			
			$json_path = $file_path . "/labels.json";
			$sync_data = $file_path . "/game.log.videoanalyzer.properties";
			
			if(!is_file($json_path)) {
				$errors = $errors . "ERROR: no json file in ".$file_path."\n";
				//echo "ERROR: no json file in ".$file_path."\n";
			} else if(!is_file($sync_data)) {
				$errors = $errors . "ERROR: no sync data in ".$file_path."\n";
				//echo "ERROR: no sync data in ".$file_path."\n";
			} else {
				array_push($g->logs, new Log($json_path, $sync_data));
			}
		}
    }
	//echo $errors;
	$g->allErrors = $errors;
}

function show_game($path, $game_name, &$games) {
	$a = scandir($path);
	
	foreach ($a as $key => $value) 
	{
		if($value == "." || $value == "..") {
			continue;
		}
		
		$file_path = $path . "/" . $value;
		//is a video
		if(is_file($file_path) && strlen($value) > 4 && substr($value, -4) == ".mp4")
		{
			$g = new Game();
			$g->name = $game_name;
			$g->half = substr($value, 0, -4);
			$g->video_path = $file_path;
			
			$log_path = $path . "/" . $g->half;
			if(is_dir($log_path)) {
				list_logs($log_path, $g);
			} else {
				echo "no logs!!!";
			}
			
			
			array_push($games, $g);
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
