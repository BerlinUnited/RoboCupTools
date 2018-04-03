<?php

// Var definition
$logDirectory = 'logs';
$logExtension = '.tc.json';
$logSortFn = function($a, $b) {
	if($a == $b) { return 0; }
  return $a < $b ? -1 : 1;
};
// REGEX: preg_match('/teamcomm_(?P<date>[\d-]+)_(?P<time>[\d-]+)_(?P<team1>[^_]+)_(?P<team2>[^_]+)_(?P<half>[\w\d]+)/', $log, $log_matches);

// read log directory files
$logFiles = [];
$dir = new DirectoryIterator($logDirectory);
foreach ($dir as $fileinfo) {
    if ($fileinfo->isFile() && strtolower(substr($fileinfo->getFilename(), -strlen($logExtension))) === $logExtension) {
      $logFiles[] = $logDirectory . '/' . $fileinfo->getFilename();
    }
}

usort($logFiles, $logSortFn);
?>
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>INDEX</title>
  </head>
  <body>
    <h2>Settings</h2>
    <p>
      <label for="maxBallAge">max ball age:</label>
      <input type="number" name="maxBallAge" min="0">
    </p>
    <h2>Timelines (fallen, ballseen)</h2>
    <ul>
      <?php array_walk($logFiles, function($file){ echo '<li>' . '<a href="d3_timeline.html?file='.rawurlencode($file).'" class="useMaxBallAge">'.$file.'</a>' . '</li>'; }); ?>
    </ul>

    <h2>Positions Heatmap</h2>
    <ul>
      <?php array_walk($logFiles, function($file){ echo '<li>' . '<a href="d3_heatmap.html?file='.rawurlencode($file).'">'.$file.'</a>' . '</li>'; }); ?>
    </ul>

    <h2>Ball Heatmap</h2>
    <ul>
      <?php array_walk($logFiles, function($file){ echo '<li>' . '<a href="d3_ballmap.html?file='.rawurlencode($file).'" class="useMaxBallAge">'.$file.'</a>' . '</li>'; }); ?>
    </ul>

    <h2>Ball Position Slider</h2>
    <ul>
      <?php array_walk($logFiles, function($file){ echo '<li>' . '<a href="d3_ball_slider.html?file='.rawurlencode($file).'" class="useMaxBallAge">'.$file.'</a>' . '</li>'; }); ?>
    </ul>

    <script type="text/javascript">
      Array.from(document.getElementsByClassName("useMaxBallAge")).forEach(function(element) {
        element.addEventListener('click', function(){
          var maxBallAge = parseFloat(document.getElementsByName("maxBallAge")[0].value);
          if(maxBallAge) {
            this.href = this.href + "&maxBallAge="+maxBallAge
          }
        });
      });
    </script>
  </body>
</html>