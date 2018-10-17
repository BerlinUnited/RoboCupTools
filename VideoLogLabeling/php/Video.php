<?php

/**
 * Class Video
 */
class Video
{
    /** @var array Container for the sources of this video. */
	private $sources = [];

    /**
     * Video constructor.
     *
     * @param $info
     */
	function __construct($info)
	{
		if(is_array($info)) {
			if (isset($info['sources'])) {
				foreach ($info['sources'] as $file) {
					$this->sources[] = new VideoFile($file);
				}
			}
		} else {
			$this->sources[] = new VideoFile($info);
		}
	}

    /**
     * @param array $sources
     */
    public function addSource($source)
    {
        $this->sources[] = new VideoFile($source);
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
}

/**
 * Class VideoFile
 */
class VideoFile
{
    /** @var string The URI for this video file. */
	private $file;

    /**
     * VideoFile constructor.
     *
     * @param $file
     */
	function __construct($file)
	{
		$this->file = $file;
	}

    /**
     * @return string
     */
    public function getFile()
    {
        return $this->file;
    }

    /**
     * @return string
     */
	public function getMimeType()
	{
		// TODO: do we have other providers?!
		return $this->isUrl() ? 'video/youtube' : mime_content_type($this->file);
	}

    /**
     * @param string $basePath
     * @return string
     */
	public function getUrl($basePath=__DIR__)
	{
		return $this->isUrl() ? $this->file : str_replace($basePath . DIRECTORY_SEPARATOR, '', $this->file);
	}

    /**
     * @return bool
     */
	public function isFile()
	{
		return is_file($this->file);
	}

    /**
     * Returns true if this VideoFile represents an URL, otherwise false.
     *
     * @return bool
     */
	public function isUrl()
	{
		// TODO: check if file is an URL
		return false;
	}

    /**
     * Returns true if file exists or url is available, otherwise false.
     *
     * @return bool
     */
	public function exists()
	{
		// TODO: check URL exists
		return $this->isUrl() ? true : file_exists($this->file);
	}
}