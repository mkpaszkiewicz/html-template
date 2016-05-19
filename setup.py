from setuptools import setup

setup(name='html-template-parser',
      version='1.0',
      author='Marcin K. Paszkiewicz',
      author_email='mkpaszkiewicz@gmail.com',
      description='CSV to HTML template parser',
      packages=['html_template_parser', 'tests'],
      install_requires=[
          'PyYAML'
      ]
      )
