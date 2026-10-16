#!/bin/bash
set -e

# Ensure proper permissions on the volume directory
sudo mkdir -p /hadoop/dfs/data
sudo chown -R hadoop:users /hadoop
sudo chmod -R 755 /hadoop

echo "Starting Hadoop DataNode..."
hdfs datanode
