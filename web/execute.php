<?php

$dir = dirname(__FILE__);
require_once $dir . "/request.php";
$default_config = array(
  "python_bin" => "python3",
  "repo_root" => realpath($dir . "/.."),
  "src_python_dir" => realpath($dir . "/../src-python"),
  "timeout_seconds" => 30,
  "max_code_bytes" => 100000,
);
$config_path = $dir . "/config.php";
$config = file_exists($config_path) ? array_merge($default_config, require $config_path) : $default_config;

$prog_text = request_value(INPUT_POST, "code");
$intsize = request_value(INPUT_POST, "intsize");
$invert_raw = request_value(INPUT_POST, "invert");
$invert = in_array($invert_raw, array(true, "1", 1, "true", "on"), true);

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

if ($intsize !== null && !preg_match("/^(arbitrary|32)$/", $intsize)) {
    header("HTTP/1.1 400 Bad Request");
    echo "bad intsize";
    exit;
}

if (!$config["src_python_dir"] || !is_dir($config["src_python_dir"])) {
    header("HTTP/1.1 500 Internal Server Error");
    echo "src-python directory is not configured";
    exit;
}

if (!function_exists("proc_open")) {
    header("HTTP/1.1 500 Internal Server Error");
    echo "proc_open is disabled";
    exit;
}

$jana_flags = array("-t" . intval($config["timeout_seconds"]));
if ($intsize === "32") {
  array_push($jana_flags, "-m32");
}
if ($invert) {
  array_push($jana_flags, "-i");
}
array_push($jana_flags, "-");

$cmd_parts = array_merge(
  array($config["python_bin"], "-m", "jana_py.cli"),
  $jana_flags
);
$quoted_cmd = implode(" ", array_map("escapeshellarg", $cmd_parts));

$cwd = sys_get_temp_dir();
$descriptorspec = array(
    0 => array("pipe", "r"),
    1 => array("pipe", "w"),
    2 => array("pipe", "w"),
);
$env = $_ENV;
$env["PYTHONPATH"] = $config["src_python_dir"];

$process = proc_open($quoted_cmd, $descriptorspec, $pipes, $cwd, $env);

if (!is_resource($process)) {
    header("HTTP/1.1 500 Internal Server Error");
    echo "failed to start python backend";
    exit;
}

fwrite($pipes[0], $prog_text);
fclose($pipes[0]);

$stdout = stream_get_contents($pipes[1]);
fclose($pipes[1]);

$stderr = stream_get_contents($pipes[2]);
fclose($pipes[2]);

$return_value = proc_close($process);

echo $return_value . "\n";
if ($return_value === 124) {
  echo "Execution timed out!\n";
}
echo $stdout;
if ($stderr !== "") {
  echo $stderr;
}

?>
