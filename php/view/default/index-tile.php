<?php
/* @var $this app\View */
/* @var $games[] \app\models\SoccerGameModel */
/* @var $game \app\models\SoccerGameModel */

$this->registerCss('
    #game_overview .dl-horizontal dt { width: 80px; }
    #game_overview .dl-horizontal dd { margin-left: 100px; }
');
?>
<div class="row">
<?php foreach ($games as $game) : ?>
    <div class="col-sm-6 col-lg-4">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title"><strong><?= \app\Application::$app->params['ownTeamName'] ?> vs. <?= $game->getOpponent() ?></strong></h3>
            </div>
            <div class="panel-body">
                <dl class="dl-horizontal">
                    <dt>Date:</dt><dd><?= $game->getDate() ?></dd>
                    <dt>Event:</dt><dd><?= $game->getEvent() ?></dd>
                    <dt>Location:</dt><dd><?= $game->getDirectory() ?></dd>
                    <dt>Halftimes:</dt><dd><?= count($game->getHalftimes()) ?></dd>
                    <dt>Robots:</dt><dd><?php
                    foreach ($game->getHalftimes() as $id => $half) {
                        echo 'half'.$id.': '.count($half->robots).'<br>';
                    }
                    ?></dd>
                    <dt>Cameras:</dt><dd><?php
                    foreach ($game->getHalftimes() as $id => $half) {
                        echo 'half'.$id.': '. count($half->video->getCameras()).'<br>';
                    }
                    ?></dd>
                    <dt>Labels:</dt><dd><?php
                    foreach ($game->getHalftimes() as $id => $half) {
                            echo 'half'.$id.': ';
                            foreach ($half->labels as $label) {
                                echo '<a href="'.\app\Url::to(['/default/view', 'id' => base64_encode($game->getDirectory()), 'half'=>$id, 'name'=>$label]).'">['.$label.']</a> ';
                            }
                            echo '<br>';
                    }
                    ?></dd>
                </dl>
            </div>
        </div>
    </div>
<?php endforeach; ?>
</div>