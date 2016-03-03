<!DOCTYPE html>
<html lang="en" ng-app="test">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
    
  <script src="lib/player/jquery.js"></script>
  
  <script src="lib/angular.min.js"></script>
  <script src="lib/angular-sanitize.min.js"></script>
  <script src="lib/tv4.min.js"></script>
  <script src="lib/ObjectPath.js"></script>
  
  <script src="lib/schema-form.min.js"></script>
  <script src="lib/bootstrap-decorator.js"></script>
  
  <script src="lib/player/mediaelement-and-player.min.js"></script>
  <link rel="stylesheet" href="lib/player/mediaelementplayer.css" />
  
  <link rel="stylesheet" href="lib/bootstrap/css/bootstrap.min.css" />
  <script src="lib/bootstrap/js/bootstrap.min.js"></script>
  
  <link rel="stylesheet" href="style.css" />
  <script src="js/field.js"></script>

</head>

<body>

<div class="container-fluid" ng-controller="MainController">

  <?php
    foreach ($games as $key => $g) {
      echo '<div class="row">';
      echo '<div class="col-sm-1"></div>';
      echo '<div class="col-sm-3">';
      echo '<h3><a href="./index.php?game='.$key.'">'.$g->name.' - '.$g->half.' ('.count($g->logs).')</a></h3>';
      echo '<video src="'.$g->video_path.'" style="width: 100%;" id="player"></video>';
      echo '</div>';
      echo '</div>';
    }
  ?>
    
  </div>
  
</div>

</body>
</html>