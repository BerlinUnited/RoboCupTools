<!DOCTYPE html>
<html lang="en" ng-app="test">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
    
  <script src="lib/jquery-3.2.0.js"></script>
  
  <script src="lib/angular.min.js"></script>
  <script src="lib/angular-sanitize.min.js"></script>
  
  <script src="lib/tv4.min.js"></script>
  <script src="lib/ObjectPath.js"></script>
  
  <script src="lib/schema-form.min.js"></script>
  <script src="lib/bootstrap-decorator.js"></script>
  
  <script src="lib/player/mediaelement-and-player.js"></script>
  <link rel="stylesheet" href="lib/player/mediaelementplayer.min.css">
  
  <link rel="stylesheet" href="lib/bootstrap/css/bootstrap.min.css" />
  <script src="lib/bootstrap/js/bootstrap.min.js"></script>
  
  <link rel="stylesheet" href="style.css" />
 
</head>

<body>

<div class="container-fluid" ng-controller="MainController">
  <div class="row title">
    <span>Nao Team Humboldt - Annotation Interface</span>
  </div>

  <div class="row">
    <div class="col-sm-2">
      <h3><a href="./index.php"><< BACK</a></h3>
    </div>
    <div class="col-sm-10">
      <h3><?php echo $g->name." - ".$g->half; ?></h3>
    </div>
  </div>


    <div class="col-sm-2">
      <div ng-controller="FormController"> 
        <form name="labels" sf-schema="schema" sf-form="form" sf-model="model" ng-submit="onSubmit(labels)"></form>
      </div>
    </div>
    
    <div class="col-sm-7">
      <div ng-controller="PlayerController">
        <video class="video-player" id="player" preload="metadata">
        <?php /* src="<?php echo $g->video_path; ?>" */ ?>
        <?php foreach ($g->video_paths as $key => $value) { ?>
          <source src="<?php echo $value; ?>" >
        <?php }?>
        </video>
      </div>
    </div>
    
    <div class="col-sm-3">
      <div ng-controller="DrawingController">
        <canvas id="canvas" width="740" height="1040" class="field-drawing"></canvas>
      </div>
    </div>


    <div class="col-sm-10 pull-right">
      <?php
      //<div data-timeline data-file="log/labels.json"></div>
        foreach ($g->logs as $key => $log) {
          echo '<div class="timeline" data-timeline data-file="'.$log->json[$name].'" data-logoffset="'.$log->log_offset.'" data-videooffset="'.$log->video_offset.'"></div>';
        }
      ?>
      
      <?php /* NOTE: There's no user authentication - everybody can submit labels! */ ?>
      <form>
        Name: <input type="text" name="lastname" data-ng-model="widget.title">
        <input type="button" value="Submit" ng-click="save($event)">
      </form>
    </div>

  
</div>

  <div class="hide">
    <img id="nao" src="nao.png" />
  </div>


  <script type="text/javascript">
    label_name = "<?=($name != 'blank')?$name:''?>";
  </script>
  <script src="js/field.js"></script>
  <script src="js/labeling.js"></script>
</body>
</html>