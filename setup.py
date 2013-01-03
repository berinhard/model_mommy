import setuptools

setuptools.setup(
    name="model_mommy",
    version="0.8.1",
    packages=["model_mommy"],
    include_package_data=True,  # declarations in MANIFEST.in
    install_requires=["Django <1.5", "PIL"],
    author="Vanderson Mota",
    author_email="vandersonmota@gmail.com",
    url="http://github.com/vandersonmota/model_mommy",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="Smart object creation facility for Django.",
    keywords="django testing factory python",
)
