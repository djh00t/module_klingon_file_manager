from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("VERSION", "r") as version_file:
    version = version_file.read().strip()

setup(
    name='gobbler_file_manager',
    version=version,
    author='David Hooton',
    author_email='gobbler_file_manager@hooton.org',
    description='A Python module for managing files on both local and AWS S3 storage.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/djh00t/gobbler-file-manager',
    packages=find_packages(),
    install_requires=[
        'boto3>=1.18,<2.0',
        'pytest>=6.2,<7.0',
        'python-dotenv>=0.19,<1.0',
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
