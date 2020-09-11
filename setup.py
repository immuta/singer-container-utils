import setuptools

setuptools.setup(
    name="singer-conainer-utils",
    version="0.0.1",
    description="Utility classes to run Singer taps and targets in containers.",
    url="http://github.com/immuta/singer-container-utils",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["singer_container_utils"],
    author="Stephen Bailey",
    install_requires=[],
    author_email="sbailey@immuta.com",
    license="MIT",
    packages=setuptools.find_packages(),
)
