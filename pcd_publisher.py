#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cyber.python.cyber_py3 import cyber, cyber_time
from modules.drivers.proto import pointcloud_pb2
import struct
import time

PCD_FILE = "/apollo/scans.pcd"  # 替换为实际的 PCD 文件路径

def read_pcd(file_path):
    """通用 PCD 读取器，支持 ASCII 和 binary"""
    points = []
    with open(file_path, 'rb') as f:
        lines = []
        while True:
            line = f.readline()
            if not line:
                break
            lines.append(line)
            if line.startswith(b'DATA'):
                data_line = line
                break

        # 解析 header
        header_lines = [l.decode('utf-8', errors='ignore').strip() for l in lines]
        for l in header_lines:
            if l.startswith('WIDTH'):
                width = int(l.split()[1])
            elif l.startswith('HEIGHT'):
                height = int(l.split()[1])
            elif l.startswith('POINTS'):
                points_num = int(l.split()[1])
            elif l.startswith('TYPE'):
                types = l.split()[1:]  # e.g., F F F
            elif l.startswith('SIZE'):
                sizes = list(map(int, l.split()[1:]))
            elif l.startswith('COUNT'):
                counts = list(map(int, l.split()[1:]))

        # 判断 DATA 类型
        if data_line.strip() == b'DATA ascii':
            # ASCII 读取
            for line in f:
                vals = line.decode('utf-8', errors='ignore').strip().split()
                if len(vals) >= 3:
                    x, y, z = map(float, vals[:3])
                    points.append((x, y, z))
        else:
            # binary 或 binary_compressed，按 step 解析
            point_step = sum(s*c for s,c in zip(sizes, counts))
            for _ in range(points_num):
                data = f.read(point_step)
                if not data:
                    break
                # 假设前 3 个字段是 float x, y, z
                x, y, z = struct.unpack('fff', data[:12])
                points.append((x, y, z))
    return points

def publish_pcd(file_path):
    points = read_pcd(file_path)
    print("Loaded {} points from PCD".format(len(points)))

    cyber.init()
    node = cyber.Node("pcd_publisher")
    writer = node.create_writer("/apollo/sensor/mid360/PointCloud",
                                pointcloud_pb2.PointCloud)

    seq = 0
    while not cyber.is_shutdown():
        msg = pointcloud_pb2.PointCloud()
        msg.header.timestamp_sec = cyber_time.Time.now().to_sec()
        msg.header.sequence_num = seq
        msg.header.module_name = "pcd_publisher"
        msg.measurement_time = cyber_time.Time.now().to_sec()
        msg.width = len(points)
        msg.height = 1
        msg.is_dense = True

        for pt_xyz in points:
            pt = msg.point.add()
            pt.x, pt.y, pt.z = pt_xyz
            pt.intensity = 100

        writer.write(msg)
        print("Published point cloud, seq:", seq)
        seq += 1
        time.sleep(0.1)  # 10Hz

    cyber.shutdown()

if __name__ == "__main__":
    publish_pcd(PCD_FILE)
