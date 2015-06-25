################################################################################
#
#  Copyright (c) 2015 HOFFMANN+LIEBENBERG in association with SNTL Publishing
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

import json
import os

def render(obj):
  
  __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
  f = open(os.path.join(__location__, 'JSONEditor.js'));
  editor = f.read()
  f.close()
  
  script = '<script src="%s/metaobj_manager/zms3.formulator.lib.jsoneditor.min.js"></script>\n<script>%s</script>'  
  editor = editor % (obj.thisURLPath, obj.GoogleAPIKey, obj.options, obj.onReady, obj.thisURLPath, obj.onChange)
  output = script % (obj.baseURLPath, editor)
  
  return output

def getSchema(obj):

  JSONDict                = {}
  JSONDict['id']          = obj.titlealt.lower()
  JSONDict['title']       = obj.title
  JSONDict['type']        = 'object'
  JSONDict['properties']  = {}

  for i, item in enumerate(obj.items, start=1):

    var = '%s'%(item.titlealt.lower())
    values = item.select.strip().splitlines()
    
    JSONDict['properties'][var]                     = {}
    JSONDict['properties'][var]['type']             = item.type == 'float' and 'number' or item.type
    JSONDict['properties'][var]['title']            = item.title + (item.mandatory and ' *' or '')
    JSONDict['properties'][var]['description']      = item.description + (item.type == 'multiselect' and obj.this.getLangStr('ZMSFORMULATOR_HINT_MULTISELECT',obj.this.REQUEST.get('lang')) or '')
    JSONDict['properties'][var]['propertyOrder']    = i
    JSONDict['properties'][var]['options']          = {}

    if item.default.strip() != '':
      JSONDict['properties'][var]['default']        = item.default 

    if item.minimum>0 or item.mandatory:
      if item.type in ['string', 'textarea']:
        JSONDict['properties'][var]['minLength']    = item.minimum > 0 and item.minimum or 1
      else:
        JSONDict['properties'][var]['minimum']      = item.minimum > 0 and item.minimum or 1

    if item.maximum>0:
      if item.type in ['string', 'textarea']:
        JSONDict['properties'][var]['maxLength']    = item.maximum
      else:
        JSONDict['properties'][var]['maximum']      = item.maximum
    
    if item.type == 'select':
      JSONDict['properties'][var]['type']           = 'string'
      JSONDict['properties'][var]['enum']           = []
      if len(values)>0:
        for val in values:
          JSONDict['properties'][var]['enum'].append(val)
    
    if item.type == 'textarea':
      JSONDict['properties'][var]['type']           = 'string'
      JSONDict['properties'][var]['format']         = 'textarea'
      JSONDict['properties'][var]['options']['input_height']  = '150px'
    
    if item.type == 'color':
      JSONDict['properties'][var]['type']           = 'string'
      JSONDict['properties'][var]['format']         = 'color'

    if item.type == 'date':
      JSONDict['properties'][var]['type']           = 'string'
      JSONDict['properties'][var]['format']         = 'date'
      
    if item.type in ['checkbox', 'multiselect']:
      JSONDict['properties'][var]['type']           = 'array'
      JSONDict['properties'][var]['uniqueItems']    = 'true'
      if item.type == 'multiselect':
        JSONDict['properties'][var]['format']       = 'select'
      JSONDict['properties'][var]['items']          = {}
      JSONDict['properties'][var]['items']['type']  = 'string'
      JSONDict['properties'][var]['items']['enum']  = []
      if len(values)>0:
        for val in values:
          JSONDict['properties'][var]['items']['enum'].append(val)

    if item.hidden:
      JSONDict['properties'][var]['options']['hidden']  = 'true'

    if item.type in ['custom'] and item.rawJSON != '':
      JSONDict['properties'][var]                   = json.loads(item.rawJSON)

  JSONSchema = json.dumps(JSONDict, sort_keys=True, indent=4, separators=(',', ': '))
  return JSONSchema
