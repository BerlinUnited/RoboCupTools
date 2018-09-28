<!DOCTYPE html>
<html lang="en" ng-app="test">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
    
  <script src="lib/jquery-3.2.0.js"></script>
  
  <script src="lib/player/mediaelement-and-player.min.js"></script>
  <link rel="stylesheet" href="lib/player/mediaelementplayer.css" />
  
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
    <div class="row" id="content">
        <div class="col-sm-offset-2 col-sm-8">
            <form method="post" action="index.php?download=selected">
            <table class="table table-striped table-condensed">
                <thead>
                    <tr>
                        <th></th>
                        <th>Competition</th>
                        <th>Date, Time - Opponents - #halftime (Robots)</th>
                        <th>Label set</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
<?php
if (!$events) {
  echo '<tr><td colspan="5"><i>No events/games available.</i></td></tr>';
}

foreach ($events as $event) {
    /* @var Event $event */
    echo '<tr><td></td><td colspan="4">'.$event->getDateString().' - '.$event->getName().'</td></tr>';

    if ($event->hasGames()) {
        foreach ($event->getGames() as $game) {
            /* @var Game $game */
            if($game->hasErrors()) {
                $errors[] = $game;
            } else {
                echo '<tr>'
                        .'<td><input type="checkbox" name="games[]" value="'.$game->getId().'" /></td>'
                        .'<td>'.'</td>'
                        .'<td>'
                            . $game->getDateString()
                            . ' - ' . $game->getTeam1() . ' vs. ' . $game->getTeam2()
                            . ' #' . $game->getHalf()
                            . ' (' . $game->getSize() . ')'
                        .'</td>'
                        .'<td>'
                    //.'<a href="./index.php?game='.$game->getId().'&name=New">[New]</a>'
                ;

                if ($game->hasLogs()) {
                    $keys = [];
                    foreach ($game->getLogs() as $log) {
                        /* @var NaoLog $log */
                        foreach ($log->getLabels() as $key => $file) {
                            if(in_array($key, $keys)) { continue; }
                            $keys[] = $key;
                        }
                    }
                    foreach ($keys as $key) {
                        echo '<a href="./index.php?game='.$game->getId().'&name='.$key.'">['.$key.']</a>';
                    }
                }
                echo '</td>'
                    .'<td>'
                        . ($game->hasLabels() ? '<a href="./index.php?download=game&game='.$game->getId().'" target="_blank" title="Save annotated events as JSON"><span class="glyphicon glyphicon-save-file"></span></a>' : '')
                    .'</td>'
                    .'</tr>';
            }
        }
    } else {
        echo '<tr class="warning"><td colspan="3">No games for this event available!</td></tr>';
    }
}
?>
                </tbody>
            </table>
            <input class="btn btn-default btn-xs pull-right" type="submit" value="Download selected">
            </form>
        </div><!-- col-sm-offset-2 col-sm-8 -->
    </div><!-- .row #content -->
</div>

<div class="errors <?=$errors?'':'hide'?>">
    <pre>
  <?php
  foreach ($errors as $game) {
      if($game instanceof Game) {
          foreach ($game->getErrors() as $error) {
              echo 'ERROR: ' . $error . '<br>';
          }
      } else {
          echo '<b>ERROR: ' . $game . '</b><br>';
      }
  }
  ?>
    </pre>
</div>

<div id="watermark"></div>

</body>
</html>