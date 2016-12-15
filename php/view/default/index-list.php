<?php
/* @var $this app\View */
/* @var $games[] SoccerGameModel */
/* @var $game SoccerGameModel */
?>

<table class="table table-striped table-hover">
    <thead>
        <tr>
            <th>Date</th>
            <th>Competition</th>
            <th>Opponent</th>
            <th>Halftime</th>
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
                <td><?= $game->getDirectory() ?></td>
                <td>(?)</td>
                <td><a href="<?= \app\Url::to(['/default/view', 'id' => base64_encode($game->getDirectory())]) ?>">???</a></td>
            </tr>
        <?php endforeach; ?>
    </tbody>
</table>