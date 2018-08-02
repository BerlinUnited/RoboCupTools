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

  <?php
	//
	echo '<div class="row title">';
		echo '<span>Nao Team Humboldt - Annotation Interface</span>';		
	echo '</div>';
    //Header
	echo '<div class="row table-head">';
		echo '<div class="col-sm-offset-1 col-sm-2">';
			echo '<span>Date-Competion-OppTeam-halftime (#Robots)</span>';
		echo '</div>';
		echo '<div class="col-sm-8">';
				echo '<span>Label Set</span>';
		echo '</div>';
	echo '</div>';

	$errors = [];
    $i = 0;
    foreach ($events as $event) {
        /* @var Event $event */
        echo '<div class="row'.($i % 2 == 1 ? ' table-row':'').'">';

        echo '<div class="col-sm-offset-1 col-sm-11">';
            echo '<strong>'.$event->getDateString().' - '.$event->getName().' </strong>';
        echo '</div>';

        echo '</div>'; // .row
        $i++;

        if ($event->hasGames()) {
            foreach ($event->getGames() as $game) {
                /* @var Game $game */
                if($game->hasErrors()) {
                    $errors[] = $game;
                } else {
                    echo '<div class="row'.($i % 2 == 1 ? ' table-row':'').'">';
                    echo '<div class="col-sm-offset-2 col-sm-4">'
                        . $game->getDateString()
                        . ' - ' . $game->getTeam1() . ' vs. ' . $game->getTeam2()
                        . ' #' . $game->getHalf()
                        . '</div>';
                    echo '<div class="col-sm-6">label';
                    /*
                    echo '<span class="labels">';
                    foreach (array_reverse($g->logs[0]->json) as $name => $path) {
                        echo '<a href="./index.php?game='.$key.'&name='.$name.'">['.$name.']</a>';
                    }
                    echo '</span>';
                    */
                    echo '</div>'; // .col-sm-8

                    echo '</div>'; // .row
                    $i++;
                }
            }
        } else {
            echo '<div class="row'.($i % 2 == 1 ? ' table-row':'').'">';
                echo '<div class="col-sm-offset-2 col-sm-10"><i>No games for this event available!</i></div>';
            echo '</div>'; // .row
            $i++;
        }
    }
    
    
    echo '<div class="errors"><pre>';
    foreach ($errors as $game)
    {
      echo $game->getErrors();
    }
    echo '</pre></div>';
  ?>
  </div>
  
  
  
</div>

<div id="watermark"></div>

</body>
</html>