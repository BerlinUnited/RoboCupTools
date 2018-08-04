<?php
require_once 'Config.php';
require_once 'Game.php';

class Event
{
    private $is_valid = false;
    private $path;
	private $date;
	private $name;

	private $games = [];

    /**
     * Event constructor.
     * @param $path
     */
	function __construct(SplFileInfo $path) {
        $this->is_valid = preg_match(Config::e('regex'), $path->getFilename(), $matches) === 1  ;
        if ($this->is_valid) {
            $this->path = $path->getRealPath();
            $this->date = DateTimeImmutable::createFromFormat('Y-m-d',$matches[1]);
            $this->name = $matches[2];

            $this->listGames();
        }
	}

    private function listGames() {
        $it = new DirectoryIterator($this->path);
        foreach($it as $file) {
            if (!$file->isDot() && $file->isDir()) {
                $game = new Game($file, $this);
                if ($game->isValid()) {
                    $this->games[$game->getId()] = $game;
                }
            }
        }
    }

    /**
     * @return bool
     */
    public function isValid()
    {
        return $this->is_valid;
    }

    public function hasGames()
    {
        return count($this->games) > 0;
    }

    /**
     * @return array
     */
    public function getGames()
    {
        return $this->games;
    }

    /**
     * @return array
     */
    public function getGame($id)
    {
        if(array_key_exists($id, $this->games)) {
            return $this->games[$id];
        }
        return null;
    }

    /**
     * @return bool|DateTimeImmutable
     */
    public function getDate()
    {
        return $this->date;
    }

    /**
     * @return string
     */
    public function getDateString($format='d.m.Y')
    {
        return $this->date->format($format);
    }

    /**
     * @return string
     */
    public function getName()
    {
        return $this->name;
    }
}