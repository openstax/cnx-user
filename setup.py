
'''
setup.py for rhaptos2

'''

from distutils.core import setup
import os, glob

def get_version():

    '''return version from fixed always must exist file

       Making very broad assumptions about the 
       existence of files '''
    
    v = open('rhaptos2/user/version.txt').read().strip()
    return v




def main():

    setup(name='rhaptos2.user',
          version=get_version(),
          packages=['rhaptos2.user',
                   ],
          namespace_packages = ['rhaptos2'],
          author='See AUTHORS.txt',
          author_email='info@cnx.org',
          url='https://github.com/Connexions/rhaptos2.user',
          license='LICENSE.txt',
          description='User functions for rhaptos2',
          long_description='see description',
          install_requires=[
              "flask >= 0.8"
              ,"statsd"
              ,"requests"
              ,"pylint"
              ,"python-memcached"
              ,"nose"
              ,"rhaptos2.common"
              ,"unittest-xml-reporting"
              ,"mikado.oss.doctest_additions"
                           ],
          scripts=glob.glob('scripts/*'),

          package_data={'rhaptos2.user': ['templates/*.*', 
                                          'static/*.*', 
                                           'version.txt', 
                                           'tests/*.*'],
                        },

         

          
          )



if __name__ == '__main__':
    main()

