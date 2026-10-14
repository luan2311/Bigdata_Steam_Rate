"""SparkSession factory for local mode and, later, the cluster from infra/."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass

from pyspark.sql import SparkSession


@dataclass(frozen=True)
class SparkSettings:
    master: str = "local[*]"
    app_name: str = "steam-reviews"
    driver_memory: str = "4g"
    shuffle_partitions: int = 16
    extra: tuple[tuple[str, str], ...] = ()


def _prepare_windows_hadoop() -> None:
    """Spark on Windows needs winutils.exe/hadoop.dll from HADOOP_HOME\\bin on PATH."""
    if os.name != "nt":
        return
    hadoop_home = os.environ.get("HADOOP_HOME")
    if not hadoop_home:
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                hadoop_home, _ = winreg.QueryValueEx(key, "HADOOP_HOME")
                os.environ["HADOOP_HOME"] = hadoop_home
        except Exception:
            pass

    if not hadoop_home:
        import warnings
        warnings.warn(
            "Biến môi trường HADOOP_HOME chưa được thiết lập trên Windows. "
            "Một số tác vụ lưu Parquet cục bộ có thể cần winutils.exe/hadoop.dll.",
            UserWarning,
            stacklevel=2,
        )
        return

    hadoop_bin = os.path.join(hadoop_home, "bin")
    if os.path.exists(hadoop_bin) and hadoop_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = hadoop_bin + os.pathsep + os.environ.get("PATH", "")


def create_spark(settings: SparkSettings) -> SparkSession:
    _prepare_windows_hadoop()
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)
    builder = (
        SparkSession.builder.master(settings.master)
        .appName(settings.app_name)
        .config("spark.driver.memory", settings.driver_memory)
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", str(settings.shuffle_partitions))
        .config("spark.sql.parquet.compression.codec", "snappy")
        .config("spark.ui.showConsoleProgress", "false")
    )
    for key, value in settings.extra:
        builder = builder.config(key, value)
    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark
