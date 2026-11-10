.PHONY: all setup test start stop health clean

all: setup test

setup:
	powershell -ExecutionPolicy Bypass -File scripts/setup.ps1

test:
	powershell -ExecutionPolicy Bypass -File scripts/test.ps1

start:
	powershell -ExecutionPolicy Bypass -File scripts/start.ps1

stop:
	powershell -ExecutionPolicy Bypass -File scripts/stop.ps1

health:
	powershell -ExecutionPolicy Bypass -File scripts/health-check.ps1

clean:
	powershell -Command "Remove-Item -Recurse -Force backend/.pytest_cache, backend/.venv, frontend/.next, frontend/node_modules -ErrorAction SilentlyContinue"
