"""zms3.formulator.ZMSFormulator
"""
from Zope2.App.startup import getConfiguration
import time

class ZMSFormulator:
  
  def __init__(self, this):
       
    self.this         = this
    self.thisURLPath  = this.absolute_url()
    self.baseURLPath  = this.getDocumentElement().absolute_url()
    self.titlealt     = this.attr('titlealt')
    self.title        = this.attr('title')
    self.description  = this.attr('attr_dc_description')
    self.options      = this.attr('optionsJS')
    self.sendViaMail  = this.attr('sendViaMail')
    self.mailAddress  = this.attr('sendViaMailAddress')
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
    
  def setData(self, data):

    zodb = getConfiguration().dbtab.getDatabase('/', is_root=1)._storage
    
    if type(data) is dict:
      self._data.update(data)
      if not zodb.isReadOnly():
        self.this.attr('_data', self._data)
        self.this.onChangeObj(self.this.REQUEST)
      else:
        print "[ZMSFormulator.setData] zodb.isReadOnly"
      return True
    else:
      print "[ZMSFormulator.setData] data is not a dict"
      return False

  def receiveData(self, data=None):
     
    if data is None:
      data = self.this.REQUEST.form.items()
    
    # TODO: parse input data
    print "[ZMSFormulator.receiveData]", data
    
    if type(data) is list and len(data)>0:
      self.setData({time.time(): data})
      
    # TODO: send data by mail

  def sendData(self):      
    """
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
    """

  def clearData(self):
    
    self._data.clear()
    self.this.attr('_data', self._data)
    self.this.onChangeObj(self.this.REQUEST)

  def printDataRaw(self):
    
    s = s1 = s2 = ''
    d = self.getData()
    for t, v in sorted(d.iteritems()):
      header = ['\nDATE']
      output = []
      output.append(time.strftime('%c', time.gmtime(t)))
      for i in sorted(v):
        i1, i2 = i
        header.append(i1.split('_', 1)[1].upper())
        outstr = self.this.str_item(i2)
        outstr = outstr.replace('`','').replace('\'','').replace('"','')
        outstr = outstr.replace('$','').replace('|','').replace(';','')
        outstr = outstr.replace('<','').replace('>','').replace('&','')
        output.append(outstr.replace('\n','; '))
      output.append('\n')
      s1 = ' | '.join(header)
      s2 += ' | '.join(output)      
    
    s = s + self.this.re_sub('[_\[\]]','',s1) + '\n' + s2
    
    return s

  def printDataPretty(self):
    
    # TODO: printDataPretty
    
    return

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
