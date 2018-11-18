import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sesame",
    version="1.0",
    author="Cipher Chen",
    author_email="cipher.chen2012@gmail.com",
    description="Passwords in my own.",
    url="https://github.com/CipherChen/sesame",
    packages=setuptools.find_packages(),
    scripts=["bin/sesame"],
    install_requires=[
        "pycrypto>=2.6.1",
    ],
    data_files=[
        ("%s/.sesame" % os.environ["HOME"], ["default/config.yaml"]),
    ],
)
