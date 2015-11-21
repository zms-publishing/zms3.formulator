# -*- coding: utf-8 -*-
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
    self.fromAddress  = this.attr('sendViaMailFrom').strip() == '' and self.this.getConfProperty('ZMSAdministrator.email', self.thisMaster.getConfProperty('ZMSAdministrator.email','')) or this.attr('sendViaMailFrom').strip()
    self.feedbackMsg  = this.attr('feedbackMsg').strip()
    self.replyAddress = None
    self.copyAddress  = None
    self.items        = []
    self._data        = {}
    
    # init _data
    if not self.getData():
      raise SystemError('Storage not available')
    
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
        if 'ZMS_FRM_USR' not in self.sqldb.columns:
          alt = 'ALTER TABLE %s ADD COLUMN `ZMS_FRM_USR` VARCHAR(128) NULL AFTER `ZMS_FRM_URL`;'%self.this.getId()
          con = self.engine.connect()
          res = con.execute(alt)
        if 'ZMS_FRM_UID' not in self.sqldb.columns:
          alt = 'ALTER TABLE %s ADD COLUMN `ZMS_FRM_UID` VARCHAR(128) NULL AFTER `ZMS_FRM_OID`;'%self.this.getId()
          con = self.engine.connect()
          res = con.execute(alt)
      except NoSuchTableError:
        self.sqldb = Table(self.this.getId(), metadata,
                           Column('ZMS_FRM_ITM', BigInteger(), primary_key=True),
                           Column('ZMS_FRM_OID', BigInteger()),
                           Column('ZMS_FRM_UID', String(128)),
                           Column('ZMS_FRM_EID', String(32)),
                           Column('ZMS_FRM_CID', String(32)),
                           Column('ZMS_FRM_FID', String(32)),
                           Column('ZMS_FRM_URL', String(512)),
                           Column('ZMS_FRM_USR', String(128)),
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
      except:
        return None
 
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
      lang = self.this.REQUEST.get('lang', self.this.getPrimaryLanguage())
      self.this.REQUEST.set('lang', self.this.getPrimaryLanguage())
      data = self.this.attr('_data')
      self._data.update(data)
      self.this.REQUEST.set('lang', lang)      
          
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
        lang = self.this.REQUEST.get('lang', self.this.getPrimaryLanguage())
        self.this.REQUEST.set('lang', self.this.getPrimaryLanguage())
        self.this.setObjStateModified(self.this.REQUEST)
        self.this.attr('_data', self._data)
        self.this.onChangeObj(self.this.REQUEST)
        self.this.commitObj(self.this.REQUEST,forced=True)
        self.this.REQUEST.set('lang', lang)
        return True
      else:
        _globals.writeBlock(self.thisMaster, "[ZMSFormulator.clearData] zodb.isReadOnly")
        return False
    
  def setData(self, receivedData):

    if type(receivedData) is dict:
      
      # save data as records to SQLDB
      if self.SQLStorage and not self.noStorage:
        modelledData = JSONEditor.JSONEditor(self)
        
        for timestamp in receivedData:
          for key, val in receivedData[timestamp]:
            
            # normalize received ZMSFormulatorItem-Key due to arrays/objects
            # fetch matching ZMSFormulatorItem-Obj to retrieve ids and values
            if '[' in key:
              itemkey = key.split('[')[0].upper()
            else:
              itemkey = key.upper() 
            if itemkey == 'RECAPTCHA':
              continue
            
            ZMS_FRM_RES = self.this.str_item(val)
            
            item = filter(lambda x: x.titlealt.upper() == itemkey, self.items)
            if len(item)>0:
              itemobj = item[0]
              if itemobj.type == 'email':
                self.replyAddress = itemobj.replyToField and ZMS_FRM_RES.strip() or None
                self.copyAddress = itemobj.copyToField and ZMS_FRM_RES.strip() or None
            else:
              raise ValueError("malformed content model")
            
            if itemobj.type in ['select', 'checkbox', 'multiselect']:
              ZMS_FRM_RES = ZMS_FRM_RES.replace('\n',', ')
              ZMS_FRM_RAW = ', '.join(itemobj.select.splitlines())
            else:
              ZMS_FRM_RAW = itemobj.rawJSON
            
            from datetime import datetime 
            ins = self.sqldb.insert().values(
              ZMS_FRM_TST = datetime.fromtimestamp(timestamp),
              ZMS_FRM_RES = ZMS_FRM_RES,
              ZMS_FRM_ORD = modelledData.JSONDict['properties'][itemkey].has_key('propertyOrder') and modelledData.JSONDict['properties'][itemkey]['propertyOrder'] or 0,
              ZMS_FRM_OID = int(itemobj.oid[4:]),              
              ZMS_FRM_UID = 'uid:' in itemobj.uid and itemobj.uid[4:] or None,
              ZMS_FRM_EID = itemobj.eid[:32],
              ZMS_FRM_CID = itemobj.cid[:32],                    
              ZMS_FRM_FID = itemobj.fid[:32],                       
              ZMS_FRM_URL = itemobj.url[:512],
              ZMS_FRM_USR = str(self.this.REQUEST.get('AUTHENTICATED_USER',''))[:128],
              ZMS_FRM_TYP = itemobj.type[:32],                   
              ZMS_FRM_KEY = key[:128], # put the received key including arrays/objects instead of plain itemobj.titlealt
              ZMS_FRM_ALT = itemobj.title[:64],
              ZMS_FRM_TXT = itemobj.description[:512],
              ZMS_FRM_MDT = itemobj.mandatory,
              ZMS_FRM_HID = itemobj.hidden,
              ZMS_FRM_MIN = itemobj.minimum,
              ZMS_FRM_MAX = itemobj.maximum, 
              ZMS_FRM_DFT = itemobj.default[:128],
              ZMS_FRM_RAW = ZMS_FRM_RAW,
              )
            con = self.engine.connect()
            res = con.execute(ins)

      # save data as dictionary to ZODB
      else: 
        self._data.update(receivedData)
        zodb = getConfiguration().dbtab.getDatabase('/', is_root=1)._storage
        if not zodb.isReadOnly() and not self.noStorage:
          lang = self.this.REQUEST.get('lang', self.this.getPrimaryLanguage())
          self.this.REQUEST.set('lang', self.this.getPrimaryLanguage())
          self.this.setObjStateModified(self.this.REQUEST)
          self.this.attr('_data', self._data)
          self.this.onChangeObj(self.this.REQUEST)
          self.this.commitObj(self.this.REQUEST,forced=True)
          self.this.REQUEST.set('lang', lang)
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
      pos = -1

      # Google.API.sitekey.password disabled
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
        if pos >= 0:
          data.pop(pos)
        # add current timestamp and store data
        self.setData({time.mktime(time.localtime()): data})
        # send data by mail if configured      
        if self.sendViaMail == True:
          self.sendData()
        return True 

      elif error:
        _globals.writeError(self.thisMaster, "[ZMSFormulator.receiveData] error occurred while using reCAPTCHA service by Google: %s"%error)        
        return False        

      else:
        _globals.writeError(self.thisMaster, "[ZMSFormulator.receiveData] input by robot detected")        
        return False
    
    else:
      _globals.writeError(self.thisMaster, "[ZMSFormulator.receiveData] unexpected data received")
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
      mhead = {'To':self.mailAddress,'From':self.fromAddress}
      
      if self.replyAddress is not None:
        mhead['Reply-To'] = self.replyAddress  
      
      rtn = self.thisMaster.sendMail(mhead, msubj, mbody, self.this.REQUEST)
      if rtn < 0:
        _globals.writeError(self.thisMaster, "[ZMSFormulator.sendData] failed to send mail")
      
      if self.copyAddress is not None:
        mhead2 = {'To':self.copyAddress,'From':self.fromAddress}
        rtn = self.thisMaster.sendMail(mhead2, msubj, mbody, self.this.REQUEST)
        if rtn < 0:
          _globals.writeError(self.thisMaster, "[ZMSFormulator.sendData] failed to send mail as copy")
    else:
      _globals.writeError(self.thisMaster, "[ZMSFormulator.sendData] no mail address specified")      

  def printDataRaw(self, frmt='txt'):
    
    data = self.getData()

    # Handle ZODB-Dictionary
    if isinstance(data, dict):
      if frmt=='txt':
        s = '%s entries:\n\n'%len(data)
      else:
        s = ''
      s1 = s2 = ''
      for t, v in sorted(data.iteritems()):
        header = ['TIMESTAMP']
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
    
    # Handle SQL-Storage
    else:
      sel = select([self.sqldb.c.ZMS_FRM_TST]).group_by(self.sqldb.c.ZMS_FRM_TST)
      con = self.engine.connect()
      res = con.execute(sel)
      if frmt=='txt':
        s = '%s entries:\n\n'%res.rowcount
      else:
        s = ''
      
      sel = select([self.sqldb.c.ZMS_FRM_KEY]).distinct().order_by(self.sqldb.c.ZMS_FRM_ORD, self.sqldb.c.ZMS_FRM_KEY)
      con = self.engine.connect()
      res1 = con.execute(sel)

      sel = select([self.sqldb.c.ZMS_FRM_KEY, self.sqldb.c.ZMS_FRM_ALT, self.sqldb.c.ZMS_FRM_RES, self.sqldb.c.ZMS_FRM_TST]).order_by(self.sqldb.c.ZMS_FRM_TST, self.sqldb.c.ZMS_FRM_KEY)
      con = self.engine.connect()
      res2 = con.execute(sel)

      header = ['TIMESTAMP']
      for head in res1:
        header.append(head[0])
      
      from collections import defaultdict
      records = defaultdict(dict)
      for rec in res2: 
        frm_key = rec[0]
        frm_res = rec[2]
        frm_tst = rec[3]
        records[frm_tst][frm_key] = frm_res
        
      output = []
      for tst, key in sorted(records.iteritems()):
        rec = []
        for h in header:
          if key.has_key(h):
            outstr = self.this.re_sub('[_\[\]]','',key[h]).replace('\n',', ')
            outstr = outstr.replace('`','').replace('´','').replace('\'','')
            outstr = outstr.replace('|','').replace('\\','').replace(';','')
            outstr = outstr.replace('<','').replace('>','').replace('"','')
            rec.append(outstr)
          elif (h!='TIMESTAMP'):
            rec.append('')
        output.append('\n'+str(tst))
        output.extend(rec)

      s1 = ';'.join(header)
      s2 = ';'.join(output)
      
      s += s1.upper() + s2.replace(';\n', '\n')

    # Render current transmitted item (last element in output-list)
    # line-by-line tab-separated to be used in sendData by mail
    if (frmt == 'tab'):
      s = ''
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
    self.uid          = this.get_uid()
    self.cid          = this.getHome().getId()
    self.fid          = this.getParentNode().getId()
    self.url          = this.getParentNode().getDeclUrl()

    # to keep headlines of DATA in sync for all language versions
    # use the value of titlealt in primary language always and ignore value of current language version
    lang = this.REQUEST.get('lang', this.getPrimaryLanguage())
    this.REQUEST.set('lang', this.getPrimaryLanguage())
    # remove square brackets from user inputs to be used as key which does not interfere with arrays/objects 
    self.titlealt     = this.attr('titlealt').replace('[','').replace(']','')
    this.REQUEST.set('lang', lang)
    
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
    self.replyToField = this.attr('replyToField')
    self.copyToField  = this.attr('copyToField')