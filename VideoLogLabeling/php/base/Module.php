<?php
namespace app;

include_once 'Component.php';

/**
 * Description of Module
 * 
 * @property string $basePath   the path where this module is located
 * @property string $controllerDir  the directory of the modules controllers
 * @property string $modelDir  the directory of the modules models
 * @property string $viewDir  the directory of the modules views
 * @property View $view  the current view object of this module
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
abstract class Module extends Component
{
    /** @var string */
    public static $controllerDir = 'controller';
    /** @var string */
    public static $modelDir = 'model';
    /** @var string */
    public static $viewDir = 'view';
    
    /** @var string */
    public $defaultController = 'default';
    /** @var string */
    public $defaultAction = 'index';
    
    /** @var Module */
    public $module;
    /** @var Controller */
    public $activeController;
    /** @var string */
    public $defaultLayoutFile = 'layout.php';

    /** @var string */
    private $_basePath;
    /** @var string */
    private $_view;
    
    /**
     * 
     * @param Module $parent
     * @param mixed[] $config
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
     * @param string $path
     */
    public function setBasePath($path) {
        $this->_basePath = $path;
    }
    
    /**
     * 
     * @return string
     */
    public function getBasePath() {
        if($this->_basePath === NULL) {
            $class = new \ReflectionClass($this);
            $this->_basePath = dirname($class->getFileName());
        }
        return $this->_basePath;
    }

    /**
     * 
     * @param string $path
     */
    public function setControllerDir($path) {
        self::$controllerDir = $path;
    }
    
    /**
     * 
     * @return string
     */
    public function getControllerDir() {
        return self::$controllerDir;
    }

    /**
     * 
     * @param string $path
     */
    public function setModelDir($path) {
        self::$modelDir = $path;
    }
    
    /**
     * 
     * @return string
     */
    public function getModelDir() {
        return self::$modelDir;
    }

    /**
     * 
     * @param string $path
     */
    public function setViewDir($path) {
        self::$viewDir = $path;
    }
    
    /**
     * 
     * @return string
     */
    public function getViewDir() {
        return self::$viewDir;
    }
    
    /**
     * 
     * @return View
     */
    public function getView() {
        if($this->_view === NULL) {
            $this->_view = new View();
        }
        return $this->_view;
    }
    

    /**
     * 
     * @param string $name of the controller
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
     * @param string $name
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

    /**
     * 
     * @return string
     */
    private function getNamespace() {
        $c = get_called_class();
        return substr($c, 0, strrpos($c, '\\'));
    }
    
}
