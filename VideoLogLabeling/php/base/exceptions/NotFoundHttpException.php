<?php
namespace app;

/**
 * Description of NotFoundHttpException
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class NotFoundHttpException extends HttpException {
    /**
     * Constructor.
     * @param string $message error message
     * @param integer $code error code
     * @param \Exception $previous The previous exception used for the exception chaining.
     */
    public function __construct($message = null, $code = 0, \Exception $previous = null)
    {
        parent::__construct(404, $message, $code, $previous);
    }
    
    /**
     * @return string the user-friendly name of this exception
     */
    public function getName()
    {
        return 'HttpException ' . $this->statusCode . ' - Not Found';
    }
}
