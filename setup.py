from setuptools import find_packages, setup

# Extract version information from Omniduct _version.py
version_info = {}
with open('interface_meta/_version.py') as version_file:
    exec(version_file.read(), version_info)

# Extract long description from readme
with open('README.md') as readme:
    long_description = ""
    while True:
        line = readme.readline()
        if line.startswith('`interface_meta`'):
            long_description = line
            break
    long_description += readme.read()

setup(
    # Package metadata
    name="interface_meta",
    versioning='post',
    version=version_info['__version__'],
    author=version_info['__author__'],
    author_email=version_info['__author_email__'],
    url="https://github.com/matthewwardrop/interface_meta",
    description=(
        ""
    ),
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    # Package details
    packages=find_packages(),

    # Dependencies
    setup_requires=['setupmeta'],
    install_requires=version_info['__dependencies__']
)
