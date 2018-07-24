<?php
namespace app\models;

/**
 * Description of SoccerVideo
 * 
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class SoccerVideo extends VideoModel
{
    public function __construct($file, $config = array()) {
        $extensions = implode('|', static::$supportedFormats);
        if(preg_match('/half(?P<half>\d+)(_(?P<camera>\d+))?\.('.$extensions.')$/i', $file, $match)) {
            parent::__construct($file, $config);
            $this->_info['id'] = md5($this->getPath().'/'.$this->getName());
            $this->_info['camera'] = isset($match['camera'])&&!empty($match['camera']) ? $match['camera'] : '0';
        } else {
            throw new Exception("Invalid file nameing!");
        }
    }
    
    public function getId() {
        return $this->getInfo('id');
    }
    
    public function getCamera() {
        return $this->getInfo('camera');
    }
}
