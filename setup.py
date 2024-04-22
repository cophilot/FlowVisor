from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Visualize the flow of your python code.'

# Setting up
setup(
    name="FlowVisor",
    version=VERSION,
    author="cophilot (Philipp B.)",
    author_email="<info@philipp-bonin.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description='Visualize the flow of your python code.',
    packages=find_packages(),
    install_requires=['diagrams', 'Pillow'],
    keywords=['python', 'flow', 'visualize', 'code', 'flowvisor', 'neuralnine'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)