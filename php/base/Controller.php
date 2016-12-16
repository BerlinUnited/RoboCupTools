<?php

namespace app;

class Controller extends Component
{
    /**
     * @var Module
     */
    public $module;
    
    public function __construct($module, $config = array()) {
        parent::__construct($config);
        $this->module = $module;
        Application::$app->activeController = $this;
    }
    
    public function getId() {
        $id = strtolower(str_replace('Controller','',get_called_class()));
        return substr($id, strrpos($id, '\\')+1);
    }

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
                return $this->getView()->renderPhpFile($this->resolveLayout(), ['content'=>$response]);
            } else {
                throw new \Exception('Unknown response type!');
            }
        } else {
            throw new NotFoundHttpException('Unknown action: ' . $action);
        }
    }

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
        return $this->getView()->render($view, $params);
    }

    /**
     * 
     * @return String
     */
    private function resolveLayout() {
        return $this->module->basePath . '/' . $this->module->viewDir .'/'. $this->module->defaultLayoutFile;
    }
    
}
