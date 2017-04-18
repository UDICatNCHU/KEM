from distutils.core import setup

setup(
    name = 'kem',
    packages = ['kem'],
    version = '1.0',
    description = 'A django App for kem',
    author = ['davidtnfsh', 'theshaneyu'],
    author_email = 'davidtnfsh@gmail.com',
    url = 'https://github.com/udicatnchu/kem',
    download_url = 'https://github.com/udicatnchu/kem/archive/v1.0.tar.gz',
    keywords = ['kem', 'gensim'],
    classifiers = [],
    license='GPL3.0',
    install_requires=[
        'numpy==1.11.1',
        'scipy==0.18.0',
        'gensim==0.13.2'
    ],
    zip_safe=True,
)
