<?php

$dir = dirname(__FILE__);
require_once $dir . "/request.php";
$default_config = array(
  "repo_root" => realpath($dir . "/.."),
);
$config_path = $dir . "/config.php";
$config = file_exists($config_path) ? array_merge($default_config, require $config_path) : $default_config;

$example = request_value(INPUT_GET, "example");
$repo_root = $config["repo_root"];

if ($example !== null) {
    if (!preg_match("/^[a-zA-Z0-9-]+$/", $example)) {
        header("HTTP/1.1 400 Bad Request");
        echo "bad example";
        exit;
    }
    $example_path = $repo_root . "/examples/$example.ja";
    $res = file_get_contents($example_path);
    if ($res === FALSE) {
        header("HTTP/1.1 404 Not Found");
        exit;
    }
    header("Content-Type: text/janus");
    echo $res;
    exit;
}

$hash = request_value(INPUT_GET, "hash");

if (!$hash || !preg_match("/^[a-z0-9]{8}$/", $hash)) {
    header("HTTP/1.1 400 Bad Request");
    echo "bad hash";
    exit;
}

$res = file_get_contents($dir . "/programs/$hash.ja");

if ($res === FALSE) {
    header("HTTP/1.1 404 Not Found");
    exit;
} else {
    header("Content-Type: text/janus");
    echo $res;
}

?>
