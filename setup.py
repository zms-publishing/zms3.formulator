import os
from setuptools import setup

VERSION = '3.2.0dev'

DEPENDENCY_LINKS = [
]

INSTALL_REQUIRES = [
]

PACKAGE_DATA = []
# Exclude special folders and files
for dirpath, dirnames, filenames in os.walk('./zms3'):
  if (
    '.'                           != dirpath and
    '.settings'                   not in dirpath and
    '.svn'                        not in dirpath 
    ): 
    if filenames: 
      for filename in filenames:
        if filename != '.DS_Store':
          PACKAGE_DATA.append(dirpath[2:]+'/%s' % filename)
# Include files from root path (because '.' is exclude above)
PACKAGE_DATA.append('*.js')

CLASSIFIERS = [
  'License :: OSI Approved :: GNU General Public License (GPL)',
  'Environment :: Web Environment',
  'Framework :: Zope2',
  'Programming Language :: Python :: 2.7',
  'Operating System :: OS Independent',
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
]

setup(
  name                  = 'zms3.formulator',
  description           = '',
#  long_description      = README,
  version               = VERSION,
  author                = 'HOFFMANN+LIEBENBERG in association with SNTL Publishing, Berlin',
  author_email          = 'zms@sntl-publishing.com',
  url                   = 'http://www.zms-publishing.com',
  download_url          = 'https://code.zms3.com/formulator',
  install_requires      = INSTALL_REQUIRES,
  dependency_links      = DEPENDENCY_LINKS,
  namespace_packages    = ['zms3'],
  packages              = ['zms3.formulator'],
#  package_dir           = {'zms3.formulator': '.'},
  package_data          = {'zms3.formulator': PACKAGE_DATA},
  classifiers           = CLASSIFIERS,
  include_package_data  = True,
  zip_safe              = False,
)