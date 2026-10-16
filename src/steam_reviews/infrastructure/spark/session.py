"""SparkSession factory for local mode and, later, the cluster from infra/."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

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
        repo_tools = Path(__file__).resolve().parents[4] / "tools" / "hadoop"
        if (repo_tools / "bin" / "winutils.exe").exists():
            hadoop_home = str(repo_tools)
            os.environ["HADOOP_HOME"] = hadoop_home

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
    python_exe = sys.executable
    os.environ["PYSPARK_PYTHON"] = python_exe
    os.environ["PYSPARK_DRIVER_PYTHON"] = python_exe
    hadoop_home = os.environ.get("HADOOP_HOME")
    builder = (
        SparkSession.builder.master(settings.master)
        .appName(settings.app_name)
        .config("spark.driver.memory", settings.driver_memory)
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", str(settings.shuffle_partitions))
        .config("spark.sql.parquet.compression.codec", "snappy")
        .config("spark.ui.showConsoleProgress", "false")
        .config("spark.pyspark.python", python_exe)
        .config("spark.pyspark.driver.python", python_exe)
    )
    if hadoop_home:
        escaped_home = hadoop_home.replace("\\", "/")
        hadoop_bin = f"{escaped_home}/bin"
        java_opts = f"-Dhadoop.home.dir={escaped_home} -Djava.library.path={hadoop_bin}"
        builder = builder.config("spark.driver.extraJavaOptions", java_opts)
        builder = builder.config("spark.executor.extraJavaOptions", java_opts)
    for key, value in settings.extra:
        builder = builder.config(key, value)
    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    if os.name == "nt":
        try:
            jvm = spark.sparkContext._jvm
            cls = jvm.java.lang.Class.forName("org.apache.hadoop.io.nativeio.NativeIO$Windows")
            field = cls.getDeclaredField("nativeLoaded")
            field.setAccessible(True)
            field.setBoolean(None, False)
        except Exception:
            pass

    try:
        from pyspark.ml.util import DefaultParamsReader

        if not getattr(DefaultParamsReader, "_antigravity_patched", False):
            orig_load = DefaultParamsReader.loadMetadata

            @staticmethod
            def patched_loadMetadata(path: str, sc, expectedClassName: str = ""):
                metadataPath = os.path.join(path, "metadata")
                clean = metadataPath
                if clean.startswith("file:"):
                    clean = clean[5:]
                    while clean.startswith("/"):
                        clean = clean[1:]
                if os.name == "nt" and len(clean) >= 2 and clean[1] == ":":
                    clean = os.path.normpath(clean)
                if os.path.isdir(clean):
                    parts = [f for f in os.listdir(clean) if f.startswith("part-")]
                    if parts:
                        with open(os.path.join(clean, parts[0]), "r", encoding="utf-8") as f:
                            return DefaultParamsReader._parseMetaData(f.readline().strip(), expectedClassName)
                try:
                    jvm = sc._gateway.jvm
                    jpath = jvm.org.apache.hadoop.fs.Path(metadataPath)
                    conf = sc._jsc.hadoopConfiguration()
                    fs = jpath.getFileSystem(conf)
                    if fs.exists(jpath):
                        statuses = fs.listStatus(jpath)
                        for stat in statuses:
                            name = stat.getPath().getName()
                            if name.startswith("part-"):
                                stream = fs.open(stat.getPath())
                                reader = jvm.java.io.BufferedReader(jvm.java.io.InputStreamReader(stream, "UTF-8"))
                                line = reader.readLine()
                                reader.close()
                                stream.close()
                                return DefaultParamsReader._parseMetaData(line, expectedClassName)
                except Exception:
                    pass
                return orig_load(path, sc, expectedClassName)

            DefaultParamsReader.loadMetadata = patched_loadMetadata
            DefaultParamsReader._antigravity_patched = True
    except Exception:
        pass

    return spark
