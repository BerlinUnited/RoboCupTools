<?php
/* @var $this       app\View */
/* @var $games[]    \app\models\SoccerGame */
/* @var $game       \app\models\SoccerGame */
/* @var $half       app\models\SoccerHalftime */
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
            <?php foreach ($game->getHalftimes() as $half) : ?>
            <tr>
                <td><?= $game->getDate() ?></td>
                <td><?= $game->getEvent() ?></td>
                <td><?= $game->getOpponent() ?></td>
                <td><?= count($game->getHalftimes()) ?></td>
                <td><?='half'.$half->id.': '.count($half->robots)?>
                </td>
                <td>
                    <span class="labels">
                    <?php
                        $labels = '';
                        foreach ($half->labels as $key => $label) {
                            if($label === 'new') {
                                $labels = '<a href="'.\app\Url::to(['/default/view', 'id' => base64_encode($game->getDirectory()), 'half'=>$half->id, 'name'=>$label]).'">['.$label.']</a> ' . $labels;
                            } else {
                                $labels .= '<a href="'.\app\Url::to(['/default/view', 'id' => base64_encode($game->getDirectory()), 'half'=>$half->id, 'name'=>$label]).'">['.$label.']</a> ';
                            }
                        }
                        echo $labels;
                    ?>
                    </span>
                </td>
            </tr>
            <?php endforeach; ?>
        <?php endforeach; ?>
    </tbody>
</table>