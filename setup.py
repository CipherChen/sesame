import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sesame",
    version="0.0.1",
    author="Cipher Chen",
    author_email="cipher.chen2012@gmail.com",
    description="Manage passwords yourself.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CipherChen/sesame",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
