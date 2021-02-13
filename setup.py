from setuptools import find_packages, setup

with open("./README.md") as readme_file:
    readme = readme_file.read()

with open("./requirements.txt") as req_file:
    requirements = req_file.read()

setup(
    name='qubot',
    version='0.1.0',
    python_requires=">=3.7",
    packages=find_packages(exclude=["tests"]),
    url='https://github.com/anthonykrivonos/qubot',
    include_package_data=True,
    license='MIT',
    author='anthonykrivonos',
    author_email='anthony.k@columbia.edu',
    description='Qubot automated testing framework.',
    install_requires=requirements,
    setup_requires=[],
    long_description=readme,
    zip_safe=False,
)
