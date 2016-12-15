<?php
/* @var $this app\View */
/* @var $games[] SoccerGameModel */
/* @var $game SoccerGameModel */

$this->registerCss('
    #game_overview .dl-horizontal dt { width: 80px; }
    #game_overview .dl-horizontal dd { margin-left: 100px; }
');
?>
<?php foreach ($games as $game) : ?>
    <div class="col-sm-6 col-lg-4">
        <a href="<?= \app\Url::to(['/default/view', 'id' => base64_encode($game->getDirectory())]) ?>">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title"><strong><?= \app\Application::$app->params['ownTeamName'] ?> vs. <?= $game->getOpponent() ?></strong></h3>
                </div>
                <div class="panel-body">
                    <dl class="dl-horizontal">
                        <dt>Date:</dt><dd><?= $game->getDate() ?></dd>
                        <dt>Event:</dt><dd><?= $game->getEvent() ?></dd>
                        <dt>Location:</dt><dd><?= $game->getDirectory() ?></dd>
                    </dl>
                </div>
            </div>
        </a>
    </div>
<?php endforeach; ?>