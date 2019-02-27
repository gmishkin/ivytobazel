#!/usr/bin/env python3

"""
ivysettings_to_workspace.py

Usage:
    ivysettings_to_workspace.py <file>
"""

import sys
import ast
import xml.etree.ElementTree as ET

from docopt import docopt
import astunparse

MAVEN_CENTRAL_URL = 'http://repo.maven.apache.org/maven2'

def convert_m2_resolver(file):
    resolvers = ast.Module()
    resolvers.body = []

    macro = ast.FunctionDef(args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), decorator_list=[])
    macro.name = 'ivy_resolvers'
    macro.body = []
    
    settings = ET.parse(file)
    default_resolver = settings.find('./settings').get('defaultResolver')
    chain = settings.find('./resolvers/chain[@name=\'' + default_resolver + '\']')
    for resolver in list(chain):
        if resolver.tag != 'ibiblio' or resolver.get('m2compatible') != 'true':
            print(resolver.get('name') + ' resolver is not Maven compatible', file=sys.stderr)
            continue
        
        call = ast.Expr()
        native_module = ast.Name('native', ast.Load())
        maven_server = ast.Call(ast.Attribute(native_module, 'maven_server', ast.Load()), [], [])
        maven_server.keywords = []
        name = resolver.get('name')
        if name == 'private':
            name = 'default'
        maven_server.keywords.append(ast.keyword('name', ast.Constant(name)))
        url = resolver.get('root')
        if url is None:
            url = MAVEN_CENTRAL_URL
        maven_server.keywords.append(ast.keyword('url', ast.Constant(url)))
        call.value = maven_server
        macro.body.append(call)

    resolvers.body.append(macro)
    resolvers_code = astunparse.unparse(resolvers)
    return resolvers_code

if __name__ == '__main__':
    arguments = docopt(__doc__)
    print(convert_m2_resolver(arguments['<file>']))
