
from uex import UASSETP

import os
import time
import inspect
import json

def check_dir(_dir, _CID=1):
    if not os.path.isdir(_dir):
        if _dir == "":
            return 3 # 路径为空
        os.makedirs(_dir, exist_ok=True)
        _C = inspect.stack()[_CID]
        if os.path.isdir(_dir):
            print(f" [INFO] check_dir(ADIR): Auto created the \"{_dir}\" folder. (File \"{_C.filename}\", line {_C.lineno})")
            return 1 # 文件夹成功创建
        else:
            print(f" [WARN] check_dir(ADIR): Fail to created the \"{_dir}\" folder . (File \"{_C.filename}\", line {_C.lineno})")
            return 0 # 没有成功创建文件夹
    else:
        return 2 # 文件夹已存在

def write_file(file, content="", encoding="utf-8", as_json=False, as_bytes=False):
    if os.path.dirname(file) != "":
        check_dir(os.path.dirname(file), 2)
    if as_bytes:
        with open(file, "wb") as f:
            f.write(content)
    else:
        with open(file, "w", encoding=encoding) as f:
            if as_json:
                content = json.dumps(content, ensure_ascii=False, indent=2, separators=(",", ":"))
            f.write(content)
    return

while True:
    file_path = input("请输入文件路径（输入0结束程序）: ").strip()
    
    if file_path == "0":
        break
    
    if not file_path:
        print("文件路径不能为空，请重新输入。")
        continue

    if file_path[0] == "\"":
        file_path = file_path[1:-1]
    
    if not os.path.exists(file_path):
        print("文件路径无效或文件不存在，请重新输入。")
        continue

    _T = time.time()

    _UASSET = UASSETP(file_path)

    if _UASSET:
        _FILE_NAME = os.path.splitext(file_path)[0].split("\\")[-1]
        for _x_, _y_ in _UASSET["Export"].items():
            if _UASSET["Export_Map"][_x_]["Class_Name"][1] == "DataTable":
                write_file(f"out/{_FILE_NAME}.json", _UASSET["Export"][_x_]["DataTable"], as_json=True)
            elif _UASSET["Export_Map"][_x_]["Class_Name"][1] == "Texture2D":
                for _i_, _z_ in enumerate(_y_["Texture2D"]["Mips"]):
                    if _z_.get("Files"):
                        if _x_ == 1 and _i_ == 0:
                            write_file(f"out/{_FILE_NAME}.png", _z_["Files"].read(), as_bytes=True)
                        else:
                            write_file(f"out/{_FILE_NAME}_{_x_}_{_i_}.png", _z_["Files"].read(), as_bytes=True)
            elif _UASSET["Export_Map"][_x_]["Class_Name"][1] == "SpineAtlasAsset":
                write_file(f"out/{_FILE_NAME}.atlas", _y_["Export_Info"]["rawData"])
            elif _UASSET["Export_Map"][_x_]["Class_Name"][1] == "SpineSkeletonDataAsset":
                write_file(f"out/{_FILE_NAME}.json", _y_["Export_Info"]["rawData"], as_bytes=True)
        print(time.time()-_T)

