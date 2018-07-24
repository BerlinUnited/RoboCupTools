<?php
namespace app\models;

/**
 * Description of SoccerHalftime
 *
 * @property SoccerGameModel[] $robots the available robots in this halftime
 * @property String[] $labels the available labels in this halftime
 * @property SoccerVideo $video the available video in this halftime
 * 
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class SoccerHalftime extends \app\Component
{
    /** 
     * @var String halftime
     */
    public $id;
    public $path;
    public $comment;
    private $_robots;
    private $_labels;
    private $_video;
    
    public function __construct($id, $path, $comment = '', $config = []) {
        parent::__construct($config);
        $this->id = $id;
        $this->path = $path;
        $this->comment = $comment;
    }
    
    /**
     * 
     * @return SoccerVideoModel[]
     */
    public function getVideo() {
        if($this->_video === NULL) {
            $this->_video = [];
            $files = glob($this->path.'/../'.DIRECTORY_SEPARATOR.'*half'.$this->id.'*.{MP4,mp4,webm,WEBM}',GLOB_BRACE);
            foreach ($files as $file) {
                $video = new SoccerVideo($file);
                if(isset($this->_video[$video->getId()])) {
                    $this->_video[$video->getId()]->addFormat($video);
                } else {
                    $this->_video[$video->getId()] = $video;
                }
            }
        }
        return $this->_video;
    }
    
    public function getVideoById($id) {
        $videos = $this->getVideo();
        return isset($videos[$id]) ? $videos[$id] : NULL;
    }
    
    public function getFirstVideo() {
        return array_values($this->getVideo())[0];
    }
    
    /**
     * 
     * @return SoccerGameLogModel[]
     */
    public function getRobots() {
        if($this->_robots === NULL) {
            foreach (scandir($this->path) as $dir) {
                if ($dir == "." || $dir == "..") {
                    continue;
                }
                $this->_robots[$dir] = new SoccerRobotLogs($this->path . DIRECTORY_SEPARATOR . $dir);
            }
        }
        return $this->_robots;
    }
    
    /**
     * 
     * @return String[]
     */
    public function getLabels() {
        if($this->_labels === NULL) {
            $this->_labels = [];
            $robots = $this->getRobots();
            foreach ($robots as $robot) {
                $this->_labels += $robot->getLabels();
            }
        }
        return $this->_labels;
    }
}
