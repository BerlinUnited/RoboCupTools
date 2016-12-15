<?php

use app\Application;

class DefaultController extends app\Controller
{
    public function actionIndex() {
        $games = [];
        $log_dir = Application::$app->getParam('log_dir');
        
        if(file_exists($log_dir) && is_dir($log_dir)) {
            $games = $this->list_logs($log_dir);
        }
        
        return $this->render('index', ['games'=>$games]);
    }
    
    private function list_logs($path) {
        $result = [];
        foreach (scandir($path) as $key => $value) {
            if ($value == "." || $value == "..") {
                continue;
            }
            if(($model = SoccerGameModel::checkAndCreate($path . "/" . $value)) !== NULL) {
                $result[] = $model;
            }
        }
        return $result;
    }

    // TODO: bind action params ...
    public function actionView() {
        $game_id = \app\Application::$app->request->get('id');
        if($game_id === NULL || ($game = SoccerGameModel::checkAndCreate(base64_decode($game_id))) === NULL) {
            throw new app\NotFoundHttpException('Unknown game id!');
        }
        return $this->render('view', ['game'=>$game]);
    }

}