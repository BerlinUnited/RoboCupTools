<?php
/* @var $this app\View */
/* @var $games[] SoccerGameModel */
/* @var $game SoccerGameModel */

$this->title = \app\Application::$app->name . ' ::: Overview';

$this->registerCssFile('style.css');
/*
$this->registerCss('
body {
    background-image: url(img/naoth-logo.png);
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-position: right bottom;
    background-size: 40%;
 }
');*/

$view = \app\Application::$app->request->get('tile', FALSE) !== FALSE ? 'index-tile' : 'index-list';
?>
<div class="row">
    <div class="col-sm-offset-3 col-sm-6">
        <h1>Overview</h1>
        <div class="row">
            <div class="col-sm-12 text-right">
                <?php
                if(\app\Application::$app->request->get('tile', FALSE) !== FALSE) {
                    echo '<a class="btn btn-default" href="'.\app\Url::to(['',]).'" role="button"><span class="glyphicon glyphicon-list"></span> Table</a>';
                } else {
                    echo '<a class="btn btn-default" href="'.\app\Url::to(['','tile'=>'']).'" role="button"><span class="glyphicon glyphicon-th-large"></span> Tiles</a>';
                }
                ?>
            </div>
        </div>
        <div class="row" id="game_overview">
            <div class="col-sm-12">
                <?=$this->render($view, ['games'=>$games])?>
            </div>
        </div>
    </div>
</div>
<div id="watermark"></div>