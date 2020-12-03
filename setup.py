from setuptools import find_packages, setup

setup(
    name='cisca_admin',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)
