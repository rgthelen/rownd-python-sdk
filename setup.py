from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rownd-flask",
    version="0.1.0",
    author="Rownd",
    author_email="support@rownd.io",
    description="Official Rownd SDK for Flask",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rgthelen/rownd-python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "Flask>=2.0.0",
        "requests>=2.31.0",
        "python-jose[cryptography]>=3.3.0",
        "pydantic>=2.0.0",
        "aiohttp>=3.9.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "cryptography>=42.0.0",
        "PyJWT>=2.0.0"

    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "cryptography>=42.0.0",
            "requests>=2.31.0",
            "aiohttp>=3.8.0",
            "pytest>=7.4.4",
            "PyJWT>=2.0.0"
        ]
    }
)
