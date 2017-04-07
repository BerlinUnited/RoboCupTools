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

<body>

<div class="container-fluid" ng-controller="MainController">

  <?php
	//
	echo '<div class="row title">';
		echo '<span>Nao Team Humboldt - Annotation Interface</span>';		
	echo '</div>';
    //Header
	echo '<div class="row table-head">';
		echo '<div class="col-sm-1"></div>';
		echo '<div class="col-sm-2">';
			echo '<span>Date-Competion-OppTeam-halftime (#Robots)</span>';
		echo '</div>';
		echo '<div class="col-sm-8">';
				echo '<span>Label Set</span>';
		echo '</div>';
	echo '</div>';
	
    $i = 0;
    foreach ($games as $key => $g) {
      
      if(sizeof($g->logs) > 0) 
      {
        if( $i % 2 == 1) {
          echo '<div class="row table-row">';
        } else {
          echo '<div class="row">';
        }
        echo '<div class="col-sm-1"></div>';
        
        echo '<div class="col-sm-2">';
          echo '<strong>'.$g->name.' - '.$g->half.' ('.count($g->logs).') </strong>';
        echo '</div>';
        
        echo '<div class="col-sm-8">';
          echo '<span class="labels">';
          foreach (array_reverse($g->logs[0]->json) as $name => $path) {
            echo '<a href="./index.php?game='.$key.'&name='.$name.'">['.$name.']</a>';
          }
          echo '</span>';
        echo '</div>';
        echo '</div>';
        //echo '<video src="'.$g->video_path.'" style="width: 100%;" id="player'.$i.'"></video>';
        $i++;
      }
    }
    
    
    echo '<div class="errors"><pre>';
    foreach ($games as $key => $g) 
    {
      echo $g->allErrors;
    }
    echo '</pre></div>';
  ?>
  </div>
  
  
  
</div>

<div id="watermark"></div>

</body>
</html>