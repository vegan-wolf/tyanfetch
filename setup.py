from setuptools import setup, find_packages

setup(
    name='tyanfetch',
    version='0.1',
    packages=find_packages(),
    package_data={"tyanfetch": ["pics/*"]},
    install_requires=[
        'psutil==7.2.2',
    ],
    entry_points={
        'console_scripts': [
            'tyanfetch=tyanfetch:cli',
        ]
    },
)