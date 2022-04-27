# ShigureBot

[![wakatime](https://wakatime.com/badge/user/b61b0f9a-f40b-4c82-bc51-0a75c67bfccf/project/c1344e53-6345-4e5f-9adc-7332f74bff44.svg)](https://wakatime.com/badge/user/b61b0f9a-f40b-4c82-bc51-0a75c67bfccf/project/c1344e53-6345-4e5f-9adc-7332f74bff44)

为自己Bot写的插件集

## 依赖

- 需求
    - Python `>=3.10`  
      （由于使用了python新版本特性，python版本低于3.10将无法正常使用本项目）
    - nonebot2 `>=2.0.0b1`
    - More...（在`pyproject.toml`）
- 安装
    - 项目使用`poetry`安装依赖，如果没有安装，请使用下面的命令安装
      ```
      pip install poetry
      ```
      在本项目`pyprojrct.toml`同目录下执行下面的命令
      ```
      poetry install
      ```

## 使用

### 整个项目

#### 使用项目`bot.py`启动

- 通过脚手架启动（推荐）

  本项目依赖项内**不**包含脚手架，如果你没有安装，请使用下面的命令安装
  ```
  pip install nb-cli
  ```
  在`bot.py`所在文件夹下，执行下面的命令通过脚手架启动项目
  ```
  nb run
  ```
- 直接使用`bot.py`启动 在`bot.py`所在目录下，执行下面的命令启动项目
  ```
  python bot.py
  ```

#### 使用现有`nonebot`项目启动

将`src/plugins/shigure_bot`目录放在你现有项目的插件文件夹下（可能为`src/plugins`或`{项目名}/plugins`文件夹）后安装依赖即可使用

### 单个插件

本项目所有单个插件放置在`src/plugins/shigure_bot/plugins`目录下。由于本项目所有带配置的插件均使用项目自有的配置文件系统，如果想要单独使用，请先尝试下面的方法

- 对单个插件`config.py`进行修改 （详细方法请自行看插件源码摸索，或者参考我的单品插件（以后会有））
- 将项目`_config`插件放置于本项目单品插件同级目录下加载
- 使用我的单品插件（以后可能会有）

## 单品插件列表

请查看`src/plugins/shigure_bot/plugins`目录，每个插件我都会写单独的`README.md`
，也可以参考[这里](https://shigure.lgc2333.top/#/?id=%e8%87%aa%e5%b7%b1%e5%86%99%e7%9a%84-nonebot2-%e6%8f%92%e4%bb%b6)

## 联系我/赞助

如果项目使用过程中有任何问题，欢迎联系我  
[个人资料](https://github.com/lgc2333/lgc2333/README.md)
