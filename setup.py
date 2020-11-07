from setuptools import setup

setup(
    name="bgmtinygrail",
    version="0.1",
    install_requires=[
        'aiohttp',
        'beautifulsoup4',
        'click',
        'flask',
        'inflection',
        'lazy-object-proxy',
        'pydantic',
        'requests',
        'sqlalchemy',
        'systemd;platform_system!="Windows"',
        'tabulate[widechars]',
    ],
    extras_requires={
        'tests': ['pytest', 'pytest_mock'],
    },
)
