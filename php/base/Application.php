<?php
namespace app;
include_once 'Module.php';

/**
 * This constant defines the framework installation directory.
 */
defined('APP_PATH') or define('APP_PATH', __DIR__);
/**
 * This constant defines whether the application should be in debug mode or not. Defaults to false.
 */
defined('APP_DEBUG') or define('APP_DEBUG', FALSE);

/**
 * Description of Application
 *
 * @property Request $request the current request
 * @property Response $response the current Response
 * 
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class Application extends Module {

    /** @var Application */
    public static $app;
    /* @var string[] */
    public static $classMap = [];
    
    /* @var string */
    public $routeParam = 'r';
    /** @var mixed[] */
    public $params = [];

    /* @var UrlManager */
    private $_urlManager;
    /* @var Request */
    private $_request;
    /* @var Response */
    private $_response;

    
    public function __construct($config = []) {
        parent::__construct(NULL, $config);
    }
    
    protected function init() {
        static::$app = $this;
        static::$classMap = require(__DIR__ . '/classes.php');
        spl_autoload_register(['app\\Application', 'autoload'], true, true);
        ErrorHandler::getInstance()->register();
    }

    public static function autoload($className) {
        if(isset(static::$classMap[$className])) {
            $classFile = static::$classMap[$className];
        } elseif(Helper::endsWith($className, 'Controller')) {
            $classFile = self::$basePath . '/' . self::$controllerDir . '/' . $className . '.php';
        } elseif(Helper::endsWith($className, 'Model')) {
            $classFile = self::$basePath . '/' . self::$modelDir . '/' . $className . '.php';
        } else {
            return;
        }
//        var_dump($classFile);
//        var_dump(file_exists($classFile));

        if (!file_exists($classFile)) {
            return;
        }

        include $classFile;
    }

    public function run() {
        $response = $this->handleRequest();
        $response->send();
    }

    /**
     * @return UrlManager
     */
    public function getUrlManager() {
        if($this->_urlManager === NULL) {
            $this->_urlManager = new UrlManager($this);
        }
        return $this->_urlManager;
    }
    
    /**
     * @return Request
     */
    public function getRequest() {
        if($this->_request === NULL) {
            $this->_request = new Request($this);
        }
        return $this->_request;
    }
    
    /**
     * @return Response
     */
    public function getResponse() {
        if($this->_response === NULL) {
            $this->_response = new Response($this);
        }
        return $this->_response;
    }

    /**
     * 
     * @param Request $request
     * @return \app\Response
     */
    public function handleRequest() {
        $r = $this->getRequest()->getRoute();
        
        // TODO: resolve the correct module
        $module = $this;
//        $module = $this->getModule($name);
        
        $action_name = '';
        if(strpos($r, '/') !== FALSE) {
            // route defines controller and action
            list($controller_name, $action_name) = split('/', $r, 2);
        } elseif ($r !== '') {
            // route contains controller xor action
            if(class_exists((ucfirst($r) . 'Controller'))) {
                // controller takes precedence over action
                $controller_name = $r;
            } else {
                // route doesn't name a controler - it has to be an action!
                $controller_name = $module->defaultController;
                $action_name = $r;
            }
        } else {
            // use default controller (and default action)
            $controller_name = $module->defaultController;
        }
        
        $controller = $module->getController(ucfirst($controller_name) . 'Controller');
        $result = $controller->runAction($action_name);
        
        if ($result instanceof Response) {
            return $result;
        }
        
        $response = $module->getResponse();
        if ($result !== null) {
            $response->content = $result;
        }

        return $response;
    }
    
    public function getParam($key, $default = NULL) {
        return isset($this->params[$key]) ? $this->params[$key] : $default;
    }
}
