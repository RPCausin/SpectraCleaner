from setuptools import setup, find_packages

import codecs
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    func = lambda name, enc=ascii: {True: enc}.get(name=='mbcs')
    codecs.register(func)

setup(
    name = 'SpectraCleaner',
    version = '0.1.0',
    author = "Raul Perea",
    author_email = "rpcausin@gmail.com",
    description = "Visualize and remove spectra with OPUS format.",
    packages = find_packages(),
    install_requires = ['AnyQt', 'opusFC', 'pyqtgraph'],
    entry_points = {
	'gui_scripts': [
        'SpectraCleaner = SpectraCleaner.SpectraCleaner:main']
        }
)
