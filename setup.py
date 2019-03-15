import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requires = [
    'click>=7.0',
    'python-twitter>=3.5',
    'gevent>=1.4.0',
    'python-dateutil>=2.7.5',
    'pytimeparse>=1.1.8',
    'colorama>=0.4.1',
    'Pygments>=2.3.1',
    'sparklines>=0.4.2',
    'numpy>=1.16.2',
]

test_requires = [
    'pytest-cov',
    'pytest>=3.6.1',
    'pytest-mock>=1.10.0',
    'pytest-vcr>=1.0.1',
]

setuptools.setup(
    name="tweet-delete",
    version="0.1.11",
    author="Brenden Matthews",
    author_email="brenden@diddyinc.com",
    description="Self-destructing Tweet tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brndnmtthws/tweet-delete",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: Public Domain",
        "Operating System :: OS Independent",
    ),
    entry_points={
        'console_scripts':
        ['tweet-delete=tweet_delete.entry:cli'],
    },
    python_requires=">=3.5",
    install_requires=requires,
    tests_require=test_requires,
    extras_require={
        'test': test_requires,
    },
)
