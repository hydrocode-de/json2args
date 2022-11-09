from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


def requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()


def version():
    with open('json2args/__version__.py') as f:
        loc = dict()
        exec(f.read(), loc, loc)
        return loc['__version__']


setup(
    name='json2args',
    author='Mirko Mälicke',
    author_email='mirko@hydrocode.de',
    description='Read keyword arguments from json file automagically',
    long_description=readme(),
    long_description_content_type='text/markdown',
    license='MIT',
    version=version(),
    packages=find_packages(),
    install_requires=requirements()
)