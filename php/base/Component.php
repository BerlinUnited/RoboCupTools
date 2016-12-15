<?php
namespace app;

/**
 * Description of Component
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
abstract class Component
{
    public function __construct($config = []) {
        foreach ($config as $key => $value) {
            $this->$key = $value;
        }
        $this->init();
    }
    
    protected function init() {
    }

    public function __set($name, $value) {
        $setter = 'set' . $name;
        if (method_exists($this, $setter)) {
            $this->$setter($value);
            return;
        }

        $trace = debug_backtrace();
        trigger_error(
                'Undefined property via __set(): ' . $name . ' ['.$setter.'()]' .
                ' in ' . $trace[0]['file'] .
                ' on line ' . $trace[0]['line'], E_USER_NOTICE);

        return null;
    }

    public function __get($name) {
        $getter = 'get' . $name;
        if (method_exists($this, $getter)) {
            return $this->$getter();
        }

        $trace = debug_backtrace();
        trigger_error(
                'Undefined property via __get(): ' . $name .
                ' in ' . $trace[0]['file'] .
                ' on line ' . $trace[0]['line'], E_USER_NOTICE);

        return null;
    }

    public function __isset($name) {
        $getter = 'get' . $name;
        if (method_exists($this, $getter)) {
            return $this->$getter() !== null;
        } else {
            return false;
        }
    }

    public function __unset($name) {
        $setter = 'set' . $name;
        if (method_exists($this, $setter)) {
            $this->$setter(null);
        }
    }

}
