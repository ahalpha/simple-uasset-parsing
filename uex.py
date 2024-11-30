
import struct
import os
import time
import io
import uuid
from wand.image import Image

IS_PRINT = False
IS_PRINT_TYPE = False
ONE_MIP = True
_RE_SAVE = False

PF_TO_DXGI_MAP = {
    "PF_A8R8G8B8": "DXGI_FORMAT_B8G8R8A8_UNORM",
    "PF_X8R8G8B8": "DXGI_FORMAT_B8G8R8X8_UNORM",
    "PF_R8G8B8": "DXGI_FORMAT_R8G8B8A8_UNORM",
    "PF_A1R5G5B5": "DXGI_FORMAT_B5G5R5A1_UNORM",
    "PF_A4R4G4B4": "DXGI_FORMAT_B4G4R4A4_UNORM",
    "PF_R5G6B5": "DXGI_FORMAT_B5G6R5_UNORM",
    "PF_R32F": "DXGI_FORMAT_R32_FLOAT",
    "PF_G16R16F": "DXGI_FORMAT_R16G16_FLOAT",
    "PF_A16B16G16R16F": "DXGI_FORMAT_R16G16B16A16_FLOAT",
    "PF_R16F": "DXGI_FORMAT_R16_FLOAT",
    "PF_DXT1": "DXGI_FORMAT_BC1_UNORM",
    "PF_DXT3": "DXGI_FORMAT_BC2_UNORM",
    "PF_DXT5": "DXGI_FORMAT_BC3_UNORM",
    "PF_BC4": "DXGI_FORMAT_BC4_UNORM",
    "PF_BC5": "DXGI_FORMAT_BC5_UNORM",
}

DXGI_TO_BPP_MAP = {
    "DXGI_FORMAT_R32G32B32A32_FLOAT": 16,
    "DXGI_FORMAT_R32G32B32A32_UINT": 16,
    "DXGI_FORMAT_R16G16B16A16_FLOAT": 8,
    "DXGI_FORMAT_R16G16B16A16_UINT": 8,
    "DXGI_FORMAT_R8G8B8A8_UNORM": 4,
    "DXGI_FORMAT_R8G8B8A8_UINT": 4,
    "DXGI_FORMAT_B8G8R8A8_UNORM": 4,
    "DXGI_FORMAT_B8G8R8X8_UNORM": 4,
    "DXGI_FORMAT_R32_FLOAT": 4,
    "DXGI_FORMAT_R32_UINT": 4,
    "DXGI_FORMAT_R16_FLOAT": 2,
    "DXGI_FORMAT_R16_UINT": 2,
    "DXGI_FORMAT_R8_UINT": 1,
    "DXGI_FORMAT_BC1_UNORM": 0.5,
    "DXGI_FORMAT_BC2_UNORM": 1,
    "DXGI_FORMAT_BC3_UNORM": 1,
    "DXGI_FORMAT_BC4_UNORM": 0.5,
    "DXGI_FORMAT_BC5_UNORM": 1
}

DXGI_TO_VALUE_MAP = {
    "DXGI_FORMAT_R32G32B32A32_FLOAT": 2,
    "DXGI_FORMAT_R32G32B32A32_UINT": 3,
    "DXGI_FORMAT_R16G16B16A16_FLOAT": 10,
    "DXGI_FORMAT_R16G16B16A16_UINT": 11,
    "DXGI_FORMAT_R8G8B8A8_UNORM": 28,
    "DXGI_FORMAT_R8G8B8A8_UINT": 30,
    "DXGI_FORMAT_B8G8R8A8_UNORM": 87,
    "DXGI_FORMAT_B8G8R8X8_UNORM": 88,
    "DXGI_FORMAT_R32_FLOAT": 41,
    "DXGI_FORMAT_R32_UINT": 42,
    "DXGI_FORMAT_R16_FLOAT": 54,
    "DXGI_FORMAT_R16_UINT": 57,
    "DXGI_FORMAT_R8_UINT": 61,
    "DXGI_FORMAT_BC1_UNORM": 71,
    "DXGI_FORMAT_BC2_UNORM": 74,
    "DXGI_FORMAT_BC3_UNORM": 77,
    "DXGI_FORMAT_BC4_UNORM": 80,
    "DXGI_FORMAT_BC5_UNORM": 83
}

STRUCT_PROPERTY_VARIANT_RULE = {
    "IntPoint": {"X": "IntProperty", "Y": "IntProperty"},
    "FrameNumber": {"Value": "IntProperty"},
    "Guid": {"GUID": "Guid"},
    "Vector2D": {"X": "FloatProperty", "Y": "FloatProperty"},
    "Vector": {"X": "FloatProperty", "Y": "FloatProperty", "Z": "FloatProperty"},
    "Vector4": {"X": "FloatProperty", "Y": "FloatProperty", "Z": "FloatProperty", "W": "FloatProperty"},
    "SoftClassPath": {"AssetPathName": "NameProperty", "SubPathString": "StrProperty"},
    "SoftObjectPath": {"AssetPathName": "NameProperty", "SubPathString": "StrProperty"},
    "Rotator": {"Pitch": "FloatProperty", "Yaw": "FloatProperty", "Roll": "FloatProperty"},
    "Quat": {"X": "FloatProperty", "Y": "FloatProperty", "Z": "FloatProperty", "W": "FloatProperty"},
    "LinearColor": {"R": "FloatProperty", "G": "FloatProperty", "B": "FloatProperty", "A": "FloatProperty"},
    "PerPlatformFloat": {"bCooked": "IntProperty", "Value": "IntProperty"},
    "MovieSceneFrameRange": {"LowerBound_Type": "ByteProperty*1", "UpperBound_Type": "ByteProperty*1", "LowerBound_Value": "IntProperty", "UpperBound_Value": "IntProperty"},
    "Tangent": { "ArriveTangent": "FloatProperty", "LeaveTangent": "FloatProperty", "ArriveTangentWeight": "FloatProperty", "LeaveTangentWeight": "FloatProperty", "TangentWeightMode": "IntProperty"}
}

UASSAT_PARSE = {}

def UASSETP(_UASSET, _UEXP=None, _UBULK=None, _SIMPLIFY=True):
    print(_UASSET, _UEXP)

    if _UASSET[-7:] != ".uasset":
        _UASSET = os.path.splitext(_UASSET)[0]+".uasset"
    if _UEXP == None:
        _UEXP = os.path.splitext(_UASSET)[0]+".uexp"
    elif _UEXP[-5:] != ".uexp":
        _UEXP = os.path.splitext(_UEXP)[0]+".uexp"
    if _UBULK == None:
        _UBULK = os.path.splitext(_UASSET)[0]+".ubulk"
    elif _UBULK[-6:] != ".ubulk":
        _UBULK = os.path.splitext(_UBULK)[0]+".ubulk"

    if not os.path.isfile(_UASSET):
        print(f" [WARN] read_text_excel: 未能加载文件 \"{_UASSET}\"")
        return
    if not os.path.isfile(_UEXP):
        _UEXP = None
    if not os.path.isfile(_UBULK):
        _UBULK = None
    
    UASSAT_PARSE["SIMPLIFY"] = _SIMPLIFY

    # print(f"Uasset: \"{_UASSET}\"\nUexp: \"{_UEXP}\"\nUbulk: \"{_UBULK}\"")
    # return

    UASSAT_PARSE["DATA"] = {}
    UASSAT_PARSE["EXPORT_ITEMS"] = None

    with open(_UASSET, "rb") as F:
        UASSAT_PARSE["FILE"] = memoryview(F.read())
        UASSAT_PARSE["OFFSET"] = 0

    PC(["Header"])
    PD("Magic_Number", "Byte*4")
    PD("File_Version")
    PD("Licensee_Version")
    PD("Custom_Version", "Byte*12")
    PD("Uasset_Size")
    PD("Package_Name", "String")
    PD("Package_Flags", "Uint32")
    PD("Name_Count")
    PD("Name_Offset")
    PD("Gatherable_Text_DataCount")
    PD("Gatherable_Text_DataOffset")
    PD("Export_Count")
    PD("Export_Offset")
    PD("Import_Count")
    PD("Import_Offset")
    PD("Depends_Offset")
    PD("Soft_Package_References_Count")
    PD("Soft_Package_References_Offset")
    PD("Searchable_Names_Offset")
    PD("Thumbnail_Table_Offset")
    AD("GUID", uuid.UUID(bytes=P("Byte*16")))
    PD("Generation_Count")
    PD("Generations", f"Int32Array*{CD("Generation_Count")*2}")
    PD("Saved_By_Engine_Version", "Byte*14")
    PD("Compatible_With_Engine_Version", "Byte*14")
    PD("Compression_Flags", "Byte*8")
    PD("Package_Source", "Uint32")
    PD("Additional_Package_Flags")
    PD("Asset_Registry_Data_Offset")
    PD("Bulk_Data_Start_Offset")
    PD("World_Tile_Info_Data_Offset")
    PD("Chunk_IDs", "Int32Array*2")
    PD("Preload_Dependency_Count")
    PD("Preload_Dependency_Offset")

    for _i_ in range(UASSAT_PARSE["DATA"]["Header"]["Name_Count"]):
        PC(["Name_Map", _i_])
        PD("Name", "String")
        PD("Hash", "Byte*4")

    for _i_ in range(UASSAT_PARSE["DATA"]["Header"]["Import_Count"]):
        PC(["Import_Map", -_i_-1])
        PD("Class_Package_Name", "Name")
        PD("Class_Name", "Name")
        PD("Outer_Index")
        PD("Object_Name", "Name")
        
    for _i_ in range(UASSAT_PARSE["DATA"]["Header"]["Export_Count"]):
        PC(["Export_Map", _i_+1])
        PD("Class_Index")
        AD("Class_Name", GET_IENAME("Class_Index"))
        PD("Super_Index")
        AD("Super_Name", GET_IENAME("Super_Index"))
        PD("Template_Index")
        AD("Template_Name", GET_IENAME("Template_Index"))
        PD("Outer_Index")
        PD("Name", "Name")
        PD("Object_Flags")
        PD("Serial_Size", "Int64")
        PD("Serial_Offset", "Int64")
        PD("Forced_Export", "Bool")
        PD("Not_For_Client", "Bool")
        PD("Not_For_Server", "Bool")
        PD("Split", "*1")
        PD("Package_GUID", "*16")
        PD("Package_Flags")
        PD("Padding", "*36")

    if not _UEXP: return UASSAT_PARSE["DATA"]
    with open(_UEXP, "rb") as F:
        CURR_UEXP_CACHE = memoryview(F.read())
        CURR_UEXP_OFFSET = 0
        
    # global IS_PRINT
    _TIME_CACHE_ = time.time()
    for _CURR_EXPORT_ID, _CURR_EXPORT_DATA in UASSAT_PARSE["DATA"]["Export_Map"].items():
        UASSAT_PARSE["FILE"] = CURR_UEXP_CACHE[CURR_UEXP_OFFSET:CURR_UEXP_OFFSET+_CURR_EXPORT_DATA["Serial_Size"]]
        CURR_UEXP_OFFSET += _CURR_EXPORT_DATA["Serial_Size"]
        UASSAT_PARSE["OFFSET"] = 0
        PC(["Export", _CURR_EXPORT_ID, "Export_Info"])
        while PARSE_PROP(): pass
        
        if _CURR_EXPORT_DATA["Class_Name"][1] == "DataTable":
            PC(["Export", _CURR_EXPORT_ID, "DataTable"])
            PD("Null_Bytes", "*4")
            _ROW_NUM = PD("Table_Height", _save=False)
            for _n_ in range(_ROW_NUM):
                _ROW_NAME = PD("Row_Name", "Name", _save=False)
                PC(["Export", _CURR_EXPORT_ID, "DataTable", _ROW_NAME[3]])
                # if _n_ == 9999: IS_PRINT = True
                while PARSE_PROP(): pass
                # if _n_ == 9999: break
            print(f"{_n_} ({time.time()-_TIME_CACHE_})")
        
        elif _CURR_EXPORT_DATA["Class_Name"][1] == "Texture2D":
            PC(["Export", _CURR_EXPORT_ID, "Texture2D"])
            PD("Null_Bytes", "*4")
            PD("Color_Range", "Int32")
            PD("Color_Mode", "Uint32")
            PD("Pixel_Format_Name_ID", "Uint64")
            PD("Skip_Offset", "Uint32")
            PD("Placeholder", "Uint32")
            _X = PD("SizeX", "Uint32")
            _Y = PD("SizeY", "Uint32")
            PD("Packed_Data", "Uint32")
            _PIXEL_F = PD("Pixel_Format", "String")
            _DXGI_F = AD("DXGI_Format", PF_TO_DXGI_MAP[_PIXEL_F])
            _BPP = AD("DXGI_Byte_Pre_Pixel", DXGI_TO_BPP_MAP[_DXGI_F])
            _DXGI_VALUE = AD("DXGI_Format_Value", DXGI_TO_VALUE_MAP[_DXGI_F])
            AD("Imported_Size", int(_X * _Y * _BPP))
            PD("First_Mip_To_Serialize", "Uint32")
            _COUNT = PD("Mip_Count", "Uint32")
            if _COUNT and ONE_MIP: _COUNT = 1
            PC([".", "Mips"], [])
            for _i_ in range(_COUNT):
                PC([".", "__INDEX__"])
                PD("bCooked", "Uint32")
                _BULK_FLAGS_VALUE = PD("Bulk_Flags_Value", "Uint32", _save=False)
                _BULK_FLAGS = []
                for _i_ in range(17):
                    if (_BULK_FLAGS_VALUE & (1 << _i_)) != 0:
                        if _i_ == 0:
                            _BULK_FLAGS.append("BULKDATA_PayloadAtEndOfFile")
                        elif _i_ == 3:
                            _BULK_FLAGS.append("BULKDATA_SingleUse")
                        elif _i_ == 6:
                            _BULK_FLAGS.append("BULKDATA_ForceInlinePayload")
                        elif _i_ == 8:
                            _BULK_FLAGS.append("BULKDATA_PayloadInSeperateFile")
                        elif _i_ == 10:
                            _BULK_FLAGS.append("BULKDATA_Force_NOT_InlinePayload")
                        elif _i_ == 16:
                            _BULK_FLAGS.append("BULKDATA_NoOffsetFixUp")
                AD("Bulk_Flags", _BULK_FLAGS)
                PD("Element_Count", "Int32")
                PD("Size", "Int32")
                PD("Offset", "Byte*5")
                PD("Split", "Byte*3")
                if "BULKDATA_ForceInlinePayload" in _BULK_FLAGS:
                    PD("Bytes", f"Byte*{CD("Size")}")
                PD("SizeX", "Uint32")
                PD("SizeY", "Uint32")
                PD("SizeZ", "Uint32")
                if "BULKDATA_ForceInlinePayload" in _BULK_FLAGS:
                    _FILES = PDDS(CD("SizeX"), CD("SizeY"), CD("Size"), _DXGI_VALUE, CD("Bytes"))
                    AD("Files", _FILES)
                PC([".."])
            PC([".."])
            
            if not _UBULK: break
            with open(_UBULK, "rb") as F:
                _UBULK_FILE = memoryview(F.read())
            _MIP_DATA = CD("Mips")
            for _x_ in range(_COUNT):
                if "BULKDATA_Force_NOT_InlinePayload" in _MIP_DATA[_x_]["Bulk_Flags"]:
                    _INT_OFFSET = int.from_bytes(_MIP_DATA[_x_]["Offset"], byteorder="little")
                    _MIP_DATA[_x_]["Bytes"] = struct.unpack_from(f"{_MIP_DATA[_x_]["Size"]}s", _UBULK_FILE, _INT_OFFSET)[0]
                    _MIP_DATA[_x_]["Files"] = PDDS(_MIP_DATA[_x_]["SizeX"], _MIP_DATA[_x_]["SizeY"], _MIP_DATA[_x_]["Size"], _DXGI_VALUE, _MIP_DATA[_x_]["Bytes"])
        
        # elif _CURR_EXPORT_DATA["Class_Name"][1] == "SpineAtlasAsset":
        #     pass
        
        # elif _CURR_EXPORT_DATA["Class_Name"][1] == "SpineSkeletonDataAsset":
        #     pass
    
    return UASSAT_PARSE["DATA"]

