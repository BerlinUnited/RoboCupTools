<?php
namespace app;

/**
 * Description of Request
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class Request extends Component
{
    private $_route;
    private $_module;
    private $_controller;
    private $_action;
    
    protected function init() {
        /**
         * action
         * controller/action
         * module/controller/action
         * module/controller
         * module/controller
         * module/module/controller
         * module
         * module/module
         */
        /*
        // TODO: if there's a module with the given id/name, create the module ...
        $module = NULL; //$this->_parent->getModule($id);
        if ($module === NULL) {
            $module = $this->module();
        }
        */
 
        /*
          VarDumper::dump($_REQUEST);
          VarDumper::dump($_ENV);
          VarDumper::dump($_SERVER);
          VarDumper::dump($_GET);
          VarDumper::dump(__FILE__);
         //*/
//        return [];
    }
    
    public function getRoute() {
        $route = isset($_GET[Application::$app->routeParam]) ? 
                $_GET[Application::$app->routeParam] : '';
        return trim($route,'/');
    }
    
    public function getType() {
        return 'GET';
    }
    
    public function get($name) {
        // TODO: escape something?!? could direct access be an security issue?!
        return isset($_GET[$name]) ? $_GET[$name] : NULL;
    }

}
