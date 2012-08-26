import setuptools

setuptools.setup(
    name="model_mommy",
    version="0.8",
    packages=["model_mommy"],
    include_package_data=True,  # declarations in MANIFEST.in
    install_requires=["Django <1.5"],
    author="vandersonmota",
    author_email="vandersonmota@gmail.com",
    url="http://github.com/vandersonmota/model_mommy",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="automatic object creation facility for django",
    keywords="django testing factory python",
)
