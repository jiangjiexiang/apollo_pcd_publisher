# pcd_publisher.py 调试记录文档

本文记录了在 Apollo 6.0 中使用 Cyber RT 发布点云 (`pcd_publisher.py`) 时遇到的问题及解决方法。

---

## 1. 问题：`intensity` 类型错误

### 报错信息
```
TypeError: 180.39413561513754 has type float, but expected one of: int, long
```

### 原因分析
- `pointcloud_pb2.PointXYZIT` 中的 `intensity` 字段要求 **整型 (int32)**。
- 程序中使用了 `random.uniform(0, 255)`，返回的是浮点数。

### 解决方法
将 `float` 转换为 `int`：
```python
pt.intensity = int(random.uniform(0, 255))
```

---

## 2. 问题：`cyber_time.sleep` 不存在

### 报错信息
```
AttributeError: module 'cyber.python.cyber_py3.cyber_time' has no attribute 'sleep'
```

### 原因分析
- `cyber_time` 模块没有 `sleep` 方法。
- 应使用 Python 标准库 `time.sleep`。

### 解决方法
```python
import time

time.sleep(0.1)  # 替代 cyber_time.sleep
```

---

## 3. 问题：`open3d` 库缺失

### 报错信息
```
ModuleNotFoundError: No module named 'open3d'
```

### 原因分析
- `open3d` 并非 Apollo 默认环境自带库。
- 由于需求只是 **读取 PCD 并发布**，无需依赖 `open3d`。

### 解决方法
- 移除 `open3d`，改用 **原生 PCD 文件解析（ASCII/binary）**。

---

## 4. 问题：读取 PCD 文件时编码错误

### 报错信息
```
UnicodeDecodeError: 'ascii' codec can't decode byte 0xc8 in position 253
```

### 原因分析
- 脚本用 `open(file, 'r')` 方式打开 PCD 文件，默认编码为 ASCII。
- 但 PCD 文件可能是 **UTF-8 ASCII** 或 **binary** 格式。

### 解决方法
1. 如果是 ASCII PCD：  
   ```python
   with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
       lines = f.readlines()
   ```
2. 如果是 binary PCD：  
   - 改用二进制模式 `open(file, 'rb')`，并用 `struct.unpack` 解析。

---

## 5. 修改 Channel 名称

### 需求
- 默认程序发布到：
  ```
  /apollo/sensor/lidar128/PointCloud2
  ```
- 需要改为 MID360 标准话题：
  ```
  /apollo/sensor/mid360/PointCloud
  ```

### 解决方法
在 `create_writer` 时修改：
```python
writer = node.create_writer("/apollo/sensor/mid360/PointCloud",
                            pointcloud_pb2.PointCloud)
```

---

## 总结

- **强制 int** → 解决 `intensity` 类型错误  
- **使用 `time.sleep`** → 替代 `cyber_time.sleep`  
- **去掉 open3d** → 避免库缺失  
- **支持 ASCII/binary PCD** → 避免编码错误  
- **修改 Writer Channel** → 对接 MID360 标准  

这样 `pcd_publisher.py` 就能稳定运行，并正确向 Apollo Channel 发布点云。
