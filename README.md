# Phân tích dữ liệu đánh giá trò chơi trên Steam

Bộ khung đồ án cho 3 thành viên, thực hiện trong 15 ngày. Luồng dữ liệu dự kiến: **Kaggle → NiFi → HDFS → Spark → dashboard**.

**Trạng thái:** đã tạo cấu trúc thư mục, package Python và tài liệu phân công. Chưa triển khai pipeline, mô hình, dashboard hoặc cấu hình chạy cụm. Các thư mục trống được giữ bằng `.gitkeep`; không phải thành phần đã hoàn thành.

## Tài liệu làm việc

- [Plan.md](Plan.md): phạm vi, lịch 15 ngày, yêu cầu môn học và tiêu chí nghiệm thu.
- [Checklist.md](Checklist.md): công việc theo từng thành viên và từng ngày.
- [Kiến trúc](docs/architecture.md): ranh giới các lớp, chiều phụ thuộc và nơi đặt mã.
- [Nhật ký đóng góp](docs/contributions.md): mẫu ghi tiến độ, review và đóng góp thực tế.

## Cấu trúc đã tạo

```text
Bigdata/
├── src/steam_reviews/
│   ├── domain/
│   │   ├── entities/             # Khái niệm Review, Dataset, Run
│   │   └── policies/             # Quy tắc nhãn, chất lượng, KPI
│   ├── application/
│   │   ├── ports/                # Hợp đồng xử lý/lưu trữ/đọc kết quả
│   │   ├── dto/                  # Request/result thuần Python
│   │   └── use_cases/            # Clean, aggregate, train, evaluate, query
│   ├── infrastructure/
│   │   ├── ingestion/            # Adapter nguồn, checksum, manifest
│   │   ├── storage/              # Adapter HDFS và snapshot cục bộ
│   │   ├── spark/                # DataFrame/SQL, ETL phân tán
│   │   └── ml/                   # Spark MLlib, lưu/nạp model
│   ├── presentation/
│   │   ├── cli/                 # Điểm vào job batch, nhận tham số
│   │   └── dashboard/
│   │       ├── pages/            # Các trang Streamlit
│   │       └── components/       # Bộ lọc, biểu đồ, trạng thái rỗng
│   └── bootstrap/               # Đọc cấu hình, ghép adapter với use case
├── infra/
│   ├── docker/                  # Dockerfile/Compose sẽ triển khai
│   ├── hadoop/                  # Cấu hình HDFS
│   └── spark/                   # Cấu hình cụm Spark
├── nifi/
│   ├── flows/                   # Flow JSON export
│   └── parameters/              # Mẫu tham số đã loại thông tin bí mật
├── schemas/
│   ├── source/                  # Schema CSV thực tế
│   ├── silver/                  # Schema dữ liệu sạch
│   └── gold/                    # Schema bảng tổng hợp và metrics
├── tests/
│   ├── unit/                    # Domain/use case, dùng fake ports
│   ├── integration/             # Adapter/Spark/HDFS/NiFi
│   ├── e2e/                     # Pipeline mẫu và dashboard
│   └── fixtures/                # Dữ liệu nhỏ do nhóm tạo để kiểm thử
├── scripts/                     # Wrapper vận hành, không đặt nghiệp vụ
├── data/
│   ├── landing/                 # Dataset đã tải
│   ├── sample/                  # Mẫu phát triển tái lập
│   └── cache/                   # Cache cục bộ
├── artifacts/
│   ├── manifests/               # Nguồn, checksum, batch, run
│   ├── metrics/                 # Độ đo và benchmark nhỏ
│   ├── figures/                 # Hình, biểu đồ phục vụ báo cáo
│   ├── models/                  # Model sinh ra, không commit Git
│   └── snapshots/               # Snapshot dashboard, không commit Git
├── docs/
│   ├── architecture.md
│   ├── contributions.md
│   ├── data/                    # Data dictionary và quyết định lấy mẫu
│   ├── runbooks/                # Hướng dẫn dựng/chạy/xử lý lỗi
│   └── evidence/                # Bằng chứng kiểm thử và nghiệm thu
├── report/
│   ├── word/                    # Báo cáo Word
│   ├── slides/                  # PPT tiến độ và cuối kỳ
│   └── demo/                    # Kịch bản và tham chiếu video
├── Rule/                        # Hai PDF quy định đã có
├── Plan.md
├── Checklist.md
└── README.md
```

## Quy tắc phát triển

1. `domain` độc lập framework; `application` chỉ phụ thuộc `domain` và các hợp đồng do chính nó khai báo.
2. `infrastructure` triển khai các port bằng Spark/HDFS/công cụ ngoài. `presentation` gọi use case, không tự viết ETL hoặc huấn luyện.
3. `bootstrap` là nơi ghép dependency. Entry point mỏng có thể gọi bootstrap; module nghiệp vụ/UI còn lại nhận dependency qua tham số.
4. Giữ xử lý hàng triệu review trong Spark adapter. Qua ranh giới use case chỉ truyền cấu hình, tham chiếu dataset/model, thống kê nhỏ; không `collect()` toàn bộ dữ liệu lên driver.
5. `infra/` chứa cấu hình triển khai; `src/steam_reviews/infrastructure/` chứa mã adapter. `nifi/` chứa flow, không trộn vào Python domain.
6. Chưa khóa dependency/runtime: TV1 và TV2 thực hiện ở D2 trước khi bổ sung file cài đặt. Không có lệnh chạy ứng dụng ở giai đoạn bộ khung này.

Dataset và sản phẩm sinh ra có thể lớn: xem [quy ước dữ liệu](data/README.md), [artifact](artifacts/README.md) và `.gitignore`. Những chỉ số hiện tại trong tài liệu là mục tiêu kế hoạch, không phải kết quả thực nghiệm.
