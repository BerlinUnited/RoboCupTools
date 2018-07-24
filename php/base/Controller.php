<?php
namespace app;

class Controller extends Component
{
    /**
     * @var Module
     */
    public $module;
    
    /**
     * 
     * @param type $module
     * @param type $config
     */
    public function __construct($module, $config = array()) {
        parent::__construct($config);
        $this->module = $module;
        Application::$app->activeController = $this;
    }
    
    /**
     * 
     * @return type
     */
    public function getId() {
        $id = strtolower(str_replace('Controller','',get_called_class()));
        return substr($id, strrpos($id, '\\')+1);
    }

    /**
     * 
     * @param type $action
     * @return type
     * @throws \Exception
     * @throws NotFoundHttpException
     */
    public function runAction($action) {
        if($action === '') {
            $action = $this->module->defaultAction;
        }
// TODO: check if function exists
// TODO: use inline/extern Actions?
// TODO: use params
        $methodName = 'action' . str_replace(' ', '', ucwords(implode(' ', explode('-', $action))));
        $methodArgs = [];
//        VarDumper::dump($methodName);
        if (method_exists($this, $methodName)) {
            $response = call_user_func_array([$this, $methodName], $methodArgs);
//            VarDumper::dump($response);
//            VarDumper::dump($this->resolveLayout());
            if(is_string($response)) {
                // TODO: return response ??!
                return $response;
            } elseif ($response instanceof Response) {
                return $response;
            } else {
                throw new \Exception('Unknown response type!');
            }
        } else {
            throw new NotFoundHttpException('Unknown action: ' . $action);
        }
    }

    /**
     * 
     * @param type $route
     * @param type $params
     * @return type
     */
    public function createRoute($route, $params) {
        // TODO: create route
        return;
    }
    
    /**
     * @return View
     */
    public function getView() {
        return $this->module->getView();
    }
    
    /**
     * @see View::render()
     * 
     * @param type $view
     * @param type $params
     * @return type
     */
    public function render($view, $params = []) {
        $content = $this->getView()->render($view, $params);
        $layout = $this->resolveLayout();
        if($layout !== NULL) {
            return $this->getView()->renderPhpFile($layout, ['content'=>$content]);
        }
        return $content;
    }
    
    /**
     * Renders a given view in response to an ajax request.
     * 
     * @see View::renderAjax()
     * 
     * @param string $view
     * @param mixed[] $params
     * @return string
     */
    public function renderAjax($view, $params = []) {
        return $this->getView()->renderAjax($view, $params);
    }

    /**
     * 
     * @return String
     */
    private function resolveLayout() {
        $module = $this->module;
        while($module !== NULL) {
            $layout = $module->basePath . '/' . $module->viewDir .'/'. $module->defaultLayoutFile;
            if(file_exists($layout)) {
                return $layout;
            }
            $module = $module->module;
        }
        return NULL;
    }
    
}
