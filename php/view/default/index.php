<?php
/* @var $this app\View */
/* @var $game SoccerGameLogModel */
$this->title = 'VideoLogLabeling ::: Overview';
$this->registerCss('
    #game_overview .dl-horizontal dt { width: 80px; }
    #game_overview .dl-horizontal dd { margin-left: 100px; }
');
?>
<div class="row">
    <div class="col-sm-offset-3 col-sm-6">
        <h1>Overview</h1>
        <div class="row" id="game_overview">
            <?php foreach ($games as $game) : ?>
                <div class="col-sm-6 col-lg-4">
                    <a href="<?= \app\Url::to(['/default/view', 'id' => base64_encode($game->getDirectory())]) ?>">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3 class="panel-title"><strong><?=\app\Application::$app->params['ownTeamName']?> vs. <?= $game->getOpponent() ?></strong></h3>
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
        </div>
    </div>
</div>