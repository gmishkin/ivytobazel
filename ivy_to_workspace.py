#!/usr/bin/env python3

"""
ivy_to_workspace.py

Usage:
    ivy_to_workspace.py <file>
"""

import ast
import re
import sys
import xml.etree.ElementTree as ET

from docopt import docopt
import astunparse

WORKSPACE_NAME_REPLACEMENT_PATTERN = re.compile('[^a-zA-Z0-9_]')

def get_dependency_workspace_name(dependency):
    return '{}_{}'.format(
        WORKSPACE_NAME_REPLACEMENT_PATTERN.sub('_', dependency.get('org')),
        WORKSPACE_NAME_REPLACEMENT_PATTERN.sub('_', dependency.get('name'))
    )

def get_dependency_artifact(dependency):
    return '{}:{}:{}'.format(
        dependency.get('org'),
        dependency.get('name'),
        dependency.get('rev')
    )

def convert_ivy_deps(file):
    dependencies = ast.Module()
    dependencies.body = []

    jars_macro = ast.FunctionDef(args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), decorator_list=[])
    jars_macro.name = 'ivy_jars'
    jars_macro.body = []

    ivyxml = ET.parse(file)
    for dependency in list(ivyxml.find('./dependencies')):
        if dependency.get('org') is None:
            continue
        call = ast.Expr()
        native_module = ast.Name('native', ast.Load())
        maven_jar = ast.Call(ast.Attribute(native_module, 'maven_jar', ast.Load()), [], [])
        maven_jar.keywords = []
        maven_jar.keywords.append(ast.keyword('name', ast.Constant(get_dependency_workspace_name(dependency))))
        maven_jar.keywords.append(ast.keyword('artifact', ast.Constant(get_dependency_artifact(dependency))))
        call.value = maven_jar
        jars_macro.body.append(call)
    
    dependencies.body.append(jars_macro)
    dependencies_code = astunparse.unparse(dependencies)
    return dependencies_code

if __name__ == '__main__':
    arguments = docopt(__doc__)
    print(convert_ivy_deps(arguments['<file>']))
