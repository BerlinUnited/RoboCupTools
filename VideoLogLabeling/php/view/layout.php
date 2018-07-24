<?php
$this->beginPage();
?>
<!DOCTYPE html>
<html lang="en" ng-app="test">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title><?=$this->title?></title>
        <link rel="stylesheet" href="lib/bootstrap/css/bootstrap.min.css" />
        <script src="lib/player/jquery.js"></script>
        <script src="lib/bootstrap/js/bootstrap.min.js"></script>
        <style>body { padding-top: 50px; }</style>
        <?php $this->head(); ?>
    </head>
    <body>
        <nav class="navbar navbar-inverse navbar-fixed-top">
            <div class="container-fluid">
                <!-- Brand and toggle get grouped for better mobile display -->
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
                        <span class="sr-only">Toggle navigation</span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </button>
                    <a class="navbar-brand" href="<?= \app\Url::home() ?>">
                        <?=(!empty(\app\Application::$app->getParam('logo'))?'<img alt="Brand" src="'.\app\Application::$app->getParam('logo').'" height="100%" class="pull-left"> &nbsp;':'')?>
                        <?=\app\Application::$app->name?>
                    </a>
                </div>

                <!-- Collect the nav links, forms, and other content for toggling -->
                <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
                    <ul class="nav navbar-nav navbar-right">
                        <li><a href="#">Link</a></li>
                        <li class="dropdown">
                            <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Dropdown <span class="caret"></span></a>
                            <ul class="dropdown-menu">
                                <li><a href="#">Action</a></li>
                                <li><a href="#">Another action</a></li>
                                <li><a href="#">Something else here</a></li>
                                <li role="separator" class="divider"></li>
                                <li><a href="#">Separated link</a></li>
                            </ul>
                        </li>
                    </ul>
                </div><!-- /.navbar-collapse -->
            </div><!-- /.container-fluid -->
        </nav>
        <?php $this->beginBody() ?>
        <div class="container-fluid" ng-controller="MainController">
            <?= $content ?>
        </div>
    </div>
    <?php $this->endBody() ?>
</body>
</html>
<?php $this->endPage() ?>