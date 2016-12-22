<?php
namespace app;

include_once 'Component.php';

/**
 * Description of Module
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
abstract class Module extends Component
{
    /** @var String */
    public static $basePath;
    /** @var String */
    public static $controllerDir = 'controller';
    /** @var String */
    public static $modelDir = 'model';
    /** @var String */
    public static $viewDir = 'view';
    
    /** @var String */
    public $defaultController = 'default';
    /** @var String */
    public $defaultAction = 'index';
    
    /** @var Module */
    public $module;
    /** @var Controller */
    public $activeController;
    /** @var String */
    public $defaultLayoutFile = 'layout.php';

    private $_view;
    
    /**
     * 
     * @param Module $parent
     * @param type $config
     */
    public function __construct($parent, $config = array()) {
        parent::__construct($config);
        $this->module = $parent;
    }
    
    /**
     * Gets called from the parent module.
     */
    abstract public function run();

    /**
     * 
     * @param String $path
     */
    public function setBasePath($path) {
        self::$basePath = $path;
    }
    
    /**
     * 
     * @return String
     */
    public function getBasePath() {
        return self::$basePath;
    }

    /**
     * 
     * @param String $path
     */
    public function setControllerDir($path) {
        self::$controllerDir = $path;
    }
    
    /**
     * 
     * @return String
     */
    public function getControllerDir() {
        return self::$controllerDir;
    }

    /**
     * 
     * @param String $path
     */
    public function setModelDir($path) {
        self::$modelDir = $path;
    }
    
    /**
     * 
     * @return String
     */
    public function getModelDir() {
        return self::$modelDir;
    }

    /**
     * 
     * @param String $path
     */
    public function setViewDir($path) {
        self::$viewDir = $path;
    }
    
    /**
     * 
     * @return String
     */
    public function getViewDir() {
        return self::$viewDir;
    }
    
    public function getView() {
        if($this->_view === NULL) {
            $this->_view = new View();
        }
        return $this->_view;
    }
    

    /**
     * 
     * @param String $name of the controller
     * @return Controller
     * @throws NotFoundHttpException
     */
    public function getController($name) {
        // set default controller if name is empty
        if($name === '' || $name === NULL) {
            $name = $this->defaultController;
        }
        
        // TODO: controller doesn't load correctly in submodules!!!
        $name = $this->getNamespace() . '\\' . $this->getControllerDir() . '\\' . $name;
        
        // TODO: is this the correct logic?!?
        if($this->activeController === NULL) {
            if(class_exists($name)) {
                $this->activeController = new $name($this);
            } else {
                throw new NotFoundHttpException('Couldn\'t find controller class ('.$name.')!'.VarDumper::dumpAsString(__NAMESPACE__));
            }
        }
        return $this->activeController;
    }

    /**
     * Tries to create a Module of the given $name.
     * The name could contain multiple submodules.
     * @param String $name
     * @return Module
     */
    public function getModule(&$name) {
        $module = $this;
        if ($name !== '') {
            $parts = explode('/', $name);
            $class = $this->getNamespace() . '\\modules\\' . $parts[0] . '\\' . ucfirst($parts[0]) . 'Module';
            if (class_exists($class)) {
                unset($parts[0]);
                $name = implode('/', $parts);
                $module = new $class($this);
                $module->getModule($name);
            }
        }
        return $module;
    }

    private function getNamespace() {
        $c = get_called_class();
        return substr($c, 0, strrpos($c, '\\'));
    }
    
}
