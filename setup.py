from setuptools import setup, find_packages

setup(
    name='steam_beautifier',
    version='0.1.0',
    packages=find_packages('src'),  # Search for packages under 'src'
    package_dir={'': 'src'},        # Root directory for packages is 'src'
    include_package_data=True,
    install_requires=[
        'Pillow==10.3.0',
        'requests==2.31.0',
    ],
    entry_points={
        'console_scripts': [
            'steam_beautifier=steam_beautifier:main',
        ],
    },
    author='Andrew',
    author_email='',
    description='Improves the visual aesthetics of Steam Libraries.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/cheex0r/SteamBeautifier',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
