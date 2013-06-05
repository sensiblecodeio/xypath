from setuptools import setup, find_packages

long_desc = """
XYPath is aiming to be XPath for spreadsheets: it offers a framework for
navigating around and extracting values from tabular data.
"""


setup(
    name='xypath',
    version='0.1.0',
    description="Extract fields from tabular data with complex expressions.",
    long_description=long_desc,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        #"License :: OSI Approved :: MIT License" TODO,
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
    ],
    keywords='',
    author='ScraperWiki Ltd',
    author_email='feedback@scraperwiki.com',
    url='http://scraperwiki.com',
    # license='MIT', TODO
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=[],
    include_package_data=False,
    zip_safe=False,
    install_requires=[
        'messytables>=0.10.0',
    ],
    tests_require=[],
    entry_points=\
    """
    """,
)
