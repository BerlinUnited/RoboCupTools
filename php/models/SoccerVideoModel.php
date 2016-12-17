<?php
namespace app\models;

/**
 * Description of SoccerVideoModel
 * 
 * @property String[] $cameras Id of available cameras (videos)
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class SoccerVideoModel extends \app\Component
{
    public $files;
    
    public function __construct($file, $config = array()) {
        parent::__construct($config);
        if(is_array($file)) {
            foreach ($file as $value) {
                $this->addVideo($value);
            }
        } else {
            $this->addVideo($file);
        }
    }
    
    public function addVideo($file) {
        $extensions = implode('|', VideoModel::$supportedFormats);
        if(preg_match('/half(?P<half>\d+)(_(?P<camera>\d+))?\.('.$extensions.')$/i', $file, $match)) {
            $camera = isset($match['camera'])&&!empty($match['camera']) ? $match['camera'] : '0';
            $video = new VideoModel($file);
            $video_key = $video->getPath().'/'.$video->getName();
            if(isset($this->files[$camera][$video_key])) {
                $this->files[$camera][$video_key]->addFormat($video);
            } else {
                $this->files[$camera][$video_key] = $video;
            }
        }
    }
    
    public function getCameras() {
        return array_keys($this->files);
    }
    
    public function getFirstCamera() {
        return reset($this->files);
    }
}
