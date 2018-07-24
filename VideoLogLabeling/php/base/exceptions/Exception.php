<?php
namespace app;

/**
 * Description of Exception
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class Exception extends \Exception {
    /**
     * @return string the user-friendly name of this exception
     */
    public function getName()
    {
        return 'Exception';
    }
}