def PARSE_PROP():
    _NAME = PD("Name", "Name", _save=False)
    if _NAME[1] == "None":
        return
    _TYPE_INDEX = PD("Type_Index", _save=False)
    _TYPE = AD("Type", GET_NAMEMAP(_TYPE_INDEX), _save=False)
    PD("Proof", "*4")
    _SIZE = PD("Size", _save=False)
    PD("Duplicate_Index", _save=False)
    if _TYPE == "ArrayProperty":
        _VARIANT = PD("Variant", "Name", _save=False)
        PD("Split", "*1")
        VPROP(_TYPE, { "NAME": _NAME[3], "SIZE": _SIZE, "VARIANT": _VARIANT[1] })
    elif _TYPE == "StructProperty":
        _VARIANT = PD("Variant", "Name", _save=False)
        PD("Struct_Header", "*16")
        PD("Split", "*1")
        VPROP(_TYPE, { "NAME": _NAME[3], "SIZE": _SIZE, "VARIANT": _VARIANT[1] })
    elif _TYPE == "ByteProperty":
        _VARIANT = PD("Variant", "Name", _save=False)
        PD("Split", "*1")
        _VALUE = PROP(_TYPE, { "NAME": _NAME[3], "SIZE": _SIZE, "VARIANT": _VARIANT[1] })
        AD(_NAME[3], _VALUE)
    elif _TYPE == "BoolProperty":
        _BOOL = PD("Bool", "Bool", _save=False)
        PD("Split", "*1")
        AD(_NAME[3], _BOOL)
    elif _TYPE == "MapProperty":
        _VARIANT_KEY = PD("Variant_Key", "Name", _save=False)
        _VARIANT_VALUE = PD("Variant_Value", "Name", _save=False)
        PD("Map_Config", "*4")
        PD("Split", "*1")
        VPROP(_TYPE, { "NAME": _NAME[3], "VARIANT_KEY": _VARIANT_KEY[1], "VARIANT_VALUE": _VARIANT_VALUE[1] })
    elif _TYPE == "EnumProperty":
        PD("Enum_Type", "Name", _save=False)
        PD("Split", "*1")
        _VALUE = PROP(_TYPE)
        AD(_NAME[3], _VALUE)
    else:
        PD("Split", "*1")
        _VALUE = PROP(_TYPE)
        AD(_NAME[3], _VALUE)
    PRINT(f"{_TAB(len(UASSAT_PARSE["CURR_CLASS"]))}================= ({UASSAT_PARSE["OFFSET"]})")
    return True

