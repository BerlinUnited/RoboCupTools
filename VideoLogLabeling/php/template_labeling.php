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
            // TODO: add ability to select different videos (if available)
            if($game->hasVideos()) {
                // retrieve the source video file type, which should be used first
                $default = !empty(Config::getInstance()->getGame()['video_default']) ? Config::getInstance()->getGame()['video_default'] : '';
                // use the first video to display
                $game_videos = $game->getVideos();
                $video = reset($game_videos);
                // sort the sources by the preferred order
                $sources = $video->getSources();
                usort($sources, function($a, $b) use ($default){
                    if($a->getType() === $default && $b->getType() === $default) { return 0; }
                    elseif ($a->getType() === $default && $b->getType() !== $default) { return -1; }
                    elseif ($a->getType() !== $default && $b->getType() === $default) { return 1; }
                    return 1;
                });
                // write out the sources
                foreach ($sources as $source) {
                    echo '<source src="'.$source->getUrl($basepath).'" type="'.$source->getMimeType().'">'."\n";
                }
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
          $log_url = str_replace($basepath . DIRECTORY_SEPARATOR, '', $log->getInfoFile());
          $sync_video = $game->hasVideos() ? key($game->getVideos()) : '';
          $sync_info = $log->getSyncInfo($sync_video);
          echo '<div id="'.$log->getId().'"'
                  .' class="timeline"'
                  .' data-file="'.$log_url.'"'
                  .' data-logoffset="'.$sync_info['log'].'"'
                  .' data-videooffset="'.$sync_info['video'].'"'
                  .' data-playernumber="'.$log->getPlayer().'"'
                  .(($name !== null && $log->getLabel($name) !== null)?' data-labels="'.str_replace($basepath . DIRECTORY_SEPARATOR, '', $log->getLabel($name)).'"':'')
                  .' data-timeline ></div>';
      }
      ?>
      <div id="configuration" class="panel-group" role="tablist" aria-multiselectable="true">
        <div class="panel panel-default">
          <div id="event_configuration" class="panel-collapse collapse" role="tabpanel" aria-labelledby="headingOne">
            <div class="panel-body"><div class="row"></div></div>
          </div>
        </div>
        <div class="panel panel-default">
          <div id="video_configuration" class="panel-collapse collapse" role="tabpanel" aria-labelledby="headingTwo">
            <div class="panel-body">
                <div class="row">
                  <div class="col-xs-6">
                    <div class="form-group">
                      <label for="video_configuration_before">Video offset <i>before</i> the event (in seconds)</label> <input type="number" step="0.1" min="0" class="form-control" id="video_configuration_before" value="3.0">
                    </div>
                  </div>
                  <div class="col-xs-6">
                    <div class="form-group">
                      <label for="video_configuration_after">Video offset <i>after</i> the event (in seconds)</label> <input type="number" step="0.1" min="0" class="form-control" id="video_configuration_after" value="3.0">
                    </div>
                  </div>
                </div>
            </div>
          </div>
        </div>
        <div id="configuration_control">
          <a role="button" data-toggle="collapse" data-parent="#configuration" href="#event_configuration" aria-expanded="false" aria-controls="event_configuration"><span class="glyphicon glyphicon-plus"></span> Select events</a>
          &nbsp;|&nbsp;
          <a role="button" data-toggle="collapse" data-parent="#configuration" href="#video_configuration" aria-expanded="false" aria-controls="video_configuration"><span class="glyphicon glyphicon-plus"></span> Video configuration</a>
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