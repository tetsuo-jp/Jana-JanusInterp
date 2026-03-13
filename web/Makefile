
HOST = topps.diku.dk
DESTDIR = /var/www/html/topps/janus-playground/
TUNNEL_PORT = 3022

RSYNC_OPTS = \
	--recursive        \
	--copy-links       \
	--perms            \
	--times            \
	--exclude=Makefile \
	--exclude=programs \
	--exclude="*.swp"  \
	--delete           \
	--verbose

all:
	@echo "Run 'make deploy' to deploy"

check: verify smoke

verify:
	php -l request.php
	php -l execute.php
	php -l load.php
	php -l save.php
	php -l config.php.example

smoke:
	php -r '$$_GET["example"]="fib"; include "load.php";' >/dev/null
	php -r '$$_POST["code"]=file_get_contents("../examples/fib.ja"); $$_POST["intsize"]="arbitrary"; $$_POST["invert"]="off"; include "execute.php";' | grep -q '^0$$'

deploy:
	rsync $(RSYNC_OPTS) . $(HOST):$(DESTDIR)

open-tunnel:
	ssh -f -L $(TUNNEL_PORT):topps.diku.dk:22 ask.diku.dk sleep 5

deploy-tunnel: RSYNC_OPTS += --rsh "ssh -p $(TUNNEL_PORT)"
deploy-tunnel: HOST = budde@localhost
deploy-tunnel: open-tunnel deploy
