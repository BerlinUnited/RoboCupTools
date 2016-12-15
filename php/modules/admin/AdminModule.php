<?php
namespace modules\admin;

/**
 * Description of AdminModule
 *
 * @author Philipp Strobel <philippstrobel@posteo.de>
 */
class AdminModule extends \app\Module
{
    protected function init() {
        \app\VarDumper::dump("test");
    }
    public function run() {
        
    }
}
