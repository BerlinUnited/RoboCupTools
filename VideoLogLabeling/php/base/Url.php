<?php
namespace app;

/**
 * Some shortcuts for the UrlManager.
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class Url {
    public static function to($url) {
        return Application::$app->getUrlManager()->createUrl($url);
    }
    
    public static function home() {
        return Application::$app->getUrlManager()->getHomeUrl();
    }
}
