import setuptools

with open("README.md", "r") as doc:
    long_description = doc.read()

setuptools.setup(
    name='mediaserver_processor',
    version='0.0.3',
    author='Job Veldhuis',
    author_email='job@baukefrederik.me',
    description='Python script for mediaserver watching, resizing and adding files to a source set.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jobveldhuis/python-mediaserver-processor',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'watchgod',
        'pillow',
        'pyYaml'
    ],
    entry_points='''
    [console_scripts]
    mediaserver_processor=mediaserver_processor.__main__:main
    ''',
    python_requires='>=3.6'
)
