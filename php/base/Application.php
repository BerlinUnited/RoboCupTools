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
 * @property UrlManager $urlmanager the url manager of this application
 * 
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class Application extends Module
{
    /**
     * @var Application the application instance
     */
    public static $app;
    /**
     * @var string[] class map used by the autoloading mechanism.
     * The array keys are the class names (without leading backslashes), and the array values
     * are the corresponding class file paths.
     */
    public static $classMap = [];
    /**
     * @var string[] the registered root namespaces and their corresponding (base) path.
     */
    public static $rootNamespace = [ 'app' => __DIR__ ];
    /**
     * @var string the parameter name, which is used to set and get the requested
     * route in the request.
     */
    public $routeParam = 'r';
    /**
     * @var string the application name.
     */
    public $name = 'VideoLogLabeling';
    /**
     * @var mixed[] the parameter for this application defined as name-value parirs
     */
    public $params = [];

    /**
     * @var UrlManager the read-only url manager component
     */
    private $_urlManager;
    /**
     * @var Request the read-only request component
     */
    private $_request;
    /**
     * @var Response the read-only response component
     */
    private $_response;

    /**
     * Constructor
     * @param String[] $config
     */
    public function __construct($config = []) {
        parent::__construct(NULL, $config);
    }
    
    /**
     * Initializes the module.
     * This method is called after the module is created and initialized with property values
     * given in configuration.
     */
    protected function init() {
        static::$app = $this;
        static::$classMap = require(__DIR__ . '/classes.php');
        static::$rootNamespace['app'] = $this->getBasePath();
        spl_autoload_register(['app\\Application', 'autoload'], true, true);
        ErrorHandler::getInstance()->register();
    }

    /**
     * Class autoload loader.
     * This method is invoked automatically when PHP sees an unknown class.
     * The method will attempt to include the class file according to the following procedure:
     *
     * 1. Search in [[classMap]];
     * 2. If the class is namespaced (e.g. `app\Component`), it will attempt
     *    to include the file simply by using the namespace as path to the file.
     * 
     * @param String $className the fully qualified class name without a leading backslash "\"
     */
    public static function autoload($className) {
        if(isset(static::$classMap[$className])) {
            $classFile = static::$classMap[$className];
        } else {
            $classFile = static::replaceRootNamespace(str_replace('\\', '/', $className)) . '.php';
        }

        if (!file_exists($classFile)) {
            return;
        }

        include $classFile;
    }
    
    /**
     * Replaces the root namespace by its corresponding base path.
     * 
     * @param String $ns the "root" namespace which should be replaced
     * @return String base path of the given root namespace
     */
    public static function replaceRootNamespace($ns) {
        if(($pos = strpos($ns, '/')) !== FALSE) {
            $root = substr($ns, 0, $pos);
            if(isset(self::$rootNamespace[$root])) {
                return self::$rootNamespace[$root] . '/' . substr($ns, $pos+1);
            }
        }
        return static::$basePath . '/' . $ns;
    }

    /**
     * Runs the application.
     * This is the main entrance of an application.
     */
    public function run() {
        $response = $this->handleRequest();
        $response->send();
    }

    /**
     * Returns the URL manager for this application.
     * @return UrlManager the url manager component
     */
    public function getUrlManager() {
        if($this->_urlManager === NULL) {
            $this->_urlManager = new UrlManager();
        }
        return $this->_urlManager;
    }
    
    /**
     * Returns the request component.
     * @return Request the request component
     */
    public function getRequest() {
        if($this->_request === NULL) {
            $this->_request = new Request();
        }
        return $this->_request;
    }
    
    /**
     * Returns the response component.
     * @return Response the response component
     */
    public function getResponse() {
        if($this->_response === NULL) {
            $this->_response = new Response();
        }
        return $this->_response;
    }

    /**
     * Handles the specified request.
     * 
     * @param Request $request the request which should be handled
     * @return \app\Response the resulting response
     */
    public function handleRequest() {
        $r = $this->getRequest()->getRoute();
        
        $module = $this->getModule($r);
        
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
                // route doesn't name a controller - it has to be an action!
                $controller_name = $module->defaultController;
                $action_name = $r;
            }
        } else {
            // use default controller (and default action)
            $controller_name = $module->defaultController;
        }
        
        $controller = $module->getController(ucfirst($controller_name) . 'Controller');
        $result = $controller->runAction($action_name);
        
        // if we got an response object we return that ...
        if ($result instanceof Response) {
            return $result;
        }
        
        // ... otherwise we set the returned result as response content
        $response = $this->getResponse();
        if ($result !== null) {
            $response->content = $result;
        }

        return $response;
    }
    
    /**
     * Returns the value of the named parameter or the default value if the parameter 
     * doesn't exist.
     * The parameter can be set via the params.php in the configuration.
     * 
     * @param String $key the parameter name
     * @param mixed $default the default value, if the parameter doesn't exists
     * @return mixed the corresponding parameter value or the default value
     */
    public function getParam($key, $default = NULL) {
        return isset($this->params[$key]) ? $this->params[$key] : $default;
    }
}
