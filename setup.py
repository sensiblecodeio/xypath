from setuptools import setup, find_packages

long_desc = """
XYPath is aiming to be XPath for spreadsheets: it offers a framework for
navigating around and extracting values from tabular data.
"""
# See https://pypi.python.org/pypi?%3Aaction=list_classifiers for classifiers

setup(
    name='xypath',
    version='1.0.5',
    description="Extract fields from tabular data with complex expressions.",
    long_description=long_desc,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
    ],
    keywords='',
    author='ScraperWiki Ltd',
    author_email='feedback@scraperwiki.com',
    url='http://scraperwiki.com',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=[],
    include_package_data=False,
    zip_safe=False,
    install_requires=[
        'messytables',
    ],
    tests_require=[],
    entry_points=\
    """
    """,
)
