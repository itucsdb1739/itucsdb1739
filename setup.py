from setuptools import setup
from pip.req import parse_requirements
from pip.download import PipSession

install_reqs = parse_requirements('requirements.txt', session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='itupass',
    packages=['itupass'],
    include_package_data=True,
    install_requires=reqs,
    setup_requires=[],
    tests_require=[],
)
