from distutils.core import setup

setup(name='ha',
      version='2.0.0',
      description='High Availability for Cortx cluster',
      url='https://github.com/Seagate/cortx-ha',
      packages=[
          'ha',
          'ha/cli',
          'ha/core',
          'ha/plugin/hare',
          'ha/setup',
          'ha/resource'
          ],
      )
