from setuptools import find_packages, setup

with open("./README.md") as readme_file:
    readme = readme_file.read()

with open("./requirements.txt") as req_file:
    requirements = req_file.read()

setup(
    name='qubot',
    version='0.0.8',
    python_requires=">=3.7",
    packages=find_packages(exclude=["tests", "examples", "docs"]),
    url='https://github.com/anthonykrivonos/qubot',
    include_package_data=True,
    license='MIT',
    author='anthonykrivonos, kenkenchuen',
    author_email='ak4483@columbia.edu, kc3334@columbia.edu',
    description='Qubot automated testing framework.',
    install_requires=requirements,
    setup_requires=[],
    long_description=readme,
    long_description_content_type="text/markdown",
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "qubot=qubot.main:main"
        ]
    }
)
