<?php
namespace app;

/**
 * Description of Request
 * 
 * @property boolean $isAjax if the current request is an ajax request
 * @property boolean $isGet if the current request is an GET request
 * @property boolean $isPost if the current request is an POST request
 * @property string $route the current (requested) route of this request (without trailing "/")
 * @property string $type the type of the request (GET, PUT, ...)
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
          VarDumper::dump('$_REQUEST: ');
          VarDumper::dump($_REQUEST);
          VarDumper::dump('$_ENV: ');
          VarDumper::dump($_ENV);
          VarDumper::dump('$_SERVER: ');
          VarDumper::dump($_SERVER);
          VarDumper::dump('$_GET: ');
          VarDumper::dump($_GET);
          VarDumper::dump('$_POST: ');
          VarDumper::dump($_POST);
         //*/
//        return [];
    }
    
    /**
     * 
     * @return string
     */
    public function getRoute() {
        $route = isset($_GET[Application::$app->routeParam]) ? 
                $_GET[Application::$app->routeParam] : '';
        return trim($route,'/');
    }
    
    /**
     * 
     * @return string
     */
    public function getType() {
        if (isset($_SERVER['REQUEST_METHOD'])) {
            return strtoupper($_SERVER['REQUEST_METHOD']);
        }
        return 'GET';
    }
    
    /**
     * 
     * @return boolean
     */
    public function getIsGet() {
        return $this->getType() === 'GET';
    }
    
    /**
     * 
     * @return boolean
     */
    public function getIsPost() {
        return $this->getType() === 'POST';
    }
    
    /**
     * 
     * @return boolean
     */
    public function getIsAjax() {
        return isset($_SERVER['HTTP_X_REQUESTED_WITH']) && $_SERVER['HTTP_X_REQUESTED_WITH'] === 'XMLHttpRequest';
    }
    
    /**
     * 
     * @param type $name
     * @param type $default
     * @return string
     */
    public function get($name, $default = NULL) {
        // TODO: escape something?!? could direct access be an security issue?!
        if($name === NULL) {
            return $_GET;
        }
        return isset($_GET[$name]) ? $_GET[$name] : $default;
    }

    public function post($name = NULL, $default = NULL) {
        // TODO: escape something?!? could direct access be an security issue?!
        if($name === NULL) {
            return $_POST;
        }
        return isset($_POST[$name]) ? $_POST[$name] : $default;
    }
}
