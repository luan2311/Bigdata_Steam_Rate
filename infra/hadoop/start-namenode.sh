#!/bin/bash
set -e

# Format NameNode if not already formatted
if [ ! -d "/hadoop/dfs/name/current" ]; then
    echo "Formatting Hadoop NameNode..."
    hdfs namenode -format -force -nonInteractive
fi

echo "Starting Hadoop NameNode..."
hdfs namenode
