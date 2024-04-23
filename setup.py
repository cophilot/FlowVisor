from setuptools import setup, find_packages

VERSION = '0.0.3'

with open('README.md', 'r') as file:
    LONG_DESCRIPTION = file.read()

# Setting up
setup(
    name='FlowVisor',
    version=VERSION,
    author='cophilot (Philipp B.)',
    author_email='<info@philipp-bonin.com>',
    license='MIT',
    url='https://github.com/cophilot/FlowVisor',
    description='Visualize the flow of your python code.',
    long_description_content_type='text/markdown',
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        'Pillow~=9.3.0',
        'diagrams~=0.23.4',
        'pickle-mixin~=1.0.2'
    ],
    keywords=['python', 'flow', 'visualize', 'code', 'flowvisor'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ]
)