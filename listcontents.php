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
			
			echo '<div><a href="'.$g->video_path.'">'.$g->name.' - '.$g->half.'</a>';
			
			foreach ($g->logs as $key => $log) {
				echo '<div><a href="'.$log->json.'">'.$g->name.'</a></div>';
			}
			
			echo '</div>';
		}
	}
?>

</body>
</html>




