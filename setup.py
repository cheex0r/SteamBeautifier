from setuptools import setup, find_packages

# Read requirements.txt
def parse_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line and not line.startswith('#')]

# Read version.py
def get_version():
    with open('src/version.py', 'r') as f:
        return f.read().split('=')[1].strip().strip('"').strip("'")

setup(
    name='steam_beautifier',
    version=get_version(),
    packages=find_packages('src'),  # Search for packages under 'src'
    package_dir={'': 'src'},        # Root directory for packages is 'src'
    include_package_data=True,
    install_requires=parse_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            'steam-beautifier=main:main',  # Point to the main function in src/main.py
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
