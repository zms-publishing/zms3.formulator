import os
import sys
from setuptools import setup

# @see https://docs.python.org/2/library/site.html
# says site.getusersitepackages() "New in version 2.7" but it is still missing at
# 2.7.5 (default, Mar  9 2014, 22:15:05)
# [GCC 4.2.1 Compatible Apple LLVM 5.0 (clang-500.0.68)]
#
# site_packages = site.getusersitepackages()
#
# therefore get it from sys.path
for path in sys.path:
  if path.endswith('site-packages'):
    site_packages = path

VERSION = '3.2.0dev3'

DATA_FILES = [
  (os.path.join(site_packages, 'zms3/formulator/'), ['zms3/formulator/JSONEditor.js']),
  (os.path.join(site_packages, 'zms3/formulator/conf'), ['conf/zms3.formulator.langdict.xml']),
  (os.path.join(site_packages, 'zms3/formulator/conf'), ['conf/zms3.formulator.metaobj.xml']),
]

CLASSIFIERS = [
  'Development Status :: 3 - Alpha'
  'Framework :: ZMS3',
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
  'License :: OSI Approved :: GNU General Public License (GPL)',
]

setup(
  name                  = 'zms3.formulator',
  description           = 'JSON-based HTML-Forms',
# long_description      = README,
  version               = VERSION,
  author                = 'HOFFMANN+LIEBENBERG in association with SNTL Publishing, Berlin',
  author_email          = 'zms@sntl-publishing.com',
  url                   = 'http://www.zms-publishing.com',
  download_url          = 'https://code.zms3.com/formulator',
  namespace_packages    = ['zms3'],
  packages              = ['zms3.formulator'],
# py_modules            = ['zms3.formulator.ZMSFormulator','zms3.formulator.JSONEditor'],
  data_files            = DATA_FILES,
  classifiers           = CLASSIFIERS,
  include_package_data  = True,
  zip_safe              = False,
)