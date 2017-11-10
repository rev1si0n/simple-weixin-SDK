import setuptools

requirements = open('./requirements.txt').readlines()

setuptools.setup(
    name='weixin',
    packages=setuptools.find_packages(),
    version="0.1.5.20171110",
    description="一个Python跨网络框架的小型微信公众号开发包。",
    author="Zhang Yi Da",
    url="https://github.com/LUSG/weixin-SDK",
    license='MIT',
    platforms=['any'],
    install_requires=requirements,
)
