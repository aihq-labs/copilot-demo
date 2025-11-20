"""
Setup configuration for Microsoft Copilot Agent SDK
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="copilot-agent-sdk",
    version="1.0.0",
    description="Python SDK for Microsoft Copilot Studio agents (Python 3.12 optimized)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AIHQ.ie",
    author_email="info@aihq.ie",
    url="https://www.aihq.ie",
    packages=find_packages(),
    python_requires=">=3.8,<3.13",  # Microsoft Agents SDK limitation
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "copilot-cli=cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        # Python 3.13 not yet supported by microsoft-agents-*
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    keywords="microsoft copilot agent sdk ai chatbot python312",
    project_urls={
        "Homepage": "https://www.aihq.ie",
        "Documentation": "https://github.com/aihq-labs/copilot-demo#readme",
    },
)