def PROP(_Type, _PARAM=None):
    if _Type == "IntProperty":
        return PD("Value", _save=False)
    elif _Type == "Int16Property":
        return PD("Value", "h", _save=False)
    elif _Type == "UInt32Property":
        return PD("Value", "I", _save=False)
    elif _Type == "FloatProperty":
        return PD("Value", "Float", _save=False)
    elif _Type == "StrProperty":
        return PD("Value", "String", _save=False)
    elif _Type == "NameProperty":
        return PD("Value", "Name", _save=False)[3]
    elif _Type[:12] == "ByteProperty":
        if len(_Type) > 12:
            if int(_Type[13:]) == 1:
                return PD("Value", "Int8", _save=False)
        elif _PARAM["SIZE"] == 8: #  in [None, "ETraceTypeQuery", "ECollisionChannel"]
            return PD("Value", "Name", _save=False)[3]
        elif _PARAM["SIZE"] == 1:
            return PD("Value", "Int8", _save=False)
        else:
            return PD("Value", f"Byte*{_PARAM["SIZE"]}", _save=False)
    elif _Type == "ObjectProperty":
        _VALUE_INDEX = PD("Value_Index", _save=False)
        if _VALUE_INDEX:
            if _VALUE_INDEX < 0:
                _CACHE = UASSAT_PARSE["DATA"]["Import_Map"][_VALUE_INDEX]
                _OBJECT_NAME = f"{_CACHE["Class_Name"][3]}'{_CACHE["Object_Name"][3]}'"
                _CACHE = UASSAT_PARSE["DATA"]["Import_Map"][_CACHE["Outer_Index"]]
                _OBJECT_PATH = _CACHE["Object_Name"][3]
                return { "ObjectName": _OBJECT_NAME, "ObjectPath": _OBJECT_PATH }
            elif _VALUE_INDEX > 0:
                _CACHE = UASSAT_PARSE["DATA"]["Export_Map"][_VALUE_INDEX]
                _OBJECT_NAME = f"{_CACHE["Class_Name"][3]}'{_CACHE["Template_Name"][3]}:{_CACHE["Name"][3]}'"
                _CACHE = UASSAT_PARSE["DATA"]["Export_Map"][_CACHE["Outer_Index"]]
                _OBJECT_PATH = _CACHE["Name"][3]
                return { "ObjectName": _OBJECT_NAME, "ObjectPath": _OBJECT_PATH }
        else:
            return None
    elif _Type == "EnumProperty":
        return PD("Enum", "Name", _save=False)[3]
    elif _Type == "Guid":
        return uuid.UUID(bytes=PD("Guid", "Byte*16", _save=False))

