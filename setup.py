from setuptools import setup, find_packages

setup(
    name="data-analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "rich>=13.0.0",
        "pytest>=7.0.0",
        "python-dotenv>=1.0.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "geopandas>=0.10.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "data-analyzer=data_analyzer.cli:cli",
        ],
    },
) 