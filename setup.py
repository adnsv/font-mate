from setuptools import setup, find_packages

setup(
    name='font-mate',
    version='0.1.0',
    packages=find_packages(),
    py_modules=['main'],
    install_requires=[
        'fonttools',   # for fontTools.ttLib.TTFont
        'ufoLib2',     # for working with UFO fonts
        'ufo2ft',      # for compiling UFO fonts to TTF/OTF
        'setuptools_scm',
    ],
    entry_points={
        'console_scripts': [
            'font-mate=main:main'  # Entry point to your root-level main.py script
        ],
    },
    description='A tool for font merging and coverage analysis.',
    author='Alex Denisov',
    author_email='alex.a.denisov@gmail.com',
    url='https://github.com/adnsv/font-mate',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    use_scm_version=True,
)
