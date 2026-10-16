#!/bin/bash
set -e

# Ensure proper permissions on the volume directory
sudo mkdir -p /hadoop/dfs/name
sudo chown -R hadoop:users /hadoop
sudo chmod -R 755 /hadoop

# Format NameNode if not already formatted
if [ ! -d "/hadoop/dfs/name/current" ]; then
    echo "Formatting Hadoop NameNode..."
    hdfs namenode -format -force -nonInteractive
fi

echo "Starting Hadoop NameNode..."
hdfs namenode
