### Python项目目录结构
---
- 目录组织方式
```
假设你的项目名为foo：

Foo/
|-- scripts/
|   |-- foo
|
|-- foo/
|   |
|   |-- __init__.py
|   |-- main.py
|-- tests/
|   |
|   |-- __init__.py
|   |-- test_main.py
|-- docs/
|   |--png、gif
|   |--html
|   |--说明文档.md
|
|-- setup.py
|-- requirements.txt
|-- README
|-- conf.cfg
|-- .gitignore
简要解释一下:

bin/: 存放项目的一些可执行文件，当然你可以起名script/之类的也行。
foo/: 存放项目的所有源代码。(1) 源代码中的所有模块、包都应该放在此目录。不要置于顶层目录。(2) 其子目录tests/存放单元测试代码； (3) 程序的入口最好命名为main.py。
docs/: 存放一些文档。
setup.py: 安装、部署、打包的脚本。
requirements.txt: 存放软件依赖的外部Python包列表。
README: 项目说明文件。
除此之外，有一些方案给出了更加多的内容。比如LICENSE.txt,ChangeLog.txt文件等，我没有列在这里，因为这些东西主要是项目开源的时候需要用到。
```
- README内容
    - 描述项目信息，内容需包括
        1. 软件定位，软件基本功能
        2. 运行代码的方法：安装环境、启动命令等。
        3. 简要的使用说明
        4. 代码目录结构，或软件的级别原理
        5. 常见问题说明
- setup.py
    - 用setup.py来管理代码的打包、安装、部署问题。对于Python业界采用流行的打包工具setuptools来管理。参考flask的setup.py
- requirements.txt
    - 目的用处
        1. 方便维护软件包依赖，开发过程中新增的包添加进这个列表、避免在setup.py安装依赖时漏掉
        2. 方便读者明确项目使用了那些Python包
        3. 文件的每一行包含一个依赖包说明，要求格式能被pip识别。通过pip install -r requirements.txt来把所有包都装好,参考：https://pip.readthedocs.io/en/1.1/requirements.html
- 配置文件处理cfg
    - 以config.py的形式放在doc目录下
    - 以.cfg的形式放在顶层目录下