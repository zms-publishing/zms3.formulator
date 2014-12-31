"""zms3.formulator.JSONEditor
"""
import json
import os


def render(obj):
  
  __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
  f = open(os.path.join(__location__, 'JSONEditor.js'));
  editor = f.read()
  f.close()
  
  script = '<script src="%s/metaobj_manager/zms3.formulator.lib.jsoneditor.min.js"></script>\n<script>%s</script>'  
  editor = editor % (obj.thisURLPath, obj.options, obj.thisURLPath)
  output = script % (obj.baseURLPath, editor)
  
  return output

def getSchema(obj):

  JSONDict                = {}
  JSONDict['id']          = obj.titlealt.lower()
  JSONDict['title']       = obj.title
  JSONDict['type']        = 'object'
  JSONDict['properties']  = {}

  for i, item in enumerate(obj.items, start=1):

    var = '%i_%s'%(i, item.titlealt.lower())
    values = item.select.strip().splitlines()
    
    JSONDict['properties'][var]                     = {}
    JSONDict['properties'][var]['type']             = item.type == 'float' and 'number' or item.type
    JSONDict['properties'][var]['title']            = item.title
    JSONDict['properties'][var]['description']      = item.description

    if item.default.strip() != '':
      JSONDict['properties'][var]['default']        = item.default 

    if item.minimum>0:
      if item.type == 'string':
        JSONDict['properties'][var]['minLength']    = item.minimum
      else:
        JSONDict['properties'][var]['minimum']      = item.minimum

    if item.maximum>0:
      if item.type == 'string':
        JSONDict['properties'][var]['maxLength']    = item.maximum
      else:
        JSONDict['properties'][var]['maximum']      = item.maximum
    
    if item.type == 'select' and len(values)>0:
      JSONDict['properties'][var]['type']           = 'string'
      JSONDict['properties'][var]['enum']           = []
      for val in values:
        JSONDict['properties'][var]['enum'].append(val)      
      
    if item.type in ['checkbox', 'multiselect'] and len(values)>0:
      JSONDict['properties'][var]['type']           = 'array'
      JSONDict['properties'][var]['uniqueItems']    = 'true'
      if item.type == 'multiselect':
        JSONDict['properties'][var]['format']       = 'select'
      JSONDict['properties'][var]['items']          = {}
      JSONDict['properties'][var]['items']['type']  = 'string'
      JSONDict['properties'][var]['items']['enum']  = []
      for val in values:
        JSONDict['properties'][var]['items']['enum'].append(val)

    if item.type in ['custom'] and item.rawJSON != '':
      JSONDict['properties'][var]                   = json.loads(item.rawJSON)
        
  JSONSchema = json.dumps(JSONDict, sort_keys=True, indent=4, separators=(',', ': '))
  return JSONSchema
