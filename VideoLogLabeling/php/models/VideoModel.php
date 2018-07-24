<?php
namespace app\models;

/**
 * Description of VideoModel
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class VideoModel extends \app\Component
{
    /**
     * @var String[]
     */
    public static $supportedFormats = [ 'mp4', 'webm' ];
    /**
     * @var String
     */
    public $defaultFormat = 'webm';
    /**
     * @var String
     */
    public $defaultPreviewImg;
    /**
     * @var String
     */
    private $_file;
    /**
     * @var mixed[]
     */
    protected $_info;
    
    /*
     * Constructor
     */
    public function __construct($file, $config = []) {
        if(!in_array(strtolower(pathinfo($file,PATHINFO_EXTENSION)), static::$supportedFormats)) {
            throw new \app\Exception("Unsupported file format!");
        }
        
        parent::__construct($config);
        $this->_file = [ $file ];
        $this->_info = pathinfo($file);
        $this->_info['extension'] = [ strtolower($this->_info['extension']) ];
        //[ 'dirname' => 'log/2016-01-16-MM-HTWK' 'basename' => 'half1.mp4' 'extension' => 'mp4' 'filename' => 'half1' ]
    }
    
    /**
     * Returns the full video file (incl. path).
     * @return String
     */
    public function __toString() {
        // TODO: return default format
        return $this->_file[0];
    }
    
    protected function getInfo($key, $default=NULL) {
        return isset($this->_info[$key])?$this->_info[$key]:$default;
    }
    
    /**
     * Return the path part of the video file.
     * @return String
     */
    public function getPath() {
        return $this->getInfo('dirname');
    }
    
    /**
     * Returns the name of the video file.
     * @return String
     */
    public function getName() {
        return $this->getInfo('filename');
    }
    
    /**
     * Returns the (available) extensions of the video file.
     * Except a specific format is requested, then this format extension is returned - if it is available!
     * Otherwise NULL will be returned.
     * @return String[]|String|NULL
     */
    public function getExtensions($format = NULL) {
        if(isset($this->_info['extension'])) {
            if($format !== NULL) {
                return array_search($format, $this->_info['extension']) !== FALSE ? strtolower($format) : NULL;
            } else {
                return $this->_info['extension'];
            }
        }
        return [];
    }
    
    /**
     * Checks, whether the video file has an preview image.
     * @return boolean
     */
    public function hasPreview() {
        // TODO: implement "hasPreview()"
        return isset($this->_info['preview']) && !empty($this->_info['preview']);
    }
    
    /**
     * Returns the preview file.
     * If the video file has an preview file, otherwise a default image is returned.
     * @return String
     */
    public function getPreview() {
        return $this->hasPreview() ? $this->_info['preview'] : $this->defaultPreviewImg;
    }
    
    /**
     * Returns the files registered to this video.
     * A video can consist of multiple files with different extension. Therefore
     * the files had to be in the same directory with the same name (only different extension).
     * 
     * @return String[]
     */
    public function getFiles() {
        return $this->_file;
    }
    
    /**
     * Merges to VideoModels if both represents the same video, but with different extensions.
     * The path to and the name must be the same.
     * 
     * @param \app\models\VideoModel $other the video which should be merged with the current
     * @return boolean returns TRUE, if both files represents the same video, FALSe otherwise
     */
    public function addFormat(VideoModel $other) {
        if($this->getPath() === $other->getPath() && $this->getName() === $other->getName() && !empty(array_diff($this->getExtensions(), $other->getExtensions()))) {
            $this->_info['extension'] = array_merge($this->getExtensions(), $other->getExtensions());
            $this->_file = array_merge($this->_file, $other->getFiles());
            return TRUE;
        }
        return FALSE;
    }
}
