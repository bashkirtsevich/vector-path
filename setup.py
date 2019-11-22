from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="vector-path",
    version="0.0.1",
    description="Simply vector path parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=["Programming Language :: Python"],
    keywords="vector path svg",
    author="D.Bashkirtsevich",
    author_email="bashkirtsevich@gmail.com",
    url="https://github.com/bashkirtsevich/vector-path",
    license="MIT License",
    include_package_data=True,
    zip_safe=True,
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.6.*"
)
