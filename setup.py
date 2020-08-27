from setuptools import setup, find_packages

setup(
    name="atsapi",
    description="An API to make some game utilites for TrekMUSH: Among The Stars available via HTTP",
    url="https://github.com/kcphysics/ATSAPI",
    author="KCPhysics",
    packages=find_packages(),
    classifiers=[
        "Programmin Language :: Python :: 3.6.8",
        "Natural Language   :: English",
        "License    :: MIT"
    ],
    entry_points={
        "console_scripts": [
        ]
    },
    zip_safe=False,
    install_requires=[
        "aiohttp",
        "aiohttp-swagger",
        "aiohttp-tokenauth",
        "importlib_resources"
    ]
)