"""zms3.formulator.ZMSFormulator
"""
from Zope2.App.startup import getConfiguration
from Products.zms import _globals
import zExceptions
import time

class ZMSFormulator:
  
  def __init__(self, this):
       
    self.this         = this
    self.thisURLPath  = this.absolute_url()
    self.baseURLPath  = this.getDocumentElement().absolute_url()
    self.thisMaster   = this.breadcrumbs_obj_path(True)[0]
    self.titlealt     = this.attr('titlealt')
    self.title        = this.attr('title')
    self.description  = this.attr('attr_dc_description')
    self.options      = this.attr('optionsJS')
    self.sendViaMail  = this.attr('sendViaMail')
    self.mailAddress  = this.attr('sendViaMailAddress').strip()
    self.items        = []
    self._data        = {}
    
    # init _data
    self.getData()
    
    # init items
    objs = filter(lambda ob: ob.isActive(self.this.REQUEST), self.this.getObjChildren('formulatorItems', self.this.REQUEST))
    for item in objs:
      self.items.append(ZMSFormulatorItem(item))    

  def getData(self):
    
    data = self.this.attr('_data')
    self._data.update(data)
    return self._data

  def clearData(self):
    
    self._data.clear()
    zodb = getConfiguration().dbtab.getDatabase('/', is_root=1)._storage
    if not zodb.isReadOnly():
      self.this.attr('_data', self._data)
      self.this.onChangeObj(self.this.REQUEST)
      return True
    else:
      _globals.writeBlock(self.thisMaster, "[ZMSFormulator.clearData] zodb.isReadOnly")
      return False
    
  def setData(self, data):

    if type(data) is dict:
      self._data.update(data)
      zodb = getConfiguration().dbtab.getDatabase('/', is_root=1)._storage
      if not zodb.isReadOnly():
        self.this.attr('_data', self._data)
        self.this.onChangeObj(self.this.REQUEST)
        return True
      else:
        _globals.writeBlock(self.thisMaster, "[ZMSFormulator.setData] zodb.isReadOnly")
        return False
    else:
      _globals.writeError(self.thisMaster, "[ZMSFormulator.setData] unexpected data (not dict)")
      return None

  def receiveData(self, data=None):
     
    if data is None:
      data = self.this.REQUEST.form.items()
    
    # TODO: parse input data
    _globals.writeBlock(self.thisMaster, "[ZMSFormulator.receiveData] %s"%data) 
        
    if type(data) is list and len(data)>0:
      # add current timestamp to data list and store as dictionary
      self.setData({time.time(): data})
      if self.sendViaMail == True:
        self.sendData()
    else:
      _globals.writeError(self.thisMaster, "[ZMSFormulator.setData] unexpected data (not list)")
      return False

  def sendData(self):      

    if self.mailAddress != '':
      msubj = '[%s] Data submitted: %s' % (self.this.getLangStr('TYPE_ZMSFORMULATOR'), self.titlealt)
      mbody = []
      mbody.append(self.title)
      mbody.append('\n')
      base = ''
      href = self.this.getHref2IndexHtml(self.this.REQUEST)
      if self.thisMaster.getConfProperty('ZMS.pathcropping',0)==1:
        base = self.this.REQUEST.get('BASE0','')
      mbody.append('%s entries at %s' % (len(self.getData()), base+href))      
      mbody.append('\n\n')
      mbody.append(self.printDataRaw())
      mbody = ''.join(mbody)
      if self.thisMaster.sendMail(self.mailAddress, msubj, mbody, self.this.REQUEST) < 0:
        _globals.writeError(self.thisMaster, "[ZMSFormulator.sendData] failed to send mail")
    else:
      _globals.writeError(self.thisMaster, "[ZMSFormulator.sendData] no mail address specified")      

  def printDataRaw(self):
    
    s = s1 = s2 = ''
    d = self.getData()
    for t, v in sorted(d.iteritems()):
      header = ['DATE']
      output = []
      output.append(time.strftime('%c', time.gmtime(t)))
      for i in sorted(v):
        i1, i2 = i
        header.append(i1.upper())
        outstr = self.this.str_item(i2)
        outstr = outstr.replace('`','').replace('\'','').replace('"','')
        outstr = outstr.replace('$','').replace('|','').replace(';','')
        outstr = outstr.replace('<','').replace('>','').replace('&','')
        output.append(outstr.replace('\n',', '))
      #output.append('\n')
      s1 = ';'.join(header)
      s2 += ';'.join(output) + '\n'
    
    s = s + self.this.re_sub('[_\[\]]','',s1) + '\n' + s2
    
    return s

class ZMSFormulatorItem:

  def __init__(self, this):
    
    self.titlealt     = this.attr('titlealt')
    self.title        = this.attr('title')
    self.description  = this.attr('attr_dc_description')
    self.type         = this.attr('type')
    self.default      = this.attr('valueDefault')
    self.minimum      = this.attr('valueMinimum')
    self.maximum      = this.attr('valueMaximum')
    self.select       = this.attr('valueSelect')
    self.rawJSON      = this.attr('rawJSON')
