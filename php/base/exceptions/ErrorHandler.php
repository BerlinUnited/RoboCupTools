<?php
namespace app;

/**
 * Description of ErrorHandler
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class ErrorHandler
{
    /**
     * @var ErrorHandler the insatance of this error handler.
     */
    private static $instances = NULL;
    /**
     * @var \Exception the exception that is being handled currently.
     */
    public $exception;
    
    /**
     * @return ErrorHandler
     */
    final public static function getInstance() {
        if (self::$instances === NULL) {
            self::$instances = new self;
        }
        return self::$instances;
    }

    private function __construct() {}

    private function __clone() {}
    
    /**
     * Register this error handler
     */
    public function register() {
        set_exception_handler([$this, 'handleException']);
        set_error_handler([$this, 'handleError']);
        register_shutdown_function([$this, 'handleFatalError']);
    }
    
    /**
     * Unregisters this error handler by restoring the PHP error and exception handlers.
     */
    public function unregister()
    {
        restore_error_handler();
        restore_exception_handler();
    }
    
    /**
     * Handles uncaught PHP exceptions.
     *
     * This method is implemented as a PHP exception handler.
     *
     * @param \Exception $exception the exception that is not caught
     */
    public function handleException($exception) {
        $this->exception = $exception;
        // disable error capturing to avoid recursive errors while handling exceptions
        $this->unregister();
        try {
            // clear existing (cached/buffered) output
            $this->clearOutput();
            // render Exception
            $this->renderException($exception);
        } catch (\Exception $e) {
            // an other exception could be thrown while displaying the exception
            if(APP_DEBUG) {
                $msg = "An Error occurred while handling another error:\n";
                $msg .= (string) $e;
                $msg .= "\nPrevious exception:\n";
                $msg .= (string) $exception;
                $msg .= "\n\$_SERVER = " . VarDumper::export($_SERVER);
                echo '<pre>' . htmlspecialchars($msg, ENT_QUOTES) . '</pre>';
//                error_log($msg);
            } else {
                echo 'An internal server error occurred.';
            }
        }

        $this->exception = null;
        exit(1);
    }

    /**
     * Handles PHP execution errors such as warnings and notices.
     *
     * This method is used as a PHP error handler. It will simply raise an ErrorException.
     *
     * @param integer $code the level of the error raised.
     * @param string $message the error message.
     * @param string $file the filename that the error was raised in.
     * @param integer $line the line number the error was raised at.
     * @return boolean whether the normal error handler continues.
     *
     * @throws \ErrorException
     */
    public function handleError($code, $message, $file, $line)
    {
        if (error_reporting() & $code) {
            throw new \ErrorException($message, $code, $code, $file, $line);
        }
        return false;
    }
    
    /**
     * Handles fatal PHP errors
     */
    public function handleFatalError()
    {
        $error = error_get_last();
        if (isset($error['type']) && in_array($error['type'], [E_ERROR, E_PARSE, E_CORE_ERROR, E_CORE_WARNING, E_COMPILE_ERROR, E_COMPILE_WARNING])) {
            $this->exception = new \ErrorException($error['message'], $error['type'], $error['type'], $error['file'], $error['line']);
            $this->clearOutput();
            $this->renderException($this->exception);
            exit(1);
        }
    }
    
    /**
     * Removes all output echoed before calling this method.
     */
    public function clearOutput()
    {
        for ($level = ob_get_level(); $level > 0; --$level) {
            if (!@ob_end_clean()) {
                ob_clean();
            }
        }
    }

    /**
     * Renders the exception.
     * @param \Exception $exception the exception to be rendered.
     */
    private function renderException($exception) {
        $response = Application::$app->getResponse();
        
        $response->content = '<pre>' . htmlspecialchars(static::convertExceptionToString($exception), ENT_QUOTES, 'UTF-8') . '</pre>';
        // INFO/TODO: can we render the error/exception as a html page?!?
//        $response->content = $this->renderFile($file, ['exception' => $exception,]);

        if ($exception instanceof HttpException) {
            $response->setStatusCode($exception->statusCode);
        } else {
            $response->setStatusCode(500);
        }

        $response->send();
    }
    
    /**
     * Converts an exception into a simple string.
     * @param \Exception $exception the exception being converted
     * @return string the string representation of the exception.
     */
    public static function convertExceptionToString($exception)
    {
        if(APP_DEBUG) {
            if($exception instanceof \ErrorException) {
                $message = 'Error: ';
            } else {
                $message = "{$exception->getName()}: ";
            }
            $message .= $exception->getMessage();
            $message .= " '" . get_class($exception) . "' with message '{$exception->getMessage()}' \n\nin "
                . $exception->getFile() . ':' . $exception->getLine() . "\n\n"
                . "Stack trace:\n" . $exception->getTraceAsString();
        } else {
            $message = 'Error: ' . $exception->getMessage();
        }
        return $message;
    }
}
