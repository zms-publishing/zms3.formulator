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

import os
import sys
from setuptools import setup

for path in sys.path:
  if path.startswith(sys.prefix) and path.endswith('site-packages'):
    site_packages = path

VERSION = '3.4.0dev'

zmspkg_name = 'formulator'
branch_name = 'master'
downld_file = 'https://bitbucket.org/zms3/%s/get/%s.zip'%(zmspkg_name, branch_name)

if 'dev' in VERSION:
  import subprocess
  # retrieve commit hash from local Git repository if available
  rtn = subprocess.Popen("git -C %s describe"%(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         shell=True, universal_newlines=True)
  rtn = rtn.communicate()[0].strip()
  rtn = rtn.split('-g')
  rtn.reverse()
  
  # otherwise retrieve commit hash from remote Git repository at Bitbucket
  if rtn[0].strip() == '':
    rtn = subprocess.Popen("curl --head " + downld_file,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           shell=True, universal_newlines=True)
    rtn = rtn.communicate()[0].strip()
    rtn = rtn.split('.zip')[0].split('filename=zms3-%s-'%zmspkg_name)
    rtn.reverse()
  
  commit_hash = rtn[0].strip()[:7]
  
  VERSION = '%s-%s%s'%(VERSION, branch_name, len(commit_hash)==7 and '-'+commit_hash or '')

INSTALL_REQUIRES = [
# Upstream requirement - install explicitly!
# 'ZMS3>=3.1.0',
  'sqlalchemy',
]

DATA_FILES = [
  (os.path.join(site_packages, 'zms3/formulator'), ['zms3/formulator/JSONEditor.js']),
  (os.path.join(site_packages, 'zms3/formulator/conf'), ['conf/zms3.formulator.example.xml']),
  (os.path.join(site_packages, 'zms3/formulator/conf'), ['conf/zms3.formulator.langdict.xml']),
  (os.path.join(site_packages, 'zms3/formulator/conf'), ['conf/zms3.formulator.metaobj.xml']),
]

PACKAGE_DATA = []
# Exclude special folders and files
for dirpath, dirnames, filenames in os.walk('.'):
  if (
    '.'                           != dirpath and
    '.settings'                   not in dirpath and
    '.git'                        not in dirpath and
    'dist'                        not in dirpath and
    'json-editor'                 not in dirpath and
    'select2'                     not in dirpath
    ): 
    if filenames: 
      for filename in filenames:
        if filename != '.DS_Store' and filename != '.gitignore':
          PACKAGE_DATA.append(dirpath[2:]+'/%s' % filename)
# Include files from root path (because '.' is exclude above)
PACKAGE_DATA.append('*.txt')

CLASSIFIERS = [
  'Development Status :: 4 - Beta',
  'Framework :: Zope2',
  'Programming Language :: Python :: 2.7',
  'Operating System :: OS Independent',
  'Environment :: Web Environment',
  'Topic :: Internet :: WWW/HTTP :: Site Management',
  'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
  'Intended Audience :: Education',
  'Intended Audience :: Science/Research',
  'Intended Audience :: Customer Service',
  'Intended Audience :: End Users/Desktop',
  'Intended Audience :: Healthcare Industry',
  'Intended Audience :: Information Technology',
  'Intended Audience :: Telecommunications Industry',
  'Intended Audience :: Financial and Insurance Industry',
  'License :: OSI Approved :: GNU Affero General Public License v3',
]

setup(
  name                  = 'zms3.formulator',
  description           = 'Submit JSON-based HTML-Forms into a SQL-Storage with protection by reCAPTCHA',
# long_description      = README,
  version               = VERSION,
  author                = 'HOFFMANN+LIEBENBERG in association with SNTL Publishing, Berlin',
  author_email          = 'zms@sntl-publishing.com',
  url                   = 'https://bitbucket.org/zms3/formulator',
  download_url          = 'https://bitbucket.org/zms3/formulator/downloads',
  namespace_packages    = ['zms3'],
  packages              = ['zms3.formulator'],
  package_dir           = {'zms3.formulator': 'zms3/formulator'},
  package_data          = {'zms3.formulator': PACKAGE_DATA},
  install_requires      = INSTALL_REQUIRES,
  data_files            = DATA_FILES,
  classifiers           = CLASSIFIERS,
  include_package_data  = True,
  zip_safe              = False,
)
