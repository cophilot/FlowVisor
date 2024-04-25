from setuptools import setup, find_packages

def get_version():
    """
    Returns the current version of the project.
    """
    
    with open('.phil-project', 'r') as f:
        text = f.read()

    for line in text.split('\n'):
        if line.startswith('version'):
            return line.split(':')[1].strip()

def get_requirements():
    with open('requirements.txt', 'r') as f:
        return f.read().split('\n')

def get_readme():
    with open('README.md', 'r') as file:
        return file.read()

# Setting up
setup(
    name='FlowVisor',
    version=get_version(),
    author='cophilot (Philipp B.)',
    author_email='<info@philipp-bonin.com>',
    license='MIT',
    url='https://github.com/cophilot/FlowVisor',
    description='Visualize and profile your python code with FlowVisor.',
    long_description_content_type='text/markdown',
    long_description=get_readme(),
    packages=find_packages(),
    install_requires=get_requirements(),
    keywords=['python', 'flow', 'visualize', 'code', 'flowvisor', 'profiling', 'profile', 'decorator'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ],
    entry_points={
        'console_scripts': [
            'add-vis=flowvisor.cli.add_vis:main',
            'remove-vis=flowvisor.cli.remove_vis:main',
            'vis-file=flowvisor.cli.vis_file:main'
        ]
    }
)