def VPROP(_TYPE, _PARAM=None):
    if _TYPE == "StructProperty":
        if _PARAM["SIZE"] == 0:
            if not UASSAT_PARSE["SIMPLIFY"]:
                AD(_PARAM["NAME"], {})
            return
        if _PARAM["VARIANT"] == "GameplayTagContainer":
            if UASSAT_PARSE["CURR_CLASS_TYPE"] == dict:
                PC([".", _PARAM["NAME"]])
            else:
                PC([".", "__INDEX__"])
            _COUNT = PD("Count", _save=False)
            for _ in range(_COUNT):
                PROP("NameProperty")
            PC([".."])
        elif _PARAM["VARIANT"] == "MovieSceneEvaluationFieldEntityTree":
            PD("Flag", f"Byte*{_PARAM["SIZE"]}", _save=False)
        elif _PARAM["VARIANT"] == "MovieSceneFloatChannel":

            PC([".", _PARAM["NAME"]])

            PD("Flag", "Byte*6")

            _TIMES_COUNT = PD("Times_Count", _save=False)
            PC([".", "Times"], [])
            for _i_ in range(_TIMES_COUNT):
                PC([".", "__INDEX__"])
                PD("Value")
                PC([".."])
            PC([".."])

            PD("Flag2", "Byte*4")

            _VALUES_COUNT = PD("Values_Count", _save=False)
            PC([".", "Values"], [])
            for _i_ in range(_TIMES_COUNT):
                PC([".", "__INDEX__"])
                PD("Value", "f")
                PC([".", "Tangent"])
                PD("ArriveTangent", "f")
                PD("LeaveTangent", "f")
                PD("ArriveTangentWeight", "f")
                PD("LeaveTangentWeight", "f")
                PD("TangentWeightMode", "f")
                PC([".."])
                PD("InterpMode", "b")
                PD("TangentMode", "b")
                PD("PaddingByte", "Byte*2")
                PC([".."])
            PC([".."])

            PD("DefaultValue", "f")
            PD("Flag3", "Byte*4")

            PC([".", "TickResolution"])
            PD("Numerator")
            PD("Denominator")
            PC([".."])

            PC([".."])

        elif _PARAM["VARIANT"] in STRUCT_PROPERTY_VARIANT_RULE.keys():
            _DATA = {}
            for _STRUCT_NAME, _STRUCT_TYPE in STRUCT_PROPERTY_VARIANT_RULE[_PARAM["VARIANT"]].items():
                _DATA[_STRUCT_NAME] = PROP(_STRUCT_TYPE)
            if not UASSAT_PARSE["SIMPLIFY"]:
                AD(_PARAM["NAME"], _DATA)
            else:
                if _DATA not in [
                    { "X": 0.0, "Y": 0.0 },
                    { "X": 0.0, "Y": 0.0, "Z": 0.0 },
                    { "X": 0.0, "Y": 0.0, "Z": 0.0, "W": 1.0 },
                    { "Pitch":0.0, "Yaw":0.0, "Roll":0.0 },
                    { "AssetPathName": "None", "SubPathString": None },
                    { "TagName": "None" },
                ]:
                    AD(_PARAM["NAME"], _DATA)
        else:
            if UASSAT_PARSE["CURR_CLASS_TYPE"] == dict:
                PC([".", _PARAM["NAME"]])
            else:
                PC([".", "__INDEX__"])
            _END_OFFSET = UASSAT_PARSE["OFFSET"] + _PARAM["SIZE"]
            while PARSE_PROP():
                if not UASSAT_PARSE["OFFSET"] < _END_OFFSET:
                    break
            PC([".."])

    elif _TYPE == "ArrayProperty":
        _COUNT = PD("Array_Count", _save=False)
        if _PARAM["SIZE"] == 4:
            if not UASSAT_PARSE["SIMPLIFY"]:
                AD(_PARAM["NAME"], [])
            return
        if _PARAM["VARIANT"] == "StructProperty":
            
            _NAME = PD("Name", "Name", _save=False)
            if _NAME[1] == "None":
                if not UASSAT_PARSE["SIMPLIFY"]:
                    AD(_PARAM["NAME"], [])
                return
            _TYPE_INDEX = PD("Type_Index", _save=False)
            _TYPE = AD("Type", GET_NAMEMAP(_TYPE_INDEX), _save=False)
            PD("Proof", "*4")
            _SIZE = PD("Size", _save=False)
            PD("Duplicate_Index", _save=False)
            _VARIANT = PD("Variant", "Name", _save=False)
            PD("Struct_Header", "*16")
            PD("Split", "*1")
            PRINT(_TAB(len(UASSAT_PARSE["CURR_CLASS"]))+"=================")
            _STRUCT_PARAM = { "NAME": _NAME[3], "SIZE": _SIZE, "VARIANT": _VARIANT[1] }

            if _STRUCT_PARAM["SIZE"] == 0:
                if not UASSAT_PARSE["SIMPLIFY"]:
                    AD(_PARAM["NAME"], [])
                return
            PC([".", _PARAM["NAME"]], _type=[])
            for _ in range(_COUNT):
                VPROP("StructProperty", _STRUCT_PARAM)
            PC([".."])
        else:
            if _PARAM["NAME"] in ["rawData"]:
                _DATA = PD("rawData", f"Byte*{_PARAM["SIZE"]-4}", _save=False)
            else:
                _DATA = []
                for _ in range(_COUNT):
                    _DATA.append(PROP(_PARAM["VARIANT"], _PARAM={ "SIZE": 8 }))
            AD(_PARAM["NAME"], _data=_DATA)
        

    elif _TYPE == "MapProperty":
        _COUNT = PD("Map_Count", _save=False)
        _MAP_P = { "Key": _PARAM["VARIANT_KEY"], "Value": _PARAM["VARIANT_VALUE"]}
        _MAP_DATA = []
        for _ in range(_COUNT):
            _ONE_DATA = {}
            for _CURR_TYPE, _CURR_VARI in _MAP_P.items():
                if _CURR_VARI in ["StructProperty", "SoftObjectProperty"]:
                    if _PARAM["NAME"] in ["RandomKeepTime"]:
                        _VALUE_0 = PD(f"Min", "f", _save=False)
                        _VALUE_1 = PD(f"Max", "f", _save=False)
                        _ONE_DATA[_CURR_TYPE] = {
                            "Min": _VALUE_0,
                            "Max": _VALUE_1
                            }
                    else:
                        _VALUE_0 = PD(f"AssetPathName", "Name", _save=False)[3]
                        _VALUE_1 = PD(f"SubPathString", "String", _save=False)
                        _ONE_DATA[_CURR_TYPE] = {
                            "AssetPathName": _VALUE_0,
                            "SubPathString": _VALUE_1
                            }
                else:
                    _ONE_DATA[_CURR_TYPE] = PROP(_CURR_VARI)
            _MAP_DATA.append(_ONE_DATA)
        AD(_PARAM["NAME"], _MAP_DATA)

def GET_NAMEMAP(_index):
    if type(_index) == str:
        _index = CD(_index)
    _name = UASSAT_PARSE["DATA"]["Name_Map"][_index]["Name"]
    return _name

def GET_IENAME(_index):
    if type(_index) == str:
        _index = CD(_index)
    if _index == 0:
        _name = None
    elif _index > 0:
        _name = UASSAT_PARSE["DATA"]["Export_Map"][_index]["Name"]
    elif _index < 0:
        _name = UASSAT_PARSE["DATA"]["Import_Map"][_index]["Object_Name"]
    return _name

" / / PARSE FIELD / / "
def P(_type="Int32"):

    _type = _type.split("*")

    if _type[0] in ["Null", ""]:
        if not len(_type) > 1: _type.append(1)
        _data = None
        UASSAT_PARSE["OFFSET"] += int(_type[1])

    elif _type[0] in ["Name"]:
        _NAME_INDEX = P()
        _NAME_ID = P()
        _NAME = GET_NAMEMAP(_NAME_INDEX)
        if _NAME_ID == 0:
            _NAME_ITEM = _NAME
        else:
            _NAME_ITEM = f"{_NAME}_{_NAME_ID-1}"
        _data = [_NAME_INDEX, _NAME, _NAME_ID, _NAME_ITEM]

    elif _type[0] in ["NameIndex"]:
        _NAME_INDEX = P()
        _NAME = GET_NAMEMAP(_NAME_INDEX)
        _data = [_NAME_INDEX, _NAME,]

    elif _type[0] in ["b", "Int8"]:
        _data = struct.unpack_from("b", UASSAT_PARSE["FILE"], UASSAT_PARSE["OFFSET"])[0]
        UASSAT_PARSE["OFFSET"] += 1
        
    elif _type[0] in ["B", "Uint8"]:
        _data = struct.unpack_from("B", UASSAT_PARSE["FILE"], UASSAT_PARSE["OFFSET"])[0]
        UASSAT_PARSE["OFFSET"] += 1

    elif _type[0] in ["h", "Int16"]:
        _data = struct.unpack_from("h", UASSAT_PARSE["FILE"], UASSAT_PARSE["OFFSET"])[0]
        UASSAT_PARSE["OFFSET"] += 2
        
    elif _type[0] in ["H", "Uint16"]:
        _data = struct.unpack_from("H", UASSAT_PARSE["FILE"], UASSAT_PARSE["OFFSET"])[0]
        UASSAT_PARSE["OFFSET"] += 2
    
    elif _type[0] in ["i", "Int32"]:
        _data = struct.unpack_from("i", UASSAT_PARSE["FILE"], UASSAT_PARSE["OFFSET"])[0]
        UASSAT_PARSE["OFFSET"] += 4
        
    elif _type[0] in ["I", "Uint32"]:
        _data = struct.unpack_from("I", UASSAT_PARSE["FILE"], UASSAT_PARSE["OFFSET"])[0]
        UASSAT_PARSE["OFFSET"] += 4
        
    elif _type[0] in ["q", "Int64"]:
        _data = struct.unpack_from("q", UASSAT_PARSE["FILE"], UASSAT_PARSE["OFFSET"])[0]
        UASSAT_PARSE["OFFSET"] += 8
        
    elif _type[0] in ["Q", "Uint64"]:
        _data = struct.unpack_from("Q", UASSAT_PARSE["FILE"], UASSAT_PARSE["OFFSET"])[0]
        UASSAT_PARSE["OFFSET"] += 8
        
    elif _type[0] in ["f", "Float"]:
        _data = struct.unpack_from("f", UASSAT_PARSE["FILE"], UASSAT_PARSE["OFFSET"])[0]
        _data = format_float(_data)
        UASSAT_PARSE["OFFSET"] += 4

    elif _type[0] in ["Int32Array"]:
        _data = []
        for _ in range(int(_type[1])):
            _data.append(P())
        
    elif _type[0] in ["?", "Bool"]:
        _data = struct.unpack_from("?", UASSAT_PARSE["FILE"], UASSAT_PARSE["OFFSET"])[0]
        UASSAT_PARSE["OFFSET"] += 1

    elif _type[0] in ["Byte"]:
        if not len(_type) > 1: _type.append(1)
        _data = struct.unpack_from(f"{_type[1]}s", UASSAT_PARSE["FILE"], UASSAT_PARSE["OFFSET"])[0]
        UASSAT_PARSE["OFFSET"] += int(_type[1])

    elif _type[0] in ["str", "String"]:
        _str_size = P()
        if _str_size != 0:
            if _str_size > 0:
                _data = struct.unpack_from(f"{_str_size-1}s", UASSAT_PARSE["FILE"], UASSAT_PARSE["OFFSET"])[0].decode('ascii')
                UASSAT_PARSE["OFFSET"] += _str_size
            elif _str_size < 0:
                _data = struct.unpack_from(f"{(-_str_size-1)*2}s", UASSAT_PARSE["FILE"], UASSAT_PARSE["OFFSET"])[0].decode('utf-16')
                UASSAT_PARSE["OFFSET"] += (-_str_size)*2
        else:
            _data = None
    
    return _data

" / / PARSE DATA TO CURR CLASS / / "
def PC(_class, _type=dict, _custom=None):
    " 创建存放数据的字典 "
    if _type == dict:
        _type = {}
    
    " 如果存在自定义列表则使用自定义 "
    if not _custom:
        _CURR_CLASS = "CURR_CLASS"
        _CURR_CLASS_TYPE = "CURR_CLASS_TYPE"
        _CURR_DATA_POS = "CURR_DATA_POS"
    else:
        _CURR_CLASS = f"CURR_CLASS_{_custom}"
        _CURR_CLASS_TYPE = f"CURR_CLASS_TYPE_{_custom}"
        _CURR_DATA_POS = f"CURR_DATA_POS_{_custom}"

    " 设定相对的字典列表 "
    if _class[0] in [".", ".."]:
        _NEW_CLASS = list(UASSAT_PARSE["CURR_CLASS"])
        for _x_ in _class:
            if _x_ == ".":
                pass
            elif _x_ == "..":
                _NEW_CLASS = _NEW_CLASS[:-1]
            else:
                _NEW_CLASS.append(_x_)
        _class = _NEW_CLASS

    " 检测从第几个位置更改列表 "
    _CHANGE = False
    _CURR_INDEX = len(_class) - 1
    for _x_, _y_ in enumerate(_class):
        if not _CHANGE:
            if _x_ < len(UASSAT_PARSE.get(_CURR_CLASS, [])): # _class 列表在之前的范围
                if _y_ != UASSAT_PARSE[_CURR_CLASS][_x_]: # _class 里的值不相同
                    _CHANGE = True
            else: # _class 列表超出之前的范围
                _CHANGE = True

        " 如果存在更改则重新设定列表"
        if _CHANGE:
            if _x_ == 0:
                if not UASSAT_PARSE["DATA"].get(_y_):
                    UASSAT_PARSE["DATA"][_y_] = {}
                if not UASSAT_PARSE.get(_CURR_DATA_POS):
                    UASSAT_PARSE[_CURR_DATA_POS] = []
                if _x_ == len(UASSAT_PARSE[_CURR_DATA_POS]):
                    UASSAT_PARSE[_CURR_DATA_POS].append(UASSAT_PARSE["DATA"][_y_])
                else:
                    UASSAT_PARSE[_CURR_DATA_POS][0] = UASSAT_PARSE["DATA"][_y_]
            elif _x_ != _CURR_INDEX:
                if isinstance(UASSAT_PARSE[_CURR_DATA_POS][_x_-1], dict):
                    if not UASSAT_PARSE[_CURR_DATA_POS][_x_-1].get(_y_):
                        UASSAT_PARSE[_CURR_DATA_POS][_x_-1][_y_] = {}
                #elif isinstance(UASSAT_PARSE[_CURR_DATA_POS][_x_-1], list):
                    #if len(UASSAT_PARSE[_CURR_DATA_POS][_x_-1]) > _y_:
                    #    print(" 序列超出范围 ")
                if _x_ == len(UASSAT_PARSE[_CURR_DATA_POS]):
                    UASSAT_PARSE[_CURR_DATA_POS].append(UASSAT_PARSE[_CURR_DATA_POS][_x_-1][_y_])
                else:
                    UASSAT_PARSE[_CURR_DATA_POS][_x_] = UASSAT_PARSE[_CURR_DATA_POS][_x_-1][_y_]
            else:
                if isinstance(UASSAT_PARSE[_CURR_DATA_POS][_x_-1], dict):
                    if not UASSAT_PARSE[_CURR_DATA_POS][_x_-1].get(_y_):
                        UASSAT_PARSE[_CURR_DATA_POS][_x_-1][_y_] = _type
                elif isinstance(UASSAT_PARSE[_CURR_DATA_POS][_x_-1], list):
                    if _y_ == "__INDEX__":
                        _y_ = len(UASSAT_PARSE[_CURR_DATA_POS][_x_-1])
                        _class[-1] = _y_
                        UASSAT_PARSE[_CURR_DATA_POS][_x_-1].append(_type)
                    #if len(UASSAT_PARSE[_CURR_DATA_POS][_x_-1]) > _y_:
                    #    print(" 序列超出范围 ")
                if _x_ == len(UASSAT_PARSE[_CURR_DATA_POS]):
                    UASSAT_PARSE[_CURR_DATA_POS].append(UASSAT_PARSE[_CURR_DATA_POS][_x_-1][_y_])
                else:
                    UASSAT_PARSE[_CURR_DATA_POS][_x_] = UASSAT_PARSE[_CURR_DATA_POS][_x_-1][_y_]
            PRINT(f"{_TAB(_x_)}{_y_} ({UASSAT_PARSE["OFFSET"]})", _custom=_custom)
                # if not isinstance(UASSAT_PARSE[_CURR_DATA_POS][_x_], _type):
                #     print(" 类型不匹配 ")
    UASSAT_PARSE[_CURR_CLASS] = _class
    UASSAT_PARSE[_CURR_DATA_POS][_x_+1:] = []
    if isinstance(UASSAT_PARSE[_CURR_DATA_POS][-1], dict):
        UASSAT_PARSE[_CURR_CLASS_TYPE] = dict
    else:
        UASSAT_PARSE[_CURR_CLASS_TYPE] = list

" / / CURR DATA / / "
def CD(_Name=None):
    if _Name == None:
        return UASSAT_PARSE["CURR_DATA_POS"][-1]
    else:
        return UASSAT_PARSE["CURR_DATA_POS"][-1].get(_Name, "__CURR_DATA_POS_NONE__")

" / / PARSE DATA / / "
def PD(_name=None, _type="Int32", _save=True):
    _data = P(_type)
    if _save and _data != None:
        if UASSAT_PARSE["CURR_CLASS_TYPE"] == dict:
            UASSAT_PARSE["CURR_DATA_POS"][-1][_name] = _data
        else:
            UASSAT_PARSE["CURR_DATA_POS"][-1].append(_data)
    if (_save and _type[0] != "*") or _RE_SAVE:
        PRINT(_data, _name, _type, True)
    return _data

" / / ADD DATA / / "
def AD(_name=None, _data=None, _save=True):
    if _save and (
        not UASSAT_PARSE["SIMPLIFY"] or _data not in [None, False]): # , 0
        if UASSAT_PARSE["CURR_CLASS_TYPE"] == dict:
            UASSAT_PARSE["CURR_DATA_POS"][-1][_name] = _data
        else:
            _name = ""
            UASSAT_PARSE["CURR_DATA_POS"][-1].append(_data)
    if _save or _RE_SAVE:
        PRINT(_data, _name, _type="Add", _auto_match=True)
    return _data

def PDDS(_X, _Y, _SIZE, _DXGI_VALUE, _BYTES):

    DDS_DATA_CACHE = (
        b'DDS '
        + struct.pack("I", 124)
        + struct.pack("I", 135183)
        + struct.pack("I", _Y)
        + struct.pack("I", _X)
        + struct.pack("I", _SIZE)
        + struct.pack("I", 1)
        + struct.pack("I", 1)
        + struct.pack("I", 0) * 9
        + b'UEDT'
        + struct.pack("I", 0)
        + struct.pack("I", 32)
        + struct.pack("I", 4)
        + b'DX10'
        + struct.pack("I", 0)
        + struct.pack("I", 0) * 4
        + struct.pack("I", 4096)
        + struct.pack("I", 0)
        + struct.pack("I", 0) * 3
        + struct.pack("I", _DXGI_VALUE)
        + struct.pack("Q", 3)
        + struct.pack("Q", 1)
        + _BYTES # P(f"Byte*{CD()["Imported_Size"]}")
        )
    # AWF("test/_cache.dds", DDS_DATA_CACHE, as_bytes=True)
    with Image() as img:
        _BytesIO_CACHE = io.BytesIO(DDS_DATA_CACHE)
        img.read(_BytesIO_CACHE)
        # img.alpha_channel = 'activate'
        img.evaluate(operator='multiply', value=1.0)
        img.format = 'png'
        _BytesIO_CACHE_SAVE = io.BytesIO()
        img.save(_BytesIO_CACHE_SAVE)
        _BytesIO_CACHE_SAVE.seek(0)
    return _BytesIO_CACHE_SAVE

" / / IF PRINT / / "
def PRINT(_data, _name=None, _type="None", _auto_match=False, _custom=None):
    if IS_PRINT and (_custom==None): #"EXPORT"
        _str = ""
        if _auto_match == True:
            _str += _TAB(len(UASSAT_PARSE["CURR_CLASS"]))
            if _type and IS_PRINT_TYPE:
                _str += f"({_type}) "
            if _name:
                _str += f"{_name}: "

            if _type.split("*")[0] in ["Byte"]:
                _str += ' '.join(f'{_d:02X}' for _d in _data)
            elif _type.split("*")[0] in ["" ,"Null"]:
                if not len(_type.split("*")) > 1:
                    _str += "XX"
                else:
                    _str += " ".join(["XX"] * int(_type.split("*")[1]))
            elif "flag" in _name.lower() and isinstance(_data, int):
                _str += "0B " + bin(_data)[2:]
            else:
                _str += str(_data)
        else:
            _str += _data

        if len(_str) > 200:
            print(_str[:200]+"...")
        else:
            print(_str)
    return

def _TAB(_tab_num):
    if not isinstance(_tab_num, int):
        _tab_num = len(_tab_num)
    if _tab_num <= 4:
        _tab = "   " * _tab_num
    else:
        _tab = "   " * 4
        for _x_ in range(_tab_num-4):
            if (_x_ % 2 != 0) or True:
                _tab += "|  "
            else:
                _tab += "   "
        #if (_tab_num-6) % 2 == 0:
        #    _tab = _tab[:-1] + "-"
    return _tab

def format_float(value):
    value = round(value, 6)
    F_CACHE = f"{value:.16f}".split(".")
    if value >= 1:
        for _i_ in range(0, len(F_CACHE[0])-3-7):
            if F_CACHE[0][_i_:_i_+4] == "9999":
                return round(value, -len(F_CACHE[0])+_i_)
            elif F_CACHE[0][_i_:_i_+4] == "0000":
                return round(value, -len(F_CACHE[0])+_i_)
        for _i_ in range(2, len(F_CACHE[1])-3):
            if F_CACHE[1][_i_:_i_+2] == "99":
                return round(value, _i_)
            elif F_CACHE[1][_i_:_i_+2] == "00":
                return round(value, _i_)
    elif value < 1:
        _MAK = False
        for _i_ in range(2, len(F_CACHE[1])-1):
            if F_CACHE[1][_i_:_i_+2] == "99":
                return round(value, _i_)
            elif F_CACHE[1][_i_:_i_+2] == "00" and _MAK:
                return round(value, _i_)
            if _i_ != 0:
                _MAK = True
    return value