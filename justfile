default:
    just --list

[unix]
_install-pre-commit:
    #!/usr/bin/env bash
    if ( which pre-commit > /dev/null 2>&1 )
    then
        pre-commit install --install-hooks
    else
        echo "-----------------------------------------------------------------"
        echo "pre-commit is not installed - cannot enable pre-commit hooks!"
        echo "Recommendation: Install pre-commit ('brew install pre-commit')."
        echo "-----------------------------------------------------------------"
    fi

[windows]
_install-pre-commit:
    #!powershell.exe
    Write-Host "Please ensure pre-commit hooks are installed using 'pre-commit install --install-hooks'"

install: (poetry "install") && _install-pre-commit

update: (poetry "install")

poetry *args:
    poetry {{args}}

test *args: (poetry "run" "pytest" "--cov=async_signals" "--cov-report" "term-missing:skip-covered" args)

test-all: (poetry "run" "tox")

ruff *args: (poetry "run" "ruff" "check" "async_signals" "tests" args)

mypy *args: (poetry "run" "mypy" "async_signals" args)

lint: ruff mypy

publish: (poetry "publish" "--build")
