<?php
include 'php/listcontents.php';
?>


<html>
<head>
</head>

<body>

<?php
foreach ($events as $event) {
    /* @var Event $event */
    if ($event->hasGames()) {
        foreach ($event->getGames() as $game) {
            /* @var Game $game */

            if ($game->getLogs()) {

                foreach ($g->logs[0]->json as $key => $path) {
                    echo '<div>' . $key . '</div>';
                }

                echo '<div><a href="' . $g->video_path . '">' . $g->name . ' - ' . $g->half . '</a>';

                foreach ($g->logs as $key => $log) {
                    echo '<div><a href="' . $log->json["blank"] . '">' . $g->name . '</a></div>';
                }

                echo '</div>';
            }
        }
    }
}
?>

</body>
</html>




