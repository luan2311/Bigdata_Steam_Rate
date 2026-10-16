"""Script tự động khởi tạo Process Group trên NiFi 2.0 và trích xuất tệp flow definition chuẩn."""

import json
import urllib3
import requests

urllib3.disable_warnings()

BASE_URL = "https://localhost:8443/nifi-api"

def main():
    print("[*] Đăng nhập vào NiFi 2.0 API...")
    res = requests.post(
        f"{BASE_URL}/access/token",
        data={"username": "admin", "password": "BigDataSteam2026!"},
        verify=False,
    )
    if res.status_code != 201:
        print(f"[-] Đăng nhập thất bại: HTTP {res.status_code}")
        return
    token = res.text
    headers = {"Authorization": f"Bearer {token}"}

    # Lấy Root Process Group ID
    pg_root = requests.get(f"{BASE_URL}/process-groups/root", headers=headers, verify=False).json()
    root_id = pg_root["id"]

    # Xóa các processor / process group cũ đang có ở root để làm sạch
    sub_groups = requests.get(f"{BASE_URL}/process-groups/{root_id}/process-groups", headers=headers, verify=False).json().get("processGroups", [])
    for g in sub_groups:
        requests.delete(f"{BASE_URL}/process-groups/{g['id']}?version={g['revision']['version']}", headers=headers, verify=False)
    
    procs = requests.get(f"{BASE_URL}/process-groups/{root_id}/processors", headers=headers, verify=False).json().get("processors", [])
    for p in procs:
        requests.delete(f"{BASE_URL}/processors/{p['id']}?version={p['revision']['version']}", headers=headers, verify=False)

    print("[*] Đang tạo Process Group 'Steam Reviews Ingestion Flow (Sample 10K)'...")
    pg_payload = {
        "revision": {"version": 0},
        "component": {
            "name": "Steam Reviews Ingestion Flow (Sample 10K)",
            "comments": "Luồng tiếp nhận dữ liệu Steam Reviews mẫu (~10.000 bản ghi) từ Landing Zone vào HDFS Bronze qua WebHDFS REST API",
            "position": {"x": 300, "y": 150},
        },
    }
    res_pg = requests.post(f"{BASE_URL}/process-groups/{root_id}/process-groups", headers=headers, json=pg_payload, verify=False)
    new_pg = res_pg.json()
    new_pg_id = new_pg["id"]
    print(f"[+] Đã tạo Process Group thành công! ID: {new_pg_id}")

    # Tạo các processor bên trong Process Group mới
    processors_config = [
        ("ListFile - Quét tệp mẫu CSV", "org.apache.nifi.processors.standard.ListFile", 100, 100, {"Input Directory": "/opt/nifi/data/sample", "File Filter": "steam_reviews_sample_10k\\.csv"}),
        ("FetchFile - Nạp nội dung tệp", "org.apache.nifi.processors.standard.FetchFile", 100, 300, {"File to Fetch": "${absolute.path}/${filename}"}),
        ("SplitRecord - Phân lô 5000 dòng", "org.apache.nifi.processors.standard.SplitRecord", 100, 500, {"Records Per Split": "5000"}),
        ("InvokeHTTP - Đẩy vào HDFS WebHDFS", "org.apache.nifi.processors.standard.InvokeHTTP", 100, 700, {"HTTP Method": "PUT", "Remote URL": "http://hdfs-namenode:9870/webhdfs/v1/steam/bronze/sample/batch_01.csv?op=CREATE"}),
        ("LogAttribute - Cách ly bản ghi lỗi (Quarantine)", "org.apache.nifi.processors.standard.LogAttribute", 600, 500, {"Log Level": "warn"}),
    ]

    for name, p_type, x, y, props in processors_config:
        p_body = {
            "revision": {"version": 0},
            "component": {
                "name": name,
                "type": p_type,
                "position": {"x": x, "y": y},
                "config": {"properties": props},
            },
        }
        r = requests.post(f"{BASE_URL}/process-groups/{new_pg_id}/processors", headers=headers, json=p_body, verify=False)
        if r.status_code == 201:
            print(f"  [+] Đã tạo: {name}")
        else:
            print(f"  [-] Lỗi tạo {name}: {r.status_code}")

    # Tải flow definition chuẩn NiFi 2.0 vừa tạo về lưu đè vào file JSON của dự án
    dl = requests.get(f"{BASE_URL}/process-groups/{new_pg_id}/download", headers=headers, verify=False)
    if dl.status_code == 200:
        with open("nifi/flows/steam_reviews_ingestion_sample_flow.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(dl.json(), indent=2, ensure_ascii=False))
        print("[+] Đã cập nhật tệp flow definition chuẩn NiFi 2.0 tại: nifi/flows/steam_reviews_ingestion_sample_flow.json")

if __name__ == "__main__":
    main()
