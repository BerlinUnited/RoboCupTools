<?php
/* @var $this       app\View */
/* @var $games[]    \app\models\SoccerGameModel */
/* @var $game       \app\models\SoccerGameModel */
/* @var $half       app\models\SoccerGameHalftimeModel */
?>

<table class="table table-striped table-hover">
    <thead>
        <tr>
            <th>Date</th>
            <th>Competition</th>
            <th>Opponent</th>
            <th>Halftime(s)</th>
            <th>#Robots</th>
            <th>Label set</th>
        </tr>
    </thead>
    <tbody>
        <?php foreach ($games as $game) : ?>
            <tr>
                <td><?= $game->getDate() ?></td>
                <td><?= $game->getEvent() ?></td>
                <td><?= $game->getOpponent() ?></td>
                <td><?= count($game->getHalftimes()) ?></td>
                <td>
                    <?php
                        foreach ($game->getHalftimes() as $id => $half) {
                            echo 'half'.$id.': '.count($half->robots).'<br>';
                        }
                    ?>
                </td>
                <td>
                    <span class="labels">
                    <?php
                        foreach ($game->getHalftimes() as $id => $half) {
                            echo 'half'.$id.': ';
                            foreach ($half->labels as $label) {
                                echo '<a href="'.\app\Url::to(['/default/view', 'id' => base64_encode($game->getDirectory()), 'half'=>$id, 'name'=>$label]).'">['.$label.']</a> ';
                            }
                            echo '<br>';
                        }
                    ?>
                    </span>
                </td>
            </tr>
        <?php endforeach; ?>
    </tbody>
</table>