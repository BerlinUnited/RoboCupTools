<?php
namespace app;

/**
 * Description of Response
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class Response extends Component
{
    public $isSent = FALSE;
    public $content = '';
    
    /**
     * @var integer the HTTP status code to send with the response.
     */
    private $_statusCode = 200;
    private $_header;
    
    public function send() {
        if($this->isSent) {
            return;
        }
        $this->sendHeader();
        $this->sendContent();
    }
    
    private function sendHeader() {
        // TODO: implement sendHeaders
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
}