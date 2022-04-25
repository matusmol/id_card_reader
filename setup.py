import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="desko_identy_chrom_card_reader",
    version="0.0.1",
    author="Matus Mol",
    author_email="matusmol93@gmail.com",
    description="Python driver for DESKO IDenty chrom",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matusmol/id_card_reader",
    project_urls={
        "Bug Tracker": "https://github.com/matusmol/id_card_reader/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
)