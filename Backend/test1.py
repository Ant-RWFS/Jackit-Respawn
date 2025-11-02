import numpy as np

T=[0, 0xC1, 0, 0, 0, 0, 0, 0, 0, 0]

T_uint8 = np.array(T, dtype=np.uint8)    # 无符号8位整数
T_int16 = np.array(T, dtype=np.int16)    # 有符号16位整数
T_float = np.array(T, dtype=np.float32)  # 单精度浮点数

print(T)
print(f"uint8: {T_uint8}, dtype: {T_uint8.dtype}")
print(f"int16: {T_int16}, dtype: {T_int16.dtype}")
print(f"float32: {T_float}, dtype: {T_float.dtype}")