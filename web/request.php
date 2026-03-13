<?php

function request_value($method, $name) {
    $source = $method === INPUT_GET ? $_GET : $_POST;
    $value = filter_input($method, $name, FILTER_UNSAFE_RAW);
    if ($value !== null && $value !== false) {
        return $value;
    }
    return array_key_exists($name, $source) ? $source[$name] : null;
}

?>
