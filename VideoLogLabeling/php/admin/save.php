<?php

$tag = $_POST["tag"];
$file = $_POST["file"];
$data = $_POST["data"];

if($tag == '') {
  echo "ERROR: a tag need to be set";
} 
else if(substr($file, -5) == ".json") {
  
  if(substr($file, -5 - strlen($tag), -5) != $tag) {
    $path = "../".substr($file, 0, -5)."-".$tag."".substr($file, -5);
  } else {
    $path = "../".$file;
  }
  
  ini_set('track_errors', 1);
  $myfile = fopen($path, "w");
  if ( $myfile ) {
    fwrite($myfile, $data);
    fclose($myfile);
    echo "SUCCESS: writing to ".$path. " -- ".$myfile." ". $data;
  } else {
    echo "ERROR: writing to ".$path."\n";
    echo $php_errormsg;
  }
}

?>