################################################################################
#
#  Copyright (c) HOFFMANN+LIEBENBERG in association with SNTL Publishing, Berlin
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

from Zope2.App.startup import getConfiguration
from Products.zms import _globals
import zExceptions
import time
import json
import urllib
import urllib2

class ZMSFormulator:
  
  def __init__(self, this):
       
    self.this         = this
    self.thisURLPath  = this.absolute_url()
    self.baseURLPath  = this.getDocumentElement().absolute_url()
    self.thisMaster   = this.breadcrumbs_obj_path(True)[0]
    self.GoogleAPIKey = self.thisMaster.getConfProperty('Google.API.sitekey.password','your_site_key')
    self.GoogleAPISec = self.thisMaster.getConfProperty('Google.API.secretkey.password','your_secret_key')
    self.titlealt     = this.attr('titlealt')
    self.title        = this.attr('title')
    self.description  = this.attr('attr_dc_description')
    self.options      = this.attr('optionsJS')
    self.onReady      = this.attr('onReadyJS')
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
      return False

  def receiveData(self, data=None):
    
    if data is None:
      data = self.this.REQUEST.form.items()

    _globals.writeBlock(self.thisMaster, "[ZMSFormulator.receiveData] %s"%data)
    
    if type(data) is list and len(data)>0:
      
      for i, item in enumerate(data):
        key, val = item
        if key == 'reCAPTCHA':
          reCAPTCHA = val
          pos = i
      
      # check if input was sent by a robot
      # hand over response value to reCAPTCHA service by Google
      url = 'https://www.google.com/recaptcha/api/siteverify'
      val = {'secret' : self.GoogleAPISec,
             'response' : reCAPTCHA}
      dat = urllib.urlencode(val)
      req = urllib2.Request(url, dat)
      res = urllib2.urlopen(req)
      ret = res.read()
      
      verification = json.loads(ret)
      
      isOK = False
      error = None
      if 'success' in verification:
        isOK = verification['success']
        if not isOK:
          if 'error-codes' in verification:
            error = verification['error-codes']
      
      if isOK:
        # remove reCAPTCHA response value from data to be stored
        data.pop(pos)
        # add current timestamp to data list and store as dictionary
        self.setData({time.time(): data})
        # send data by mail if configured      
        if self.sendViaMail == True:
          self.sendData()
        return True 

      elif error:
        _globals.writeError(self.thisMaster, "[ZMSFormulator.setData] error occurred while using reCAPTCHA service by Google: %s"%error)        
        return False        

      else:
        _globals.writeError(self.thisMaster, "[ZMSFormulator.setData] input by robot detected")        
        return False
    
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
      mbody.append(base+href)      
      mbody.append('\n\n')
      mbody.append(self.printDataRaw())
      mbody = ''.join(mbody)
      if self.thisMaster.sendMail(self.mailAddress, msubj, mbody, self.this.REQUEST) < 0:
        _globals.writeError(self.thisMaster, "[ZMSFormulator.sendData] failed to send mail")
    else:
      _globals.writeError(self.thisMaster, "[ZMSFormulator.sendData] no mail address specified")      

  def printDataRaw(self):
    
    d = self.getData()
    s = '%s entries:\n\n'%len(d)
    s1 = s2 = ''
    for t, v in sorted(d.iteritems()):
      header = ['DATE']
      output = []
      output.append(time.strftime('%c', time.gmtime(t)))
      for i in sorted(v):
        i1, i2 = i
        header.append(i1.upper())
        outstr = self.this.str_item(i2)
        outstr = outstr.replace('`','').replace('´','').replace('\'','')
        outstr = outstr.replace('|','').replace('\\','').replace(';','')
        outstr = outstr.replace('<','').replace('>','').replace('"','')
        output.append(outstr.replace('\n',', '))
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
