<?php
// uncomment/delete in production mode or set to FALSE
defined('APP_DEBUG') or define('APP_DEBUG', TRUE);

require(__DIR__ . '/php/autoload.php');
require(__DIR__ . '/php/base/Application.php');

$config = require(__DIR__ . '/php/config.php');

(new app\Application($config))->run();

/*    
  include 'php/listcontents.php';
  
  $game = NULL;
  $name = "blank";
  
  if(isset($_GET["name"])) {
    $name = $_GET["name"];
  }
  
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
*/