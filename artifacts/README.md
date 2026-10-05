# Sản phẩm thực nghiệm

- `manifests/`: thông tin nguồn, checksum, phiên bản, batch, run và split.
- `metrics/`: JSON/CSV nhỏ chứa độ đo mô hình và benchmark.
- `figures/`: biểu đồ/ảnh đã chọn cho báo cáo.
- `models/`: model sinh ra, bỏ qua Git.
- `snapshots/`: bảng kết quả cho dashboard, bỏ qua Git nếu là dữ liệu sinh ra.

Mỗi artifact phải truy ngược được run_id, cấu hình, phạm vi dataset và người thực hiện. Manifest/metrics nhỏ có thể commit sau khi kiểm tra không chứa token hoặc dữ liệu cá nhân không cần thiết. Với model/snapshot ngoài Git, ghi vị trí lưu, checksum và cách tạo lại trong hướng dẫn bàn giao.

Hiện chưa có kết quả thực nghiệm. Không thêm số liệu minh họa mà không gắn nhãn rõ.
