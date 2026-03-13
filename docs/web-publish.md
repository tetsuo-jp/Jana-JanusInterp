# Web Publish Guide

This repository already contains a browser playground under `web/`. The PHP
backend can now execute the Python interpreter in `src-python/`.

## Requirements

- PHP 8+
- Python 3
- The repository available on the server, or `web/config.php` configured to
  point at the deployed `src-python/` and `examples/` locations
- A writable `web/programs/` directory for saved snippets

## Setup

1. Copy `web/config.php.example` to `web/config.php`.
2. Set:
   - `python_bin`
   - `repo_root`
   - `src_python_dir`
   - `timeout_seconds`
   - `max_code_bytes`
   - `save_enabled`
3. Ensure the web server user can write to `web/programs/`.
4. Publish `web/` as the document root content.
5. Keep the repository checkout, or at minimum `src-python/` and `examples/`, on the same host that serves `web/`.

## What Works

- `execute.php` runs `python3 -m jana_py.cli`
- `load.php?example=<name>` serves examples from `examples/`
- `save.php` stores shared snippets under `web/programs/`
- Existing frontend options for `invert` and `32-bit integers` are supported

## Recommended Smoke Test

Run a local PHP server from the repository root:

```bash
php -S 127.0.0.1:8000 -t web
```

Then open `http://127.0.0.1:8000/` and run the Fibonacci example.

If browser access is inconvenient, the same checks can be done with HTTP:

```bash
curl 'http://127.0.0.1:8000/load.php?example=fib'
curl -X POST 'http://127.0.0.1:8000/execute.php' \
  --data-urlencode "code=$(cat examples/fib.ja)" \
  --data 'intsize=arbitrary' \
  --data 'invert=off'
```

The first line of `execute.php` output is the process exit code. A successful
run returns `0`.

For a quick pre-deploy check from `web/`:

```bash
make check
```

## Deployment Notes

- `web/config.php` is machine-local and should not be committed.
- `web/programs/` must be writable by the web server process.
- `execute.php` shells out to the Python CLI, so disable this feature if your
  hosting environment forbids subprocess execution.
- The server must expose only `web/`; the repository root should stay outside
  the document root.
- Set `save_enabled` to `false` if you do not want public snippet sharing.
- Set `max_code_bytes` conservatively for your host.
- Apply rate limiting and request-size limits at the web server or reverse
  proxy layer.

## Example Configs

Development-style config:

```php
<?php
return array(
  "python_bin" => "python3",
  "repo_root" => realpath(__DIR__ . "/.."),
  "src_python_dir" => realpath(__DIR__ . "/../src-python"),
  "timeout_seconds" => 30,
  "max_code_bytes" => 100000,
  "save_enabled" => true,
);
```

Production-style config:

```php
<?php
return array(
  "python_bin" => "/usr/bin/python3",
  "repo_root" => "/srv/jana/Jana-JanusInterp",
  "src_python_dir" => "/srv/jana/Jana-JanusInterp/src-python",
  "timeout_seconds" => 10,
  "max_code_bytes" => 50000,
  "save_enabled" => false,
);
```
