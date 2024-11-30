# simple-uasset-parsing
Python 的简易 UE4 资产文件 .uasset 解析，针对尘白禁区自动化收集创建。

## 提示
- 可以提取包括大部分纹理，DataTable 以及 Spine 的动画 / 切片数据，或是 Uasset 的信息数据
- 仅针对尘白禁区进行适配 UE4.26 / UE4.27，不支持 UE5+

## 使用方法

使用前可能需要安装 Wind 的相关的模块及程序

``` python
from uex import UASSETP

UASSETP(_UASSET, _UEXP, _UBULK)
```

- _UASSET - 必要
- _UEXP - 非必要 - 如果为空则会在当前目录自动查找
- _UBULK - 非必要 - 如果为空则会在当前目录自动查找

## 或者直接使用示例 .example.py

这里也需要安装 Wind 的相关的模块及程序才能使用

``` cmd
py uex.py
```

运行后根据提示拖入 .uasset (或是 .uexp/.ubulk) 资产，会自动收集并存放在 out 文件夹。