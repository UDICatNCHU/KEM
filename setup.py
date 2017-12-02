from distutils.core import setup

setup(
    name = 'kem',
    packages=['kem'],
    package_dir={'kem':'kem'},
    package_data={'kem':['management/commands/*']},
    version = '2.6',
    description = 'A django App for kem',
    author = ['davidtnfsh', 'theshaneyu'],
    author_email = 'davidtnfsh@gmail.com',
    url = 'https://github.com/udicatnchu/kem',
    download_url = 'https://github.com/udicatnchu/kem/archive/v2.6.tar.gz',
    keywords = ['kem', 'gensim'],
    classifiers = [],
    license='GPL3.0',
    install_requires=[
        'simplejson',
        'numpy==1.12.1',
        'scipy==0.18.0',
        'gensim',
        'ngram'
    ],
    zip_safe=True,
)
