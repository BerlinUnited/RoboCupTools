<?php
namespace app;

/**
 * Description of Response
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class Response extends Component
{
    
    const FORMAT_RAW = 'raw';
    const FORMAT_HTML = 'html';
    const FORMAT_JSON = 'json';
    
    public $isSent = FALSE;
    public $content = '';
    
    /**
     * @var integer the HTTP status code to send with the response.
     */
    private $_statusCode = 200;
    private $_header = [];
    
    public function send() {
        if($this->isSent) {
            return;
        }
        $this->sendHeader();
        $this->sendContent();
    }
    
    private function sendHeader() {
        // TODO: implement sendHeaders
        foreach ($this->_header as $key => $value) {
            header("$key: $value");
        }
        http_response_code($this->getStatusCode());
    }
    
    private function sendContent() {
        echo $this->content;
    }
    
    /**
     * Sets the response status code.
     * @param int $code the status code
     */
    public function setStatusCode($code) {
        if ($code === null) {
            $code = 200;
        }
        $this->_statusCode = (int) $code;
    }
    
    /**
     * @return int the HTTP status code to send with the response.
     */
    public function getStatusCode()
    {
        return $this->_statusCode;
    }
    
    public function setHeader($key, $value) {
        $this->_header[$key] = $value;
    }
    
    public function setFormat($format) {
        // TODO: make it configurable which charset should be used?!
        switch ($format) {
            case self::FORMAT_RAW:
                // nothing is set on raw
                break;
            case self::FORMAT_JSON:
                $this->_header['Content-Type'] = 'application/json; charset=UTF-8';
                break;
            case self::FORMAT_HTML:
            default:
                $this->_header['Content-Type'] = 'text/html; charset=UTF-8';
                break;
        }
    }
}