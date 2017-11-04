from setuptools import setup, find_packages

with open('requirements.txt') as rf:
    requirements = rf.readlines()


def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='voxelviz',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'Click',
    ],
    include_package_data=True,
    entry_points='''
        [console_scripts]
        vxv=voxelviz.app:vxv
        vxv_download_data=voxelviz.utils:download_data
    '''
)
