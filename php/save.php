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
  
  $myfile = fopen($path, "w");
  fwrite($myfile, $data);
  fclose($myfile);
  
  echo $path;
}

?>