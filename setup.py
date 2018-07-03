from setuptools import setup, find_packages

setup(name='instana',
      version='0.10.1',
      download_url='https://github.com/instana/python-sensor',
      url='https://www.instana.com/',
      license='MIT',
      author='Instana Inc.',
      author_email='peter.lombardo@instana.com',
      description='Metrics sensor and distributed trace collector for Instana',
      packages=find_packages(exclude=['tests', 'examples']),
      long_description="The instana package provides Python metrics and traces for Instana.",
      zip_safe=False,
      install_requires=['autowrapt>=1.0',
                        'fysom>=2.1.2',
                        'opentracing>=1.2.1,<2.0',
                        'basictracer<3.0'],
      entry_points={
                    'instana':  ['string = instana:load'],
                    'flask':    ['flask = instana.flaskana:hook'],
                    'runtime':  ['string = instana:load'],  # deprecated: use same as 'instana'
                    'django':   ['string = instana:load'],  # deprecated: use same as 'instana'
                    'django19': ['string = instana:load'],  # deprecated: use same as 'instana'
                    },
      extras_require={
        'test': [
            'nose>=1.0',
            'flask>=0.12.2',
            'lxml>=3.4',
            'MySQL-python>=1.2.5;python_version<="2.7"',
            'requests>=2.17.1',
            'urllib3[secure]>=1.15',
            'spyne>=2.9',
            'suds-jurko>=0.6'
        ],
      },
      test_suite='nose.collector',
      keywords=['performance', 'opentracing', 'metrics', 'monitoring'],
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: Software Development :: Libraries :: Python Modules'])
