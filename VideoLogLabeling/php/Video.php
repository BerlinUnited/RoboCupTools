<?php
require_once 'Config.php';
require_once 'Game.php';

/**
 * Class Video
 */
class Video
{
	/** @var Game The game this video belongs to. */
	private $game;
    /** @var array Container for the sources of this video. */
	private $sources = [];
	/** @var float The synchronisation point for this video. */
	private $syncpoint = 0.0;

    /**
     * Video constructor.
     *
     * @param $game
     * @param $info
     */
	function __construct(Game $game, $info)
	{
		$this->game = $game;
		if(is_array($info)) {
			if (isset($info['sources'])) {
				foreach ($info['sources'] as $file) {
					$this->sources[] = new VideoFile($this, $file);
				}
			}
			if (isset($info['sync'])) {
				$this->syncpoint = $info['sync'];
			}
		} else {
			$this->sources[] = new VideoFile($this, $info);
		}
	}

    /**
     * @param array $sources
     */
    public function addSource($source)
    {
        $this->sources[] = new VideoFile($this, $source);
    }

    /**
     * Returns the first existing source or null if there's none.
     * If a mimetype is given, the first existing source with this mimetype is returned or null if there's none.
     *
     * @param string $mime
     * @return VideoFile|null
     */
	public function getFile($mime='')
	{
		foreach ($this->sources as $video) {
            /* @var VideoFile $video */
		    if($video->exists() && (empty($mime) || $video->getMimeType() === $mime)) {
				return $video;
			}
		}
		return NULL;
	}

    /**
     * Returns the URL of the first existing source or null if there's none.
     * If a mimetype is given, the URL of the first existing source with this mimetype is returned or null if there's none.
     *
     * @param string $basePath
     * @param string $mime
     * @return string|null
     */
	public function getUrl($basePath=__DIR__, $mime='')
	{
        foreach ($this->sources as $video) {
            /* @var VideoFile $video */
            if($video->exists() && (empty($mime) || $video->getMimeType() === $mime)) {
                return $video->getUrl($basePath);
            }
        }
		return NULL;
	}

    /**
     * Return all existing video sources.
     *
     * @return array
     */
	public function getSources()
	{
		return array_filter($this->sources, function($v){ return $v->exists(); });
	}

    /**
     * Returns all available mimetypes.
     *
     * @return array
     */
	public function getMimeTypes()
	{
		return array_unique(array_map(function($v){return $v->getMimeType();}, $this->sources));
	}

    /**
     * Checks, whether a given mimetype is available.
     *
     * @param string $mime
     * @return bool
     */
	public function hasMimeType($mime='')
	{
		foreach ($this->sources as $video) {
            /* @var VideoFile $video */
			if ($video->getMimeType() === $mime) {
				return true;
			}
		}
	}

    /**
     * @param $source
     * @return bool
     */
    public function hasSource($source)
    {
        foreach ($this->sources as $video) {
            /* @var VideoFile $video */
            if($source === $video->getFile()) {
                return true;
            }
        }
        return false;
    }

    /**
     * @return string
     */
    public function getPath()
    {
    	return $this->game->getPath() . DIRECTORY_SEPARATOR . Config::g('dirs')['video'];
    }

    /**
     * @return float
     */
    public function getSyncPoint()
    {
    	return $this->syncpoint;
    }
}

/**
 * Class VideoFile
 */
class VideoFile
{
	/** @var Video The Video this file belongs to. */
	private $video;
    /** @var string The URI for this video file. */
	private $uri;
    /** @var string The URI type. */
	private $type;

    /**
     * VideoFile constructor.
     *
     * @param $video
     * @param $file
     */
	function __construct(Video $video, $file, $type = null)
	{
		$this->video = $video;
        // videos in info file are without the path
		$this->uri = strpos($file, DIRECTORY_SEPARATOR) === false ? $video->getPath() . DIRECTORY_SEPARATOR . $file : $file;

		$this->type = strtolower($type !== null ? $type : ($this->isUrl()?'url':pathinfo($file, PATHINFO_EXTENSION)));
	}

    /**
     * @return string
     */
    public function getFile()
    {
        return $this->uri;
    }

    /**
     * Returns the type of this video file.
     * This is generally the extension of the file, but could also be something manually set (eg. 'url').
     *
     * @return string
     */
    public function getType()
    {
        return $this->type;
    }

    /**
     * @return string
     */
	public function getMimeType()
	{
		// TODO: do we have other providers?!
		return $this->isUrl() ? 'video/youtube' : mime_content_type($this->uri);
	}

    /**
     * @param string $basePath
     * @return string
     */
	public function getUrl($basePath=__DIR__)
	{
		return $this->isUrl() ? $this->uri : str_replace($basePath . DIRECTORY_SEPARATOR, '', $this->uri);
	}

    /**
     * @return bool
     */
	public function isFile()
	{
		return is_file($this->uri);
	}

    /**
     * Returns true if this VideoFile represents an URL, otherwise false.
     *
     * @return bool
     */
	public function isUrl()
	{
		return filter_var($this->uri, FILTER_VALIDATE_URL) !== FALSE;
	}

    /**
     * Returns true if file exists or it is an url, otherwise false.
     * NOTE: availability of the url isn't checked.
     *
     * @return bool
     */
	public function exists()
	{
		return $this->isUrl() || file_exists($this->uri);
	}
}