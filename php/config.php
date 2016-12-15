<?php

$params = require(__DIR__ . '/params.php');

return [
    'basePath' => __DIR__,
    'controllerDir'=> 'controller',
    'modelDir'     => 'models',
    'viewDir'      => 'view',
    'params' => $params,
];