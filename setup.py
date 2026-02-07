from setuptools import setup, find_packages

setup(
    name="dbbox",
    version="0.1.0",
    author="Jeff Mirabile",
    author_email="jmmirabile@gmail.com",
    description="Simple SQLite database utility with CRUD operations via CLI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jmmirabile/dbbox",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "confbox>=0.1.0",
    ],
    entry_points={
        "console_scripts": [
            "dbbox=dbbox.cli:main",
        ],
    },
    license="MIT",
)
