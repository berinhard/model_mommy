import sys
import setuptools

setuptools.setup(
    name="model_mommy",
    version="0.5",
    packages=["model_mommy",],
    install_requires=["django",],
    author="vandersonmota",
    author_email="vandersonmota@gmail.com",
    url="http://github.com/vandersonmota/model_mommy",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="automatic object creation facility for django",
    keywords="django testing factory python",
)
