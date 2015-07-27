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

class JSONEditor:
  
  def __init__(self, obj):
    
    self.JSONDict                = {}
    self.JSONDict['id']          = obj.titlealt.upper()
    self.JSONDict['title']       = obj.title
    self.JSONDict['type']        = 'object'
    self.JSONDict['properties']  = {}
  
    for i, item in enumerate(obj.items, start=1):
  
      var = '%s'%(item.titlealt.upper())
      values = item.select.strip().splitlines()
      
      self.JSONDict['properties'][var]                     = {}
      self.JSONDict['properties'][var]['type']             = item.type == 'float' and 'number' or item.type
      self.JSONDict['properties'][var]['title']            = item.title + (item.mandatory and ' *' or '')
      self.JSONDict['properties'][var]['description']      = item.description + (item.type == 'multiselect' and obj.this.getLangStr('ZMSFORMULATOR_HINT_MULTISELECT',obj.this.REQUEST.get('lang')) or '')
      self.JSONDict['properties'][var]['propertyOrder']    = i
      self.JSONDict['properties'][var]['options']          = {}
  
      if item.default.strip() != '':
        self.JSONDict['properties'][var]['default']        = item.default 
  
      if item.minimum>0 or item.mandatory:
        if item.type in ['string', 'textarea']:
          self.JSONDict['properties'][var]['minLength']    = item.minimum > 0 and item.minimum or 1
        else:
          self.JSONDict['properties'][var]['minimum']      = item.minimum > 0 and item.minimum or 1
  
      if item.maximum>0:
        if item.type in ['string', 'textarea']:
          self.JSONDict['properties'][var]['maxLength']    = item.maximum
        else:
          self.JSONDict['properties'][var]['maximum']      = item.maximum
      
      if item.type == 'select':
        self.JSONDict['properties'][var]['type']           = 'string'
        self.JSONDict['properties'][var]['enum']           = []
        if len(values)>0:
          for val in values:
            self.JSONDict['properties'][var]['enum'].append(val)
      
      if item.type == 'textarea':
        self.JSONDict['properties'][var]['type']           = 'string'
        self.JSONDict['properties'][var]['format']         = 'textarea'
        self.JSONDict['properties'][var]['options']['input_height']  = '150px'
      
      if item.type == 'color':
        self.JSONDict['properties'][var]['type']           = 'string'
        self.JSONDict['properties'][var]['format']         = 'color'
  
      if item.type == 'date':
        self.JSONDict['properties'][var]['type']           = 'string'
        self.JSONDict['properties'][var]['format']         = 'date'
        
      if item.type in ['checkbox', 'multiselect']:
        self.JSONDict['properties'][var]['type']           = 'array'
        self.JSONDict['properties'][var]['uniqueItems']    = 'true'
        if item.type == 'multiselect':
          self.JSONDict['properties'][var]['format']       = 'select'
        self.JSONDict['properties'][var]['items']          = {}
        self.JSONDict['properties'][var]['items']['type']  = 'string'
        self.JSONDict['properties'][var]['items']['enum']  = []
        if len(values)>0:
          for val in values:
            self.JSONDict['properties'][var]['items']['enum'].append(val)
  
      if item.hidden:
        self.JSONDict['properties'][var]['options']['hidden']  = 'true'
  
      if item.type in ['custom'] and item.rawJSON != '':
        self.JSONDict['properties'][var]                   = json.loads(item.rawJSON)

  def render(self, obj):
    
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    f = open(os.path.join(__location__, 'JSONEditor.js'));
    editor = f.read()
    f.close()
    
    script = '<script src="%s/metaobj_manager/zms3.formulator.lib.jsoneditor.min.js"></script>\n<script>%s</script>'  
    editor = editor % (obj.thisURLPath, obj.GoogleAPIKey, obj.options, obj.onReady, obj.thisURLPath, obj.onChange)
    output = script % (obj.baseURLPath, editor)
    
    return output
  
  def getSchema(self):
  
    JSONSchema = json.dumps(self.JSONDict, sort_keys=True, indent=4, separators=(',', ': '))
    return JSONSchema
