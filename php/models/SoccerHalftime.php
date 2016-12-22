<?php
namespace app\models;

/**
 * Description of SoccerHalftime
 *
 * @property SoccerGameModel[] $robots the available robots in this halftime
 * @property String[] $labels the available labels in this halftime
 * @property SoccerVideoModel $video the available video in this halftime
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
     * @return SoccerVideoModel
     */
    public function getVideo() {
        if($this->_video === NULL) {
            $files = glob($this->path.'/../'.DIRECTORY_SEPARATOR.'*half'.$this->id.'*.{MP4,mp4,webm,WEBM}',GLOB_BRACE);
            $this->_video = new SoccerVideo($files);
        }
        return $this->_video;
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
            $r = current($this->getRobots());
            if($r !== FALSE) {
                $this->_labels = $r->getLabels();
            }
        }
        return $this->_labels;
    }
}
