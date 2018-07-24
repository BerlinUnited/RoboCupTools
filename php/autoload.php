<?php

spl_autoload_register(function ($class_name) {
//    var_dump($class_name);
    if(file_exists(__DIR__ . '/' . str_replace('\\', '/', $class_name) . '.php')) {
        require_once __DIR__ . '/' . str_replace('\\', '/', $class_name) . '.php';
    }
},true,true);