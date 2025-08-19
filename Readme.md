# README - pcd_publisher.py

## 📌 脚本功能

`pcd_publisher.py` 是一个用于 **将本地 PCD 点云文件发布到 Apollo Cyber RT Channel** 的工具脚本。  

- 脚本读取本地的 `.pcd` 文件（ASCII 或 Binary 格式）。  
- 将点云数据转换为 Apollo 的 **`PointCloud`** 消息（`modules/drivers/proto/pointcloud.proto`）。  
- 发布到指定的 Cyber RT Channel，例如：
  ```
  /apollo/sensor/mid360/PointCloud
  ```
- Apollo 的 **Cyber Visualizer** 或其他订阅节点即可实时显示/消费点云数据。  

最初设计该脚本的目的：  
👉 在没有真实传感器的情况下，用离线 PCD 数据模拟雷达点云输入，方便进行 **算法调试、可视化验证**。

---

## ⚙️ 环境依赖

1. Apollo 6.0 (Cyber RT 框架)
2. Python 3.6+
3. 已编译的 `pointcloud_pb2.py`  
   - 由 `modules/drivers/proto/pointcloud.proto` 生成。
4. PCD 文件（ASCII 或 Binary）

不需要额外的 `open3d` 等第三方库。

---

## 🚀 使用方法

1. 进入 Apollo 容器：
   ```bash
   bash docker/scripts/dev_into.sh
   ```

2. 设置 `PYTHONPATH`：
   ```bash
   cd /apollo
   export PYTHONPATH=/apollo:${PYTHONPATH}
   ```

3. 编辑脚本，指定 PCD 文件路径，例如：
   ```python
   pcd_file = "/apollo/data/pcd/sample.pcd"
   publish_pcd(pcd_file)
   ```

4. 运行脚本：
   ```bash
   python3 pcd_publisher.py
   ```

5. 在 Cyber Visualizer 中订阅对应 Channel：
   ```
   /apollo/sensor/mid360/PointCloud
   ```
   即可看到点云数据。

---

## 🛠 常见问题

- **intensity 类型错误** → 确保强制转换为 `int`。  
- **`cyber_time.sleep` 报错** → 使用标准库 `time.sleep`。  
- **PCD 文件编码错误** → 指定 `encoding='utf-8', errors='ignore'` 或使用 `rb` 方式。  
- **Channel 不匹配** → 确认脚本发布 Channel 与 Cyber Visualizer 订阅的一致。  

---

## 📖 扩展

该脚本可以作为基础工具扩展，例如：  
- 播放 PCD 序列文件，模拟实时点云。  
- 将点云按频率循环发布，模拟传感器流。  
- 与 Apollo 感知模块对接，验证感知算法效果。  
