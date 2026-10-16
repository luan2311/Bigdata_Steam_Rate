"""Script tự động khởi tạo Process Group trên NiFi 2.0, kết nối đầy đủ các Processor và trích xuất flow definition chuẩn."""

import json
import sys
import urllib3
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

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

    # Xóa các process group cũ đang có ở root để làm sạch hoàn toàn canvas
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

    # Cấu hình 5 processors chuẩn NiFi 2.0
    processors_config = [
        {
            "key": "list_file",
            "name": "ListFile - Quét tệp mẫu CSV",
            "type": "org.apache.nifi.processors.standard.ListFile",
            "position": {"x": 300, "y": 50},
            "properties": {"Input Directory": "/opt/nifi/data/sample", "File Filter": "steam_reviews_sample_10k\\.csv"},
            "auto_term": [],
        },
        {
            "key": "fetch_file",
            "name": "FetchFile - Nạp nội dung tệp",
            "type": "org.apache.nifi.processors.standard.FetchFile",
            "position": {"x": 300, "y": 250},
            "properties": {"File to Fetch": "${absolute.path}/${filename}"},
            "auto_term": [],
        },
        {
            "key": "split_text",
            "name": "SplitText - Phân lô 5000 dòng",
            "type": "org.apache.nifi.processors.standard.SplitText",
            "position": {"x": 300, "y": 450},
            "properties": {"Line Split Count": "5000", "Header Line Count": "1"},
            "auto_term": ["original"],
        },
        {
            "key": "invoke_http",
            "name": "InvokeHTTP - Đẩy vào HDFS WebHDFS",
            "type": "org.apache.nifi.processors.standard.InvokeHTTP",
            "position": {"x": 300, "y": 680},
            "properties": {
                "HTTP Method": "PUT",
                "HTTP URL": "http://hdfs-namenode:9870/webhdfs/v1/steam/bronze/sample/batch_01.csv?op=CREATE",
            },
            "auto_term": ["Original", "Response", "Retry"],
        },
        {
            "key": "log_attribute",
            "name": "LogAttribute - Cách ly bản ghi lỗi (Quarantine)",
            "type": "org.apache.nifi.processors.standard.LogAttribute",
            "position": {"x": 820, "y": 450},
            "properties": {"Log Level": "warn"},
            "auto_term": ["success"],
        },
    ]

    created_procs = {}
    for p_cfg in processors_config:
        p_body = {
            "revision": {"version": 0},
            "component": {
                "name": p_cfg["name"],
                "type": p_cfg["type"],
                "position": p_cfg["position"],
                "config": {
                    "properties": p_cfg["properties"],
                    "autoTerminatedRelationships": p_cfg["auto_term"],
                },
            },
        }
        r = requests.post(f"{BASE_URL}/process-groups/{new_pg_id}/processors", headers=headers, json=p_body, verify=False)
        if r.status_code == 201:
            proc_data = r.json()
            created_procs[p_cfg["key"]] = proc_data["id"]
            print(f"  [+] Đã tạo Processor: {p_cfg['name']}")
        else:
            print(f"  [-] Lỗi tạo {p_cfg['name']}: {r.status_code} - {r.text}")

    print("[*] Đang kết nối các đường ống dữ liệu (Connections)...")
    connections_config = [
        ("list_file", "fetch_file", ["success"], "success"),
        ("fetch_file", "split_text", ["success"], "success"),
        ("fetch_file", "log_attribute", ["failure", "not.found", "permission.denied"], "lỗi đọc tệp"),
        ("split_text", "invoke_http", ["splits"], "splits (từng lô)"),
        ("split_text", "log_attribute", ["failure"], "lỗi phân chia"),
        ("invoke_http", "log_attribute", ["Failure", "No Retry"], "lỗi HDFS"),
    ]

    for src_key, dst_key, rels, conn_name in connections_config:
        conn_body = {
            "revision": {"version": 0},
            "component": {
                "name": conn_name,
                "source": {
                    "id": created_procs[src_key],
                    "type": "PROCESSOR",
                    "groupId": new_pg_id,
                },
                "destination": {
                    "id": created_procs[dst_key],
                    "type": "PROCESSOR",
                    "groupId": new_pg_id,
                },
                "selectedRelationships": rels,
            },
        }
        r_conn = requests.post(f"{BASE_URL}/process-groups/{new_pg_id}/connections", headers=headers, json=conn_body, verify=False)
        if r_conn.status_code == 201:
            print(f"  [+] Đã tạo kết nối: {src_key} -> {dst_key} ({conn_name})")
        else:
            print(f"  [-] Lỗi kết nối {src_key} -> {dst_key}: {r_conn.status_code} - {r_conn.text}")

    # Kiểm tra trạng thái validation của toàn bộ Processors
    procs_status = requests.get(f"{BASE_URL}/process-groups/{new_pg_id}/processors", headers=headers, verify=False).json().get("processors", [])
    has_error = False
    print("\n[*] Kiểm tra tính hợp lệ (Validation) của Flow:")
    for p in procs_status:
        v_errors = p["component"].get("validationErrors", [])
        p_name = p["component"]["name"]
        if v_errors:
            has_error = True
            print(f"  [!] {p_name}: {v_errors}")
        else:
            print(f"  [OK] {p_name}: 0 lỗi cấu hình (Valid)")

    # Tải flow definition chuẩn NiFi 2.0 vừa tạo về lưu đè vào file JSON của dự án
    dl = requests.get(f"{BASE_URL}/process-groups/{new_pg_id}/download", headers=headers, verify=False)
    if dl.status_code == 200:
        with open("nifi/flows/steam_reviews_ingestion_sample_flow.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(dl.json(), indent=2, ensure_ascii=False))
        print("\n[+] Đã cập nhật tệp flow definition hoàn chỉnh tại: nifi/flows/steam_reviews_ingestion_sample_flow.json")

    # Xóa file tạm proc_info.txt nếu có
    import os
    if os.path.exists("proc_info.txt"):
        os.remove("proc_info.txt")

if __name__ == "__main__":
    main()
