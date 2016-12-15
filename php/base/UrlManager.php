<?php
namespace app;

/**
 * Description of UrlManager
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class UrlManager extends Component {
    
    public function createUrl($url) {
//        VarDumper::dump('asdf');
        // create route
        if(is_array($url)) {
            $this->normalizeRoute($url[0]);
            // TODO: create url route
            $route = '?'.Application::$app->routeParam.'='.$url[0];
            unset($url[0]);
            foreach ($url as $key => $value) {
                $route .= '&'.$key.'='.$value;
            }
            return $route;
        }
        // interpret as normal url
        return $url;
    }
    
    private function normalizeRoute(&$route) {
        // TODO: route normalization
        if($route === '') {
            $route = Application::$app->request->getRoute();
        }
    }
    
    public function getHomeUrl() {
        // TODO: determine correct script/homeUrl!?
        return 'index.php';
    }
}
