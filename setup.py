import setuptools
from os.path import join, dirname


setuptools.setup(
    name="model_mommy",
    version="0.8.1",
    author="Vanderson Mota",
    author_email="vandersonmota@gmail.com",
    url="http://github.com/vandersonmota/model_mommy",
    license="Apache 2.0",
    description="Smart object creation facility for Django.",
    long_description=open(join(dirname(__file__), "README.rst")).read(),
    packages=["model_mommy"],
    include_package_data=True,  # declarations in MANIFEST.in
    install_requires=["Django <1.5", "PIL"],
    keywords="django testing factory python",
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
    ],
)
