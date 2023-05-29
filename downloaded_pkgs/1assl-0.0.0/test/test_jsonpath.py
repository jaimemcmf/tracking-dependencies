#!/usr/bin/env python

import json
import jsonpath
import ruamel.yaml as yaml

with open('blueprint.json') as blueprint_file:
    content = yaml.load(blueprint_file, Loader=yaml.Loader)

# print(json.dumps(content, indent=4))


node_selector_jsonpath = "?($.spec.template.spec.nodeSelector=={})"
# (@.type=='compute')
# "{'type': 'compute'}"

jsonpath_value = """$.spec.template.spec.volumes[?(@.name=='gmcdata')]'"""
# print(jsonpath.jsonpath(content, jsonpath_value))
# print()
print(jsonpath.jsonpath(content, node_selector_jsonpath))