<?php
namespace app\controller;

use app\Application;
use app\models\SoccerGame;

class DefaultController extends \app\Controller
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
            if(($model = SoccerGame::checkAndCreate($path . "/" . $value)) !== NULL) {
                $result[] = $model;
            }
        }
        return $result;
    }

    // TODO: bind action params ...
    public function actionView() {
        $game_id = \app\Application::$app->request->get('id');
        $half_id = \app\Application::$app->request->get('half');
        $label = \app\Application::$app->request->get('name', 'new');
        $video = \app\Application::$app->request->get('video');
        
        if($game_id === NULL || ($game = SoccerGame::checkAndCreate(base64_decode($game_id))) === NULL) {
            throw new \app\NotFoundHttpException('Unknown game id!');
        }
        if($half_id === NULL || ($half = $game->getHalf($half_id)) === NULL) {
            throw new \app\NotFoundHttpException('Unknown halftime id!');
        }
        
        return $this->render('view', [
            'game'=>$game,
            'half'=>$half,
            'label'=>$label,
            'video'=>$video,
        ]);
    }
    
    public function actionSave() {
        // return response as JSON
        Application::$app->response->format = \app\Response::FORMAT_JSON;
        $result = [];
        // only ajax & post request allowed!
        if (Application::$app->request->isAjax && Application::$app->request->isPost) {
            // replace whitespaces with underscore
            $tag = preg_replace('/\s+/', '_', Application::$app->request->post('tag'));
            $file = preg_replace('/\s+/', '_', Application::$app->request->post('file'));
            // TODO: should we "verify" the data?!?
            $data = Application::$app->request->post('data');
            
            if (empty($tag)) {
                $result = [ 'error' => 'a tag need to be set' ];
            } elseif (preg_match(\app\models\SoccerRobotLogs::$regex_json, $file, $match)) {
                $path = preg_replace('/labels.*\.json$/', 'labels-'.$tag.'.json', $file);
                $jsonFile = fopen($path, "w");
                if ($jsonFile) {
                    fwrite($jsonFile, $data);
                    fclose($jsonFile);
                    $result = [ 'success' => 'writing to ' . $path . ' -- ' . $jsonFile . ' ' . $data ];
                } else {
                    $result = [ 'error' => 'writing to ' . $path ];
                }
            } else {
                $result = [ 'error' => 'invalid json file' ];
            }
        } else {
            $result = [ 'error' => 'invalid request' ];
        }
        return json_encode($result);
    }

}