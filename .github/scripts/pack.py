import os
import sys
import tarfile
import io
import time

arch = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else "aarch64"

def build_ipk(pkg_name, version, arch, output_file):
    debian_binary = b"2.0\n"
    control_text = f"Package: {pkg_name}\nVersion: {version}\nArchitecture: {arch}\nMaintainer: ZJJCKA\nDescription: WebUI for MT5700\n".encode("utf-8")
    
    # 1. 构建 control.tar.gz
    ctrl_io = io.BytesIO()
    with tarfile.open(fileobj=ctrl_io, mode="w:gz") as tar:
        ti = tarfile.TarInfo(name="./control")
        ti.size, ti.mtime, ti.mode = len(control_text), int(time.time()), 0o644
        tar.addfile(ti, io.BytesIO(control_text))
    
    # 2. 目录映射配置：(源码路径, 路由器根路径前缀)
    mappings = [
        ("luci-app-at-webserver/root", ""),        # 映射菜单与 ACL 文件 -> /usr/share/...
        ("luci-app-at-webserver/htdocs", "www"),    # 映射静态视图 JS 文件 -> /www/luci-static/...
        ("at-webserver/files", ""),                 # 映射后台脚本与 Web 前端 -> /etc/init.d/..., /usr/bin/...
    ]

    data_io = io.BytesIO()
    added_dirs = set()

    with tarfile.open(fileobj=data_io, mode="w:gz") as tar:
        for src_dir, target_prefix in mappings:
            if not os.path.exists(src_dir):
                continue
            for root, _, files in os.walk(src_dir):
                for f in files:
                    fp = os.path.join(root, f)
                    rel = os.path.relpath(fp, src_dir).replace(os.sep, "/")
                    
                    if target_prefix:
                        arcname = "./" + target_prefix + "/" + rel
                    else:
                        arcname = "./" + rel

                    # 补全父级目录节点，确保 Busybox tar 解压时能顺利新建文件夹
                    parent_dir = os.path.dirname(arcname)
                    dir_parts = parent_dir.split("/")
                    current_dir = ""
                    for part in dir_parts:
                        if not part:
                            continue
                        current_dir = current_dir + "/" + part if current_dir else part
                        if current_dir not in added_dirs:
                            d_ti = tarfile.TarInfo(name=current_dir)
                            d_ti.type = tarfile.DIRTYPE
                            d_ti.mode = 0o755
                            d_ti.mtime = int(time.time())
                            tar.addfile(d_ti)
                            added_dirs.add(current_dir)

                    # 添加文件项
                    mode = 0o755 if f.endswith(".sh") or "init.d" in arcname or "bin" in arcname or "cgi-bin" in arcname else 0o644
                    with open(fp, "rb") as rf:
                        data = rf.read()
                    
                    ti = tarfile.TarInfo(name=arcname)
                    ti.size = len(data)
                    ti.mtime = int(time.time())
                    ti.mode = mode
                    tar.addfile(ti, io.BytesIO(data))
                
    # 3. 打包生成最终的 .ipk 格式
    with tarfile.open(output_file, mode="w:gz") as ipk:
        for name, data in [("debian-binary", debian_binary), ("control.tar.gz", ctrl_io.getvalue()), ("data.tar.gz", data_io.getvalue())]:
            ti = tarfile.TarInfo(name=name)
            ti.size, ti.mtime, ti.mode = len(data), int(time.time()), 0o644
            ipk.addfile(ti, io.BytesIO(data))

if __name__ == "__main__":
    build_ipk("luci-app-mt5700webui", "1.0.0-1", arch, f"luci-app-mt5700webui_1.0.0-1_{arch}.ipk")
