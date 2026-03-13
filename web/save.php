<?php

$dir = dirname(__FILE__);
require_once $dir . "/request.php";
$default_config = array(
    "save_enabled" => true,
    "max_code_bytes" => 100000,
);
$config_path = $dir . "/config.php";
$config = file_exists($config_path) ? array_merge($default_config, require $config_path) : $default_config;
$programs_dir = $dir . "/programs";
if (!is_dir($programs_dir)) {
    mkdir($programs_dir, 0775, true);
}

if (!$config["save_enabled"]) {
    header("HTTP/1.1 403 Forbidden");
    echo "sharing disabled";
    exit;
}

$prog_text = request_value(INPUT_POST, "code");
if ($prog_text === null || $prog_text === false) {
    header("HTTP/1.1 400 Bad Request");
    echo "missing code";
    exit;
}

if (strlen($prog_text) > intval($config["max_code_bytes"])) {
    header("HTTP/1.1 400 Bad Request");
    echo "code too large";
    exit;
}

$hash = substr(sha1($prog_text), 0, 8);

$res = file_put_contents($programs_dir . "/$hash.ja", $prog_text);

if ($res === FALSE) {
    header("HTTP/1.1 500 Internal Server Error");
    exit;
} else {
    echo $hash;
}

?>
