#!/usr/bin/python3
# https://gist.github.com/joshbode/569627ced3076931b02f
import os
import json
import sys

import yaml
from typing import Any, IO

class Loader(yaml.SafeLoader):
    """YAML Loader with `!include` constructor."""

    def __init__(self, stream: IO) -> None:
        """Initialise Loader."""

        try:
            self._root = os.path.split(stream.name)[0]
        except AttributeError:
            self._root = os.path.curdir

        super().__init__(stream)


def read_yaml(filename):
    extension = os.path.splitext(filename)[1].lstrip('.')
    with open(filename, 'r') as f:
        if extension in ('yaml', 'yml'):
            return yaml.load(f, Loader)
        elif extension in ('json', ):
            return json.load(f)
        else:
            return ''.join(f.readlines())


def construct_include(loader: Loader, node: yaml.Node) -> Any:
    """Include file referenced at node."""
    filename = os.path.abspath(os.path.join(loader._root, loader.construct_scalar(node)))
    return read_yaml(filename)

def construct_include_dir(loader: Loader, node: yaml.Node) -> Any:
    """Include directory referenced at node."""
    base_object = {}
    reference_root = os.path.abspath(os.path.join(loader._root, loader.construct_scalar(node)))
    # r=root, d=directories, f = files
    for r, d, f in os.walk(reference_root):
        for filename in f:
            if '.yaml' in filename:
                base_object.update(read_yaml(os.path.join(r, filename)))
    return base_object

yaml.add_constructor('!include', construct_include, Loader)
yaml.add_constructor('!include_dir_merge_named', construct_include_dir, Loader)


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        data = yaml.load(f, Loader)
    print(yaml.dump(data))
