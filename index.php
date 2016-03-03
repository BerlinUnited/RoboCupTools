<?php
  include 'php/listcontents.php';
  
  $game = NULL;
  
  if(isset($_GET["game"])) {
    foreach ($games as $key => $g) {
      if(sizeof($g->logs) > 0) {
        if($_GET["game"] == $key) {
          $game = $g;
          break;
        }
      }
    }
  }
?>

<?php

if( $game != NULL) {
  include 'php/labeling_template.php';
} else {  
  include 'php/overview_template.php';
}
?>
