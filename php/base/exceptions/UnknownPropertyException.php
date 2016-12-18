<?php
namespace app;

/**
 * Description of UnknownPropertyException
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class UnknownPropertyException extends Exception
{
    public function getName() {
        return 'Unknown Property';
    }
}
