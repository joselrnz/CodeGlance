<?php
class Router {
    public function dispatch($path) { return $path; }
    public function add($route) { return true; }
}

function bootstrap() {
    return new Router();
}
