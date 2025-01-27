import importlib.util
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from pydantic_core import SchemaValidator

__all__ = ('Err',)


@dataclass
class Err:
    message: str
    errors: Any = None

    def __repr__(self):
        if self.errors:
            return f'Err({self.message!r}, errors={self.errors!r})'
        else:
            return f'Err({self.message!r})'


@pytest.fixture(params=['python', 'json'])
def py_or_json(request):
    class CustomSchemaValidator:
        def __init__(self, schema):
            self.validator = SchemaValidator(schema)

        def validate_python(self, py_input):
            return self.validator.validate_python(py_input)

        def validate_test(self, py_input):
            if request.param == 'json':
                return self.validator.validate_json(json.dumps(py_input))
            else:
                return self.validator.validate_python(py_input)

        def isinstance_test(self, py_input):
            if request.param == 'json':
                return self.validator.isinstance_json(json.dumps(py_input))
            else:
                return self.validator.isinstance_python(py_input)

    return CustomSchemaValidator


@pytest.fixture
def tmp_work_path(tmp_path: Path):
    """
    Create a temporary working directory.
    """
    previous_cwd = Path.cwd()
    os.chdir(tmp_path)

    yield tmp_path

    os.chdir(previous_cwd)


@pytest.fixture
def import_execute(request, tmp_work_path: Path):
    def _import_execute(source: str, *, custom_module_name: str = None):
        example_bash_file = tmp_work_path / 'example.sh'
        example_bash_file.write_text('#!/bin/sh\necho testing')
        example_bash_file.chmod(0o755)
        (tmp_work_path / 'first/path').mkdir(parents=True, exist_ok=True)
        (tmp_work_path / 'second/path').mkdir(parents=True, exist_ok=True)

        module_name = custom_module_name or request.node.name

        module_path = tmp_work_path / f'{module_name}.py'
        module_path.write_text(source)
        spec = importlib.util.spec_from_file_location('__main__', str(module_path))
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except KeyboardInterrupt:
            print('KeyboardInterrupt')

    return _import_execute


if sys.platform == 'emscripten':
    # we have to stub pytest-benchmark since it can't currently be used with webassembly/emscripten

    @pytest.fixture
    def benchmark():
        def result(func, *args, **kwargs):
            return func(*args, **kwargs)

        return result

    def pytest_configure(config):
        config.addinivalue_line('markers', 'benchmark: pytest-benchmark stub, ignored')

    def pytest_addoption(parser):
        parser.addoption('--benchmark-columns', action='store', default='-', help='pytest-benchmark stub, ignored')
        parser.addoption('--benchmark-group-by', action='store', default='-', help='pytest-benchmark stub, ignored')
        parser.addoption('--benchmark-warmup', action='store', default='-', help='pytest-benchmark stub, ignored')
        parser.addoption('--benchmark-disable', action='store_true', default='-', help='pytest-benchmark stub, ignored')
