<?php
namespace app;

/**
 * Description of Component
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
abstract class Component
{
    /**
     * Constructor.
     * The default implementation does two things:
     *
     * - Initializes the object with the given configuration `$config`.
     * - Call [[init()]].
     *
     * If this method is overridden in a child class, it is recommended that
     *
     * - the last parameter of the constructor is a configuration array, like `$config` here.
     * - call the parent implementation at the end of the constructor.
     *
     * @param array $config name-value pairs that will be used to initialize the object properties
     */
    public function __construct($config = []) {
        foreach ($config as $key => $value) {
            $this->$key = $value;
        }
        $this->init();
    }
    
    /**
     * Initializes the object.
     * This method is invoked at the end of the constructor after the object is initialized with the
     * given configuration.
     */
    protected function init() {
    }

    /**
     * Sets the value of a component property.
     * Therefore it checks if a setter method exists.
     *
     * Do not call this method directly as it is a PHP magic method that
     * will be implicitly called when executing `$component->property = $value;`.
     * 
     * @param string $name the property name
     * @param mixed $value the property value
     * @throws UnknownPropertyException if the property is not defined
     */
    public function __set($name, $value) {
        $setter = 'set' . $name;
        if (method_exists($this, $setter)) {
            $this->$setter($value);
            return;
        } else {
            throw new UnknownPropertyException('Setting unknown property: ' . get_class($this) . '::' . $name);
        }
        return null;
    }

    /**
     * Returns the value of a component property.
     * Therefore it checks if a getter method exists and calls it.
     *
     * Do not call this method directly as it is a PHP magic method that
     * will be implicitly called when executing `$value = $component->property;`.
     * 
     * @param string $name the property name
     * @return mixed the property value
     * @throws UnknownPropertyException if the property is not defined
     */
    public function __get($name) {
        $getter = 'get' . $name;
        if (method_exists($this, $getter)) {
            return $this->$getter();
        } else {
            throw new UnknownPropertyException('Getting unknown property: ' . get_class($this) . '::' . $name);
        }
        return null;
    }
    
    /**
     * Checks if a property is set, i.e. defined and not null.
     * Therefore it checks whether the getter method exists and the value of the
     * property isn't null.
     *
     * Do not call this method directly as it is a PHP magic method that
     * will be implicitly called when executing `isset($component->property)`.
     * 
     * @param string $name the property name
     * @return boolean whether the named property is set
     * @see http://php.net/manual/en/function.isset.php
     */
    public function __isset($name) {
        $getter = 'get' . $name;
        if (method_exists($this, $getter)) {
            return $this->$getter() !== null;
        } else {
            return false;
        }
    }
    
    /**
     * Sets a component property to be null.
     * Therefore it checks whether the setter method exists and sets the value of the
     * property null.
     *
     * Do not call this method directly as it is a PHP magic method that
     * will be implicitly called when executing `unset($component->property)`.
     * 
     * @param string $name the property name
     * @see http://php.net/manual/en/function.unset.php
     */
    public function __unset($name) {
        $setter = 'set' . $name;
        if (method_exists($this, $setter)) {
            $this->$setter(null);
        }
    }
}
