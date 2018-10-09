<?php
/* @var Game $game */
/* @var string $name */
/* @var string $basepath */
?>
<!DOCTYPE html>
<html lang="en" ng-app="test">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title><?= $game->getEvent()->getName() ?> | <?= $game->getDateString() ?> - <?= $game->getTeam1() ?> vs. <?= $game->getTeam2() ?> #<?= $game->getHalf() ?></title>
    
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
    <div class="row" id="title">
        <div class="col-sm-offset-2 col-sm-8">
            <a href="index.php">Nao Team Humboldt - Annotation Interface</a>
        </div>
    </div>

    <div class="row">
        <div class="col-sm-2">
            <h3><a href="./index.php"><< BACK</a></h3>
        </div>
        <div class="col-sm-10">
            <h3><?= $game->getEvent()->getName() ?> | <?= $game->getDateString() ?> - <?= $game->getTeam1() ?> vs. <?= $game->getTeam2() ?> #<?= $game->getHalf() ?></h3>
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
        <?php
            foreach ($game->getVideos() as $video) {
                $video_url = str_replace($basepath . DIRECTORY_SEPARATOR, '', $video);
                echo '<source src="'.$video_url.'" >';
            }
        ?>
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
      foreach ($game->getLogs() as $log) {
          /* @var NaoLog $log */
          // TODO: security risk - any file could be loaded?!
          $log_url = str_replace($basepath . DIRECTORY_SEPARATOR, '', $log->getEvents());
          echo '<div id="'.$log->getId().'"'
                  .' class="timeline"'
                  .' data-file="'.$log_url.'"'
                  .' data-logoffset="'.$log->getSyncInfo('log_offset').'"'
                  .' data-videooffset="'.$log->getSyncInfo('video_offset').'"'
                  .' data-playernumber="'.$log->getPlayer().'"'
                  .(($name !== null && $log->getLabel($name) !== null)?' data-labels="'.str_replace($basepath . DIRECTORY_SEPARATOR, '', $log->getLabel($name)).'"':'')
                  .' data-timeline ></div>';
      }
      ?>
      <div id="configuration">
        <div class="collapse container-fluid" id="event_configuration">
          <div class="row"></div>
        </div>
        <div id="configuration_control">
          <span class="caret"></span> <a role="button" data-toggle="collapse" href="#event_configuration" aria-expanded="false" aria-controls="collapseExample">Select events</a>
        </div>
      </div>
      <?php /* NOTE: There's no user authentication - everybody can submit labels! */ ?>
      <form id="label_title_form" class="form-inline">
        <div class="form-group">
          <label for="label_title">Name: </label>
          <input type="text" id="label_title" name="label_title" class="form-control" data-ng-model="widget.title" placeholder="Labels title">
        </div>
        <input type="button" class="btn btn-default" value="Submit" ng-click="save($event)">
        <div class="alert hidden" role="alert"></div>
      </form>
    </div>

  
</div>

  <div class="hidden">
    <img id="nao" src="nao.png" />
  </div>

  <script src="js/annotation_labels.js"></script>
  <script src="js/field.js"></script>
  <script src="js/labeling.js"></script>
</body>
</html>