<!DOCTYPE html>
<html lang="en" ng-app="test">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
    
  <script src="lib/player/jquery.js"></script>
  
  <script src="lib/player/mediaelement-and-player.min.js"></script>
  <link rel="stylesheet" href="lib/player/mediaelementplayer.css" />
  
  <link rel="stylesheet" href="lib/bootstrap/css/bootstrap.min.css" />
  <script src="lib/bootstrap/js/bootstrap.min.js"></script>
  
  <link rel="stylesheet" href="style.css" />
  <script src="js/field.js"></script>

</head>

<style>
.labels a {
  margin: 5px;
}
.labels {
  margin-bottom:5px;
}
</style>

<body>

<div class="container-fluid" ng-controller="MainController">

  <?php
      $i = 0;
      foreach ($games as $key => $g) {
        
        if(sizeof($g->logs) > 0) 
        {
          if($i % 6 == 0) {
            if($i > 0) {
              echo '</div>';
              echo '</div>';
            }
            echo '<div class="row">';
            echo '<div class="row-height">';
          }
          
            echo '<div class="col-sm-2 col-height">';
            echo '<div class="inside inside-full-height">';
            echo '<div class="content">';
            
              echo '<h4>'.$g->name.'</h4>'; 
              echo '<h4>'.$g->half.' ('.count($g->logs).') </h4>';
              echo '<div class="labels">';
              foreach ($g->logs[0]->json as $name => $path) {
                echo '<a href="./index.php?game='.$key.'&name='.$name.'">['.$name.']</a>';
              }
              echo '</div>';
              echo '<video src="'.$g->video_path.'" style="width: 100%;" id="player"></video>';
            
            echo '</div>';
            echo '</div>';
            echo '</div>';
          
          $i++;
        }
      }
    
    if($i > 0) {
      echo '</div>';
      echo '</div>';
    }
    
    echo '<div style=""><pre>';
    foreach ($games as $key => $g) 
    {
      echo $g->allErrors;
    }
    echo '</pre></div>';
  ?>
  </div>
  
  
  
</div>

</body>
</html>