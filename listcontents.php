<?php
include 'php/listcontents.php';
?>


<html>
<head>
</head>

<body>

<?php
	foreach ($games as $key => $g) {
		if(sizeof($g->logs) > 0) {
			
      foreach ($g->logs[0]->json as $key => $path) {
        echo '<div>'.$key.'</div>';
      }
      
			echo '<div><a href="'.$g->video_path.'">'.$g->name.' - '.$g->half.'</a>';
			
			foreach ($g->logs as $key => $log) {
				echo '<div><a href="'.$log->json["blank"].'">'.$g->name.'</a></div>';
			}
			
			echo '</div>';
		}
	}
?>

</body>
</html>




