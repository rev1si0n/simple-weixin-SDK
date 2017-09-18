import setuptools

requirements = [
    'IPy>=0.83',
    'msgpack-python>=0.4.8',
    #'pycrypto>=2.6.1',
    'requests>=2.18.4',
    'xmltodict>=0.11.0',
    'PyMySQL>=0.7.11',
    'redis>=2.10.6'
    ]


setuptools.setup(
    name='weixin',
    packages=setuptools.find_packages(),
    version="0.1.0",
    description="一个Python跨网络框架的小型微信公众号开发包。",
    author="Zhang Yi Da",
    url="https://github.com/thisforeda/weixin-Python-SDK",
    license='MIT',
    platforms=['any'],
    install_requires=requirements,
)
