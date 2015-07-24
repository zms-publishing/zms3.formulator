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

from Zope2.App.startup import getConfiguration
from Products.zms import _globals
import zExceptions
import time
import json
import urllib
import urllib2
from zms3.formulator import JSONEditor
from sqlalchemy import *
from sqlalchemy.exc import *

class ZMSFormulator:
  
  def __init__(self, this):
       
    self.this         = this
    self.thisURLPath  = this.absolute_url()
    self.baseURLPath  = this.getDocumentElement().absolute_url()
    self.thisMaster   = this.breadcrumbs_obj_path(True)[0]
    self.GoogleAPIKey = self.this.getConfProperty('Google.API.sitekey.password', self.thisMaster.getConfProperty('Google.API.sitekey.password','no_site_key'))
    self.GoogleAPISec = self.this.getConfProperty('Google.API.secretkey.password', self.thisMaster.getConfProperty('Google.API.secretkey.password','no_secret_key'))
    self.dbconnection = self.this.getConfProperty('ZMSFormulator.dbconnection.password', self.thisMaster.getConfProperty('ZMSFormulator.dbconnection.password','mysql://localhost/test'))
    self.titlealt     = this.attr('titlealt')
    self.title        = this.attr('title')
    self.description  = this.attr('attr_dc_description')
    self.options      = this.attr('optionsJS')
    self.onReady      = this.attr('onReadyJS')
    self.onChange     = this.attr('onChangeJS')
    self.noStorage    = this.attr('dataStorageDisabled')
    self.SQLStorage   = this.attr('dataStorageSQL')
    self.sendViaMail  = this.attr('sendViaMail')
    self.mailAddress  = this.attr('sendViaMailAddress').strip()
    self.feedbackMsg  = this.attr('feedbackMsg').strip()
    self.items        = []
    self._data        = {}
    
    # init _data
    self.getData()
    
    # init items
    objs = filter(lambda ob: ob.isActive(self.this.REQUEST), self.this.getObjChildren('formulatorItems', self.this.REQUEST, ['ZMSFormulatorItem']))
    for item in objs:
      self.items.append(ZMSFormulatorItem(item))    

  def getData(self):
    
    if self.SQLStorage and not self.noStorage:
      
      self.engine = create_engine(self.dbconnection)
      metadata = MetaData()
      try:
        self.sqldb = Table(self.this.getId(), metadata, autoload=True, autoload_with=self.engine)
      except NoSuchTableError:
        self.sqldb = Table(self.this.getId(), metadata,
                           Column('ZMS_FRM_ITM', BigInteger(), primary_key=True),
                           Column('ZMS_FRM_OID', BigInteger()),
                           Column('ZMS_FRM_EID', String(32)),
                           Column('ZMS_FRM_CID', String(32)),
                           Column('ZMS_FRM_FID', String(32)),
                           Column('ZMS_FRM_URL', String(512)),
                           Column('ZMS_FRM_MDT', Boolean()),                                              
                           Column('ZMS_FRM_HID', Boolean()),
                           Column('ZMS_FRM_MIN', Integer()),
                           Column('ZMS_FRM_MAX', Integer()),
                           Column('ZMS_FRM_DFT', String(128)),                        
                           Column('ZMS_FRM_KEY', String(128)),
                           Column('ZMS_FRM_ALT', String(64)),             
                           Column('ZMS_FRM_TXT', String(512)),
                           Column('ZMS_FRM_TYP', String(32)),
                           Column('ZMS_FRM_ORD', SmallInteger()),
                           Column('ZMS_FRM_RAW', Text()),
                           Column('ZMS_FRM_RES', Text()),
                           Column('ZMS_FRM_TST', DateTime()),
                           )
        metadata.create_all(self.engine)
 
      sel = select([
                    self.sqldb.c.ZMS_FRM_TST, 
                    self.sqldb.c.ZMS_FRM_KEY, 
                    self.sqldb.c.ZMS_FRM_ALT, 
                    self.sqldb.c.ZMS_FRM_RES]
                   ).order_by(self.sqldb.c.ZMS_FRM_KEY)
      con = self.engine.connect()
      res = con.execute(sel)
      
      self._data = res
      
    else:
      data = self.this.attr('_data')
      self._data.update(data)
    
    return self._data

  def clearData(self):
    
    if self.SQLStorage and not self.noStorage:      
      con = self.engine.connect()
      con.execute(self.sqldb.delete())
      return True
    else:
      self._data.clear()
      zodb = getConfiguration().dbtab.getDatabase('/', is_root=1)._storage
      if not zodb.isReadOnly() and not self.noStorage:
        self.this.REQUEST.set('lang', self.this.getPrimaryLanguage())
        self.this.setObjStateModified(self.this.REQUEST)
        self.this.attr('_data', self._data)
        self.this.onChangeObj(self.this.REQUEST)
        self.this.commitObj(self.this.REQUEST,forced=True)
        return True
      else:
        _globals.writeBlock(self.thisMaster, "[ZMSFormulator.clearData] zodb.isReadOnly")
        return False
    
  def setData(self, receivedData):

    if type(receivedData) is dict:
      
      # save data as record to SQLDB
      if self.SQLStorage and not self.noStorage:
        modelledData = JSONEditor.JSONEditor(self)
        
        for timestamp in receivedData:
          for key, val in receivedData[timestamp]:
            
            # normalize received ZMSFormulatorItem-Key due to arrays/objects
            # fetch matching ZMSFormulatorItem-Obj to retrieve ids and values
            if '[' in key:
              itemkey = key.split('[')[0].lower()
            else:
              itemkey = key.lower() 
            if itemkey == 'recaptcha':
              continue
            itemobj = filter(lambda x: x.titlealt.lower() == itemkey, self.items)[0]
            
            if itemobj.type in ['select', 'checkbox', 'multiselect']:
              ZMS_FRM_RAW = itemobj.select.strip()
            else:
              ZMS_FRM_RAW = itemobj.rawJSON
            
            from datetime import datetime 
            ins = self.sqldb.insert().values(
              ZMS_FRM_TST = datetime.fromtimestamp(timestamp),
              ZMS_FRM_RES = str(val),
              ZMS_FRM_ORD = modelledData.JSONDict['properties'][itemkey]['propertyOrder'],
              ZMS_FRM_OID = int(itemobj.oid[4:]),              
              ZMS_FRM_EID = itemobj.eid,
              ZMS_FRM_CID = itemobj.cid,                    
              ZMS_FRM_FID = itemobj.fid,                       
              ZMS_FRM_URL = itemobj.url,
              ZMS_FRM_TYP = itemobj.type,                   
              ZMS_FRM_KEY = key, # put the received key including arrays/objects instead of plain itemobj.titlealt
              ZMS_FRM_ALT = itemobj.title,
              ZMS_FRM_TXT = itemobj.description,
              ZMS_FRM_MDT = itemobj.mandatory,
              ZMS_FRM_HID = itemobj.hidden,
              ZMS_FRM_MIN = itemobj.minimum,
              ZMS_FRM_MAX = itemobj.maximum, 
              ZMS_FRM_DFT = itemobj.default,
              ZMS_FRM_RAW = ZMS_FRM_RAW,
              )
            con = self.engine.connect()
            res = con.execute(ins)

      # save data as dictionary to ZODB
      else: 
        self._data.update(receivedData)
        zodb = getConfiguration().dbtab.getDatabase('/', is_root=1)._storage
        if not zodb.isReadOnly() and not self.noStorage:
          self.this.REQUEST.set('lang', self.this.getPrimaryLanguage())
          self.this.setObjStateModified(self.this.REQUEST)
          self.this.attr('_data', self._data)
          self.this.onChangeObj(self.this.REQUEST)
          self.this.commitObj(self.this.REQUEST,forced=True)
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
      
      isOK = False
      error = None
      pos = 0

      # Google.API.sitekey.password not configured
      if self.GoogleAPIKey == 'no_site_key':
        isOK = True

      # check if input was sent by a robot
      # hand over response value to reCAPTCHA service by Google
      else:
        
        for i, item in enumerate(data):
          key, val = item
          if key == 'reCAPTCHA':
            reCAPTCHA = val
            pos = i

        url = 'https://www.google.com/recaptcha/api/siteverify'
        val = {'secret' : self.GoogleAPISec,
               'response' : reCAPTCHA}
        dat = urllib.urlencode(val)
        req = urllib2.Request(url, dat)
        res = urllib2.urlopen(req)
        ret = res.read()
        
        verification = json.loads(ret)
      
        if 'success' in verification:
          isOK = verification['success']
          if not isOK:
            if 'error-codes' in verification:
              error = verification['error-codes']
      
      if isOK:
        # remove reCAPTCHA response value from data to be stored
        if pos > 0:
          data.pop(pos)
        # add current timestamp and store data
        self.setData({time.mktime(time.localtime()): data})
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
      mbody.append(self.printDataRaw(frmt='tab'))
      mbody = ''.join(mbody)
      if self.thisMaster.sendMail(self.mailAddress, msubj, mbody, self.this.REQUEST) < 0:
        _globals.writeError(self.thisMaster, "[ZMSFormulator.sendData] failed to send mail")
    else:
      _globals.writeError(self.thisMaster, "[ZMSFormulator.sendData] no mail address specified")      

  def printDataRaw(self, frmt='csv'):
    
    data = self.getData()
    
    if isinstance(data, dict):
      s = '%s entries:\n\n'%len(data)
      s1 = s2 = ''
      for t, v in sorted(data.iteritems()):
        header = ['timestamp']
        output = []
        output.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t)))
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
        
      s += s1.upper() + '\n' + s2
    
    else:
      sel = select([self.sqldb.c.ZMS_FRM_TST]).group_by(self.sqldb.c.ZMS_FRM_TST)
      con = self.engine.connect()
      res = con.execute(sel)
      s = '%s entries:\n\n'%res.rowcount
      
      sel = select([self.sqldb.c.ZMS_FRM_KEY]).distinct().order_by(self.sqldb.c.ZMS_FRM_ORD, self.sqldb.c.ZMS_FRM_KEY)
      con = self.engine.connect()
      res1 = con.execute(sel)

      sel = select([self.sqldb.c.ZMS_FRM_KEY, self.sqldb.c.ZMS_FRM_ALT, self.sqldb.c.ZMS_FRM_RES, self.sqldb.c.ZMS_FRM_TST]).order_by(self.sqldb.c.ZMS_FRM_TST, self.sqldb.c.ZMS_FRM_ORD, self.sqldb.c.ZMS_FRM_KEY)
      con = self.engine.connect()
      res2 = con.execute(sel)

      header = ['timestamp']
      for head in res1:
        header.append(head[0])
        
      record = []
      for recd in res2:
        record.append((recd[0], recd[2], recd[3]))

      output = []
      for r in record:
        for h in header:
          if r[0] == h:
            outstr = self.this.re_sub('[_\[\]]','',r[1]).replace('\n',', ')
            if r[0] == header[1]:
              output.append('\n' + str(r[2]))
            outstr = outstr.replace('`','').replace('´','').replace('\'','')
            outstr = outstr.replace('|','').replace('\\','').replace(';','')
            outstr = outstr.replace('<','').replace('>','').replace('"','')
            output.append(outstr)
            
      s1 = ';'.join(header)
      s2 = ';'.join(output)
      
      s += s1.upper() + s2.replace(';\n', '\n')
    
    if (frmt == 'tab'):
      s = ''
      # render current transmitted item (last element in output-list)
      # line-by-line tab-separated to be used in sendData by mail
      # TODO: recognize different length and order of output-lists due to special array-fields
      if len(output)>=len(header):
        for item in zip(header, output[-len(header):]):
          desc = item[0].strip()
          cont = item[1].strip()
          if len(desc)<8:
            tab = '\t\t\t'
          elif len(desc)<16:
            tab = '\t\t'
          else:
            tab = '\t'
            
          s += desc.upper() + tab + cont + '\n'
        
    return s

class ZMSFormulatorItem:

  def __init__(self, this):
    
    self.eid          = this.getId()
    self.oid          = this.get_oid()
    self.cid          = this.getHome().getId()
    self.fid          = this.getParentNode().getId()
    self.url          = this.getParentNode().getDeclUrl()     
    self.titlealt     = this.attr('titlealt')
    self.title        = this.attr('title')
    self.description  = this.attr('attr_dc_description')
    self.type         = this.attr('type')
    self.default      = this.attr('valueDefault')
    self.minimum      = this.attr('valueMinimum')
    self.maximum      = this.attr('valueMaximum')
    self.select       = this.attr('valueSelect')
    self.rawJSON      = this.attr('rawJSON')
    self.mandatory    = this.attr('mandatoryField')
    self.hidden       = this.attr('hiddenField')
