# TODO set requirement files / add URL / add Keywords

from setuptools import setup, find_packages

setup(name='uisdata',
      packages=find_packages(exclude=['tests']),
      version='0.1',
      license='MIT',
      description='UIS data select, metadata and label merge',
      long_description=open('README.md').read(),
      author='UIS_DAO_M_Murphy',
      author_email='m.murphy@unesco.org',
      url='https://github.com/Max-Murphy-code/uisdata.git',
      #download_url='https://github.com/Max-Murphy-code/uisdata/archive/uisdata-0.1.tar.gz',
      keywords = ['', '', ''],
      setup_requires=['pandas', 'numpy'],
      classifiers=[
            'Development Status :: 3 - Alpha',
            # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
            'Intended Audience :: Data analysts, developers',  # Define that your audience are developers
            'Topic :: Software Development :: Build Tools',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3'
      ],
      zip_safe=False
      )
