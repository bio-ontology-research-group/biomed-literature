import setuptools


setuptools.setup(
    name="biolit",
    version="0.0.1",
    description="Concept associations in biomedical literature",
    long_description=open("readme.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bio-ontology-research-group/biomed-literature",
    packages=setuptools.find_packages(),
    install_requires=['pronto', 'elasticsearch'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 1 - Planning"]
)
