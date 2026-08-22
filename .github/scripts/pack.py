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
    
    # 2. 目录映射表：(源码相对目录, 释放到路由器的根前缀)
    mappings = [
        ("luci-app-at-webserver/root", ""),        # 映射到 / (usr/share/luci/menu.d 等)
        ("luci-app-at-webserver/htdocs", "www"),    # 映射到 /www (luci-static)
        ("at-webserver/files", ""),                 # 映射到 / (etc/init.d, usr/bin, www/5700 等)
    ]

    # 3. 构建 data.tar.gz
    data_io = io.BytesIO()
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
                        arcname = "./" + arcname_path if (arcname_path := rel) else "./"
                        
                    mode = 0o755 if f.endswith(".sh") or "init.d" in arcname or "bin" in arcname or "cgi-bin" in arcname else 0o644
                    
                    with open(fp, "rb") as rf:
                        data = rf.read()
                    ti = tarfile.TarInfo(name=arcname)
                    ti.size, ti.mtime, ti.mode = len(data), int(time.time()), mode
                    tar.addfile(ti, io.BytesIO(data))
                
    # 4. 打包 .ipk
    with tarfile.open(output_file, mode="w:gz") as ipk:
        for name, data in [("debian-binary", debian_binary), ("control.tar.gz", ctrl_io.getvalue()), ("data.tar.gz", data_io.getvalue())]:
            ti = tarfile.TarInfo(name=name)
            ti.size, ti.mtime, ti.mode = len(data), int(time.time()), 0o644
            ipk.addfile(ti, io.BytesIO(data))

if __name__ == "__main__":
    build_ipk("luci-app-mt5700webui", "1.0.0-1", arch, f"luci-app-mt5700webui_1.0.0-1_{arch}.ipk")
