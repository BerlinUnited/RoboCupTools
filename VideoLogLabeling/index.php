<?php
  include 'php/listcontents.php';
  
  $game = NULL;
  $name = "blank";
  
  if(isset($_GET["name"])) {
    $name = $_GET["name"];
  }
  
  if(isset($_GET["game"])) {
    // TODO: search for a game!
  }
?>

<?php

if( $game != NULL) {
  include 'php/labeling_template.php';
} else {  
  include 'php/overview_template.php';
}
?>
