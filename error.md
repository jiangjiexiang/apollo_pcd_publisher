# Apollo 6.0 使用 Python 运行 Cyber RT 节点 ImportError 解决方案

## 1. 问题现象

在 Apollo 6.0 的 Docker 环境里运行 Python 脚本，例如：

```bash
cd /apollo
python3 pcd_publisher.py
```

报错示例：

```text
ImportError: cannot import name 'pointcloud_pb2'
ImportError: cannot import name 'header_pb2'
ImportError: cannot import name 'error_code_pb2'
```

---

## 2. 原因分析

- Apollo 的 proto 文件有依赖关系：  
  `pointcloud.proto → header.proto → error_code.proto`
- 如果下游依赖没有编译成 Python 文件（xxx_pb2.py），就会报错。
- Apollo 默认用 Bazel 构建，生成的 Python 文件路径正确，但 Python 解释器的 `sys.path` 没有包含 `/apollo`，导致无法找到。
- 直接用 `python3 xxx.py` 运行时，Apollo 的包导入规则不会自动生效，所以 import 失败。

---

## 3. 解决方法

### 方法 1：全量编译 proto（推荐）

进入 Apollo 容器，执行：

```bash
bash apollo.sh build
```

Bazel 会编译所有 .proto 文件，生成对应的 _pb2.py 文件。编译完成后，检查：

```bash
ls modules/drivers/proto/pointcloud_pb2.py
ls modules/common/proto/header_pb2.py
ls modules/common/proto/error_code_pb2.py
```

这些文件都应该存在。

---

### 方法 2：手动编译 proto 文件

如果只想生成 Python 文件，可以手动执行：

```bash
cd /apollo
protoc --python_out=. modules/common/proto/error_code.proto
protoc --python_out=. modules/common/proto/header.proto
protoc --python_out=. modules/drivers/proto/pointcloud.proto
```

这样会生成：

- modules/common/proto/error_code_pb2.py
- modules/common/proto/header_pb2.py
- modules/drivers/proto/pointcloud_pb2.py

---

### 方法 3：添加 Python 路径

即使生成了 _pb2.py，Python 依然可能报错，因为找不到包。  
解决方法是在运行前设置环境变量：

```bash
cd /apollo
export PYTHONPATH=/apollo:${PYTHONPATH}
python3 pcd_publisher.py
```

或者在脚本开头加：

```python
import sys
sys.path.append("/apollo")
```

这样 Python 就能正确找到 modules.xxx.proto 的依赖。

---

### 方法 4：使用 cyber_launch 启动

Apollo 推荐用 cyber_launch 启动 Python 节点，它会自动处理 Python 路径问题。  
写一个 .dag 配置文件，并用：

```bash
cyber_launch start your_launch.launch
```

这样导入问题就不会出现。

---

## 4. 总结推荐做法

1. 先全量编译

    ```bash
    bash apollo.sh build
    ```

2. 运行脚本时加 PYTHONPATH

    ```bash
    cd /apollo
    export PYTHONPATH=/apollo:${PYTHONPATH}
    python3 pcd_publisher.py
    ```

3. 如果还是缺 proto，就手动用 protoc 生成。

---

## 5. 常见坑点

- 必须在 `/apollo` 根目录下运行脚本，否则 `modules.xxx.proto` 的 import 会失败。
- 不要在 `modules/drivers/proto` 目录下运行脚本，这样 Python 会误以为 modules 不是包。
- 确保 _pb2.py 文件存在，如果缺少就用 protoc 手动生成。

---

这样整理下来，你随时可以参考，避免再踩坑 🚀