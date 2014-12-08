import json
import time
from Zope2.App.startup import getConfiguration

def getJSONEditor(self):

  f = open(self.getPRODUCT_HOME()+'/Extensions/formulator.js')
  formulatorjs = f.read()%(self.absolute_url(), self.attr('optionsJS'), self.absolute_url())
  jsoneditorjs = '%s/metaobj_manager/zms3.formulator.jsoneditor.min.js'%self.getDocumentElement().absolute_url()
  f.close()  

  JSONEditor = '''
    <button id='submit'>Submit</button>
    <button id='restore'>Restore</button>

    <span id='valid_indicator'></span>
    
    <div id='editor_holder'></div>
  
    <script src="%s"></script>     
    <script>%s</script>
  '''%(jsoneditorjs, formulatorjs)
  
  return JSONEditor

def getJSONSchema(self):

  JSONDict                = {}
  JSONDict['id']          = self.attr('titlealt').lower()
  JSONDict['title']       = self.attr('title')
  #self.attr('attr_dc_description')
  JSONDict['type']        = 'object'
  JSONDict['properties']  = {}

  for i, formulatorItem in enumerate(filter(lambda ob: ob.isActive(self.REQUEST), self.getObjChildren('formulatorItems', self.REQUEST)), start=1):

    #formulatorItem.attr('identifier')
    varname       = '%i_%s'%(i, formulatorItem.attr('titlealt').lower())
    title         = formulatorItem.attr('title')
    datatype      = formulatorItem.attr('type')
    description   = formulatorItem.attr('attr_dc_description')
    valueDefault  = formulatorItem.attr('valueDefault')
    valueMinimum  = formulatorItem.attr('valueMinimum')
    valueMaximum  = formulatorItem.attr('valueMaximum')
    valueSelect   = formulatorItem.attr('valueSelect').strip().splitlines()
    rawJSON       = formulatorItem.attr('rawJSON').strip()
    
    JSONDict['properties'][varname]                    = {}
    JSONDict['properties'][varname]['type']            = datatype == 'float' and 'number' or datatype
    JSONDict['properties'][varname]['title']           = title
    JSONDict['properties'][varname]['description']     = description

    if valueDefault.strip() != '':
      JSONDict['properties'][varname]['default']       = valueDefault 

    if valueMinimum>0:
      if datatype == 'string':
        JSONDict['properties'][varname]['minLength']   = valueMinimum
      else:
        JSONDict['properties'][varname]['minimum']     = valueMinimum

    if valueMaximum>0:
      if datatype == 'string':
        JSONDict['properties'][varname]['maxLength']   = valueMaximum
      else:
        JSONDict['properties'][varname]['maximum']     = valueMaximum

    if datatype == 'select' and len(valueSelect)>0:
      JSONDict['properties'][varname]['type']          = 'string'
      JSONDict['properties'][varname]['enum'] = []
      for selectItem in valueSelect:
        JSONDict['properties'][varname]['enum'].append(selectItem)      
      
    if datatype in ['checkbox', 'multiselect'] and len(valueSelect)>0:
      JSONDict['properties'][varname]['type']          = 'array'
      JSONDict['properties'][varname]['uniqueItems']   = 'true'
      if datatype == 'multiselect':
        JSONDict['properties'][varname]['format']      = 'select'
      JSONDict['properties'][varname]['items']         = {}
      JSONDict['properties'][varname]['items']['type'] = 'string'
      JSONDict['properties'][varname]['items']['enum'] = []
      for selectItem in valueSelect:
        JSONDict['properties'][varname]['items']['enum'].append(selectItem)

    if datatype in ['custom'] and rawJSON != '':
      JSONDict['properties'][varname]                  = json.loads(rawJSON)
      
  JSONSchema = json.dumps(JSONDict, sort_keys=True, indent=4, separators=(',', ': '))  
  
  return JSONSchema

def putJSONData(self):
  
  dataINP = self.REQUEST.form.items()

  dbtab   = getConfiguration().dbtab
  zodb    = dbtab.getDatabase('/', is_root=1)._storage
  
  if not zodb.isReadOnly():
    dataRAW = self.attr('_data')
    dataRAW.update({self.getTime(): dataINP})
    self.attr('_data',dataRAW)
    self.onChangeObj(self.REQUEST)
  else:
    print "\n[zodb] READONLY:", getJSONData(self, dataINP)
  
  if (self.attr('sendViaMail')==True and self.attr('sendViaMailAddress').strip()!=''):
    mto = self.attr('sendViaMailAddress').strip()
    msubject = '%s: %s'%(self.getLangStr('TYPE_ZMSFORMULATOR'), self.getTitlealt(self.REQUEST))
    mbody = []
    mbody.append(self.getTitle(self.REQUEST))
    mbody.append('\n')
    mbody.append(self.getHref2IndexHtml(self.REQUEST))
    mbody.append('\n')
    mbody.append(getJSONData(self, dataINP))
    mbody = ''.join(mbody)
    if self.sendMail(mto, msubject, mbody, self.REQUEST)<0:
      print "\n[sendMail] FAILED:", mto, msubject, mbody
  
def getJSONData(self, data=None):

  dataRAW = {}
  if data==None:
    dataRAW = self.attr('_data')
  else:
    dataRAW.update({self.getTime(): data})
  
  s = ''
  if type(dataRAW) is dict:
    for key, val in sorted(dataRAW.iteritems()):
      header = ['\nDATE']
      output = []
      output.append(time.strftime("\n%a, %d %b %Y %H:%M:%S %Z", time.gmtime(key)))
      for v in sorted(val):
        v0, v1 = v
        header.append(v0.split('_', 1)[1].upper())
        outstr = self.str_item(v1)
        outstr = outstr.replace('`','').replace('\'','').replace('"','')
        outstr = outstr.replace('$','').replace('|','').replace(';','')
        outstr = outstr.replace('<','').replace('>','').replace('&','')
        output.append(outstr.replace('\n','; '))
      s1 = ' | '.join(header)
      s2 = ' | '.join(output)
      s = s + self.re_sub('[_\[\]]','',s1)+' | '+s2+' | '
    
  return s




