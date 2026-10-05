# CHECKLIST CÔNG VIỆC — 3 THÀNH VIÊN / 15 NGÀY

**Đề tài:** Phân tích dữ liệu đánh giá trò chơi trên Steam.  
**Căn cứ:** [Plan.md](Plan.md), hai PDF trong `Rule/`, [kiến trúc mã nguồn](docs/architecture.md).  
**Thời lượng dự kiến:** 4 giờ/người/ngày; D1–D15 là ngày kế hoạch, gắn ngày thực tế khi nhóm bắt đầu.  
**Trạng thái ban đầu:** 0/45 đầu việc theo ngày được nghiệm thu. Thư mục đã tạo chỉ là bộ khung; không đồng nghĩa hoàn thành việc triển khai.

## Cách sử dụng

- Thay TV1/TV2/TV3 bằng họ tên và MSSV trong `docs/contributions.md`.
- Chỉ chuyển `[ ]` thành `[x]` sau khi có sản phẩm, kiểm tra đạt và người review xác nhận. Nếu một phần chưa xong, giữ ô trống và ghi phần còn lại vào nhật ký.
- Mỗi đầu việc có mã cố định, ngày đích, đầu ra và điều kiện hoàn thành. Dùng mã đó trong commit/PR và nhật ký.
- Ghi bằng chứng, thời gian thực tế, trạng thái đang làm/bị chặn và người review ở `docs/contributions.md`; cập nhật dòng tiến độ tổng sau mỗi buổi họp.
- Đường dẫn trong checklist là nơi bàn giao dự kiến. Những file chức năng, model, Word/PPT chưa tồn tại phải được tạo trong quá trình thực hiện.
- Nếu bị chặn quá 2 giờ, báo nhóm. Bỏ phần mở rộng trước; giữ NiFi, HDFS/Spark, mô hình cơ bản, dashboard và hồ sơ nộp.

## 1. TV1 — Hạ tầng, NiFi, HDFS và điều phối

**Khu vực chính:** `infra/`, `nifi/`, `src/steam_reviews/infrastructure/ingestion/`, `src/steam_reviews/infrastructure/storage/`, `src/steam_reviews/bootstrap/`.  
**Review:** TV2 kiểm tra dữ liệu/hạ tầng nhận vào; TV3 kiểm tra hướng dẫn dựng và demo.

- [ ] **TV1-D01 — Chốt điều kiện thực hiện.** Chuẩn bị đề cương; xác nhận với GV nhóm 3 người (Rule ghi 2), đề tài, hạn hai giai đoạn và yêu cầu cụm; kiểm kê RAM/disk. **Đầu ra:** ghi nhận trong `docs/runbooks/` và nhật ký; các mục chờ trả lời được liệt kê, không tự coi đã duyệt.
- [ ] **TV1-D02 — Dựng môi trường smoke.** Tạo cấu hình trong `infra/`, chạy NiFi, HDFS và Spark; cùng TV2 khóa phiên bản/runtime. **Đạt khi:** ghi/đọc HDFS và chạy Spark job nhỏ được, có lệnh dựng lại và cấu hình không chứa bí mật.
- [ ] **TV1-D03 — Xây luồng tiếp nhận.** Làm ListFile/FetchFile → CSVReader/SplitRecord → WebHDFS; giữ nguyên dữ liệu nguồn và xử lý tệp hoàn tất. **Đạt khi:** khoảng 10.000 record vào HDFS, fixture CSV nhiều dòng/Unicode đọc đúng; export flow vào `nifi/flows/`.
- [ ] **TV1-D04 — Hoàn thiện độ tin cậy ingestion.** Bổ sung batch_id tái lập, manifest, ghi tạm/commit, retry giới hạn, quarantine và back pressure. **Đạt khi:** mô phỏng lỗi có nhánh xử lý; replay cùng lô không gây tăng số ID duy nhất sau ETL; lưu log/ảnh vào `docs/evidence/`.
- [ ] **TV1-D05 — Nạp Core và chứng minh phân tán.** Nạp phạm vi dữ liệu đã chốt với TV2; kiểm tra 2 DataNode, replication và executor/task. **Đạt khi:** có manifest Core, ảnh/log HDFS/Spark, dữ liệu bàn giao được tới dashboard tối thiểu của TV3.
- [ ] **TV1-D06 — Đo ingestion/ETL.** Ghi số record, thời gian, RAM/disk, lỗi, tham số queue; hỗ trợ TV2 phân vùng/tài nguyên. **Đầu ra:** bảng đo ở `artifacts/metrics/` và bản viết phần NiFi/HDFS cho báo cáo.
- [ ] **TV1-D07 — Bàn giao tiến độ hạ tầng.** Demo luồng NiFi và HDFS, tổng hợp vướng mắc, quyết định điều kiện thử Full. **Đạt khi:** TV3 có sơ đồ, ảnh thật, thông số máy và nội dung để đưa vào gói báo cáo tiến độ.
- [ ] **TV1-D08 — Điều phối các công đoạn.** Ghép adapter/use case tại bootstrap và bổ sung wrapper cần thiết ở `scripts/`; chỉ cho Spark đọc đợt có dấu hoàn tất. **Đạt khi:** thử đợt chưa hoàn tất bị ngăn đọc; restart không làm mất trạng thái đã commit.
- [ ] **TV1-D09 — Review vận hành và cấu hình.** Kiểm tra import flow, tham số mẫu, quyền/đường dẫn, event log và nhật ký executor. **Đạt khi:** TV2 chạy được pipeline bằng hướng dẫn trong `docs/runbooks/`; không có secret trong file bàn giao.
- [ ] **TV1-D10 — Chạy quy mô đã chốt.** Thử Full nếu tài nguyên cho phép; nếu không, hoàn thiện Core và ghi lý do giới hạn. **Đầu ra:** manifest/run_id, số bản ghi, RAM/disk/time thực tế; không ghi kết quả subset thành Full.
- [ ] **TV1-D11 — Benchmark và thử khôi phục.** So sánh 1/2 worker với cùng đầu vào và tổng tài nguyên khi so sánh; thử HDFS gián đoạn và replay. **Đạt khi:** có cấu hình, số đo từng lần, trạng thái cache, bằng chứng không đọc lô dở và không nhân đôi silver.
- [ ] **TV1-D12 — Hoàn thiện gói kỹ thuật.** Export flow, tham số mẫu, cấu hình cụm và README cài/chạy/dừng/khởi động lại; sao lưu artifact. **Đạt khi:** không thiếu tệp/đường dẫn cần thiết, TV3 nhận được ứng viên bàn giao để kiểm tra sạch.
- [ ] **TV1-D13 — Hỗ trợ nghiệm thu độc lập.** Để TV3 tự dựng theo README; chỉ ghi nhận/sửa lỗi hướng dẫn hoặc cấu hình. **Đạt khi:** có nhật ký dựng sạch, lỗi đã sửa và kết quả kiểm tra lại phần ảnh hưởng.
- [ ] **TV1-D14 — Diễn tập hạ tầng và dự phòng.** Trình bày NiFi → HDFS/Spark; kiểm tra bản sao, dataset smoke offline và artifact demo. **Đạt khi:** demo không phụ thuộc tải lại dataset lớn; biết khôi phục nếu máy/mạng lỗi.
- [ ] **TV1-D15 — Điều phối kiểm tra và nộp.** Kiểm kê source/config/README; cùng nhóm rà V1–V10 của Plan.md, lịch nộp và quyền truy cập tệp. **Đạt khi:** gói cuối đủ thành phần, có bản sao và bằng chứng nộp Classroom theo hạn thật.

## 2. TV2 — Dữ liệu, Spark, phân tích và ML

**Khu vực chính:** `src/steam_reviews/domain/`, `src/steam_reviews/application/`, `src/steam_reviews/infrastructure/spark/`, `src/steam_reviews/infrastructure/ml/`, `src/steam_reviews/presentation/cli/`, `schemas/`.  
**Review:** TV1 kiểm tra chạy phân tán/tái lập; TV3 kiểm tra ý nghĩa KPI và kết quả hiển thị.

- [ ] **TV2-D01 — Chốt bài toán dữ liệu.** Kiểm tra truy cập Kaggle, liệt kê cột cần và 5 câu hỏi phân tích; đề xuất phạm vi EDA/ML. **Đầu ra:** ghi chú trong `docs/data/`, phân biệt nhãn khuyến nghị với cảm xúc ba lớp.
- [ ] **TV2-D02 — Kiểm kê và khóa hợp đồng dữ liệu.** Tải/đo tệp, checksum, header, số record, ngày/ngôn ngữ/nhãn; tạo mẫu tái lập; cùng TV1/TV3 chốt schema source/silver/gold. **Đạt khi:** có data dictionary, manifest, grain/bộ lọc của gold, quyết định Core và phiên bản runtime.
- [ ] **TV2-D03 — Xây ETL đầu tiên đúng lớp.** Khai báo policy/DTO/port/use case cần thiết; adapter Spark đọc bronze, chuẩn hóa kiểu/null/UTC. **Đạt khi:** smoke chạy qua CLI/use case; fixture lỗi có kết quả rõ; application không import PySpark.
- [ ] **TV2-D04 — Làm sạch và dedup.** Áp dụng quy tắc ID/nhãn/game, xử lý thiếu, chọn bản cập nhật mới nhất theo ID và ghi silver Parquet. **Đạt khi:** có quarantine/reason, số trước–sau đối soát đúng, tách lỗi tệp khỏi lỗi record.
- [ ] **TV2-D05 — Tạo gold v1.** Xây quality/game/monthly/language/playtime summaries theo schema đã thống nhất. **Đạt khi:** mẫu số/rate đúng, có run_id và chiều lọc; TV3 dùng dữ liệu thật, không phải fixture.
- [ ] **TV2-D06 — Tạo baseline và LR đầu tiên.** Chọn tập tiếng Anh, loại văn bản rỗng; chia train/validation/test theo nhóm text hash, cố định seed; chạy baseline đa số và TF-IDF + LR. **Đầu ra:** split manifest, cấu hình, metrics đầu tiên; IDF chỉ fit trên train.
- [ ] **TV2-D07 — Bàn giao tiến độ phân tích/ML.** Kiểm tra giao nhau ID/text hash bằng 0; trình bày baseline, phân bố lớp và hướng cải thiện. **Đạt khi:** TV3 có số liệu thật, lý thuyết và hạn chế để hoàn thiện slide tiến độ.
- [ ] **TV2-D08 — Chọn cấu hình trên validation.** Chạy tối đa 4 cấu hình theo Plan.md, kiểm tra có/không trọng số lớp. **Đạt khi:** lưu cấu hình và metrics từng lần, chọn bằng macro-F1 validation; chưa dùng test để chọn tham số.
- [ ] **TV2-D09 — Đánh giá test và phân tích lỗi.** Chốt mô hình rồi chấm baseline/LR trên cùng test; tính macro-F1, precision/recall từng lớp, PR-AUC, confusion matrix; xem khoảng 30 lỗi. **Đạt khi:** có model reference, metrics và giải thích lỗi trung thực.
- [ ] **TV2-D10 — Tối ưu theo số đo.** Hỗ trợ chạy Full/Core với TV1; điều chỉnh partition/kích thước tệp và kiểm tra đối soát. **Đạt khi:** số liệu các mức dữ liệu có phạm vi rõ, không collect toàn bộ review lên driver, không thay test sau khi xem kết quả.
- [ ] **TV2-D11 — Kiểm tra kết quả độc lập.** Đối soát gold bằng truy vấn riêng; kiểm tra model nạp lại; cùng TV3 kiểm tra ít nhất 3 tổ hợp filter. **Đạt khi:** KPI/số lượng khớp và dự đoán mẫu tái lập trong dung sai đã công bố.
- [ ] **TV2-D12 — Viết và đóng gói phần thực nghiệm.** Hoàn thiện lý thuyết, data dictionary, quy trình làm sạch, mô hình, metrics và hạn chế; bàn giao thông số/script cho TV3. **Đạt khi:** report có nguồn, input/output và cách tái tạo từng kết quả chính.
- [ ] **TV2-D13 — Review chéo cuối.** Kiểm tra split, schema, số liệu Word/PPT/dashboard và quy tắc Clean Architecture. **Đạt khi:** lỗi thống kê/import/rò rỉ được sửa và kiểm tra lại; lưu bằng chứng ở `docs/evidence/`.
- [ ] **TV2-D14 — Diễn tập xử lý/ML.** Giải thích nhãn, mất cân bằng, TF-IDF/LR, baseline, cách chia tập và giới hạn. **Đạt khi:** trả lời được vì sao dùng Spark, vì sao không suy diễn nhân quả và vì sao kết quả chỉ áp dụng trong phạm vi dữ liệu.
- [ ] **TV2-D15 — Xác nhận artifact dữ liệu/mô hình.** Kiểm tra metric, model/snapshot tham chiếu, checksum, phiên bản và hướng dẫn tái lập. **Đạt khi:** thành viên khác truy cập được artifact cần dùng và nhận biết rõ full/subset.

## 3. TV3 — Dashboard, kiểm tra số liệu và hồ sơ

**Khu vực chính:** `src/steam_reviews/presentation/dashboard/`, use case đọc dashboard và adapter snapshot phối hợp với TV2, `docs/`, `report/`, `artifacts/figures/`.  
**Review:** TV2 kiểm tra KPI/mô hình; TV1 kiểm tra chạy ứng dụng và gói demo.

- [ ] **TV3-D01 — Khung hồ sơ và giao diện.** Tạo bố cục Word đúng Rule, wireframe 4 trang, điền thông tin thành viên và mẫu nhật ký. **Đạt khi:** nhóm thống nhất màn hình cần có, phân công viết và cấu trúc báo cáo.
- [ ] **TV3-D02 — Chốt hợp đồng hiển thị.** Cùng TV2 chốt KPI, grain gold, mẫu số, đơn vị, run_id, bộ lọc; tạo fixture nhỏ có gắn nhãn minh họa. **Đạt khi:** biết trường đầu vào cho từng biểu đồ và cách hiển thị thiếu/rỗng.
- [ ] **TV3-D03 — Dựng dashboard skeleton.** Tạo entry point, điều hướng và trang tổng quan trong `presentation/dashboard/`; nhận dữ liệu qua use case/port. **Đạt khi:** giao diện chạy với fixture, không import Spark hoặc client HDFS vào trang.
- [ ] **TV3-D04 — Làm trang trò chơi.** Tạo biểu đồ xếp hạng, xu hướng tháng và bộ lọc theo hợp đồng. **Đạt khi:** ngưỡng số đánh giá/mẫu số thể hiện rõ; có kiểm tra filter và trạng thái không có dữ liệu.
- [ ] **TV3-D05 — Kết nối dữ liệu thật.** Đọc snapshot gold thông qua application và adapter; đối chiếu KPI với TV2. **Đạt khi:** toàn luồng tối thiểu chạy được, trang hiển thị nguồn, phạm vi mẫu và run_id thật.
- [ ] **TV3-D06 — Trang chất lượng dữ liệu và slide tiến độ.** Trực quan thiếu/trùng/lỗi và nhóm giờ chơi; tổng hợp hình thật, lý thuyết và baseline được bàn giao. **Đầu ra:** bản nháp gói tiến độ, không dùng số minh họa như kết quả thật.
- [ ] **TV3-D07 — Hoàn thiện báo cáo giai đoạn 1.** Tổng hợp kết quả TV1/TV2, nhật ký tuần 1 và đóng góp; trình bày thử. **Đạt khi:** slide tiến độ, nội dung lý thuyết, demo và tồn đọng sẵn sàng nộp theo lịch GV.
- [ ] **TV3-D08 — Trang đánh giá mô hình.** Hiển thị baseline/LR, metrics, confusion matrix và phạm vi dữ liệu; xử lý thiếu artifact. **Đạt khi:** validation/test được ghi rõ, không gắn nhãn kết quả validation là test.
- [ ] **TV3-D09 — Viết kết quả và hạn chế.** Nhận test metrics từ TV2; kiểm tra số liệu và ví dụ dự đoán; bổ sung phần đánh giá vào Word. **Đạt khi:** số liệu biểu đồ/bảng thống nhất, ví dụ không lộ định danh cá nhân không cần thiết.
- [ ] **TV3-D10 — Hoàn thiện ứng dụng.** Đủ 4 trang, ít nhất 6 biểu đồ, bộ lọc/nhãn/đơn vị đúng; viết ít nhất 5 nhận xét có số liệu. **Đạt khi:** mỗi nhận xét truy được bảng hoặc biểu đồ, phạm vi suy rộng được ghi rõ; đóng băng tính năng.
- [ ] **TV3-D11 — Kiểm thử tương tác và đối soát.** Kiểm tra filter, dữ liệu rỗng, run_id, snapshot thiếu; so ít nhất 3 tổ hợp filter với truy vấn TV2. **Đạt khi:** lưu bảng kiểm tra expected/actual và sửa lỗi làm sai kết luận.
- [ ] **TV3-D12 — Ghép hồ sơ hoàn chỉnh.** Tạo Word đủ các mục theo Rule, PPT cuối, kịch bản demo; nhận phần viết của TV1/TV2 và kiểm kê source/artifact. **Đạt khi:** có ứng viên bàn giao tại `report/word/`, `report/slides/`, `report/demo/`.
- [ ] **TV3-D13 — Tự dựng/chạy theo README.** Dùng môi trường sạch, làm theo hướng dẫn; ghi mọi bước thiếu và lỗi. **Đạt khi:** smoke từ landing tới dashboard chạy lại được sau sửa; Word/mục lục/nguồn và đường dẫn được rà.
- [ ] **TV3-D14 — Điều phối diễn tập toàn bài.** Cả 3 người trình bày; đo thời gian theo yêu cầu GV; ghi video dự phòng và kiểm tra artifact offline. **Đạt khi:** demo liền mạch, video xem được, ai cũng biết phần mình và câu hỏi phản biện.
- [ ] **TV3-D15 — Đóng gói và xác minh bài nộp.** Kiểm tra Word/PPT, góp ý cuối, nhật ký/đóng góp, source và liên kết dữ liệu; phối hợp TV1 nộp. **Đạt khi:** tệp mở/tải lại được, quyền truy cập đúng, có bằng chứng nộp và bản sao gói cuối.

## 4. Các điểm bàn giao bắt buộc

| Hạn | Người giao → nhận | Sản phẩm | Điều kiện để người nhận bắt đầu |
|---|---|---|---|
| Cuối D2 | TV2 → TV1, TV3 | Schema v1, mẫu thật, grain gold, data dictionary | Tên cột/kiểu/null/đơn vị được review; fixture giao diện ghi rõ minh họa. |
| Cuối D3 | TV1 → TV2 | Bronze smoke và manifest | Tệp đọc được, CSV multiline đúng, có dấu hoàn tất. |
| Cuối D5 | TV2 → TV3 | Gold/snapshot v1 | KPI và run_id đã đối soát; adapter đọc thống nhất với hợp đồng. |
| D6–D7 | TV1, TV2 → TV3 | Sơ đồ, ảnh, lý thuyết, baseline/metrics sơ bộ | Số liệu thật, cấu hình và phạm vi được ghi rõ. |
| Cuối D9 | TV2 → TV3 | Model metrics cuối và ví dụ lỗi | Cùng test cho baseline/LR; có nhãn lớp dương và macro-F1 đúng. |
| Cuối D12 | TV1, TV2 → TV3 | Hướng dẫn chạy, phần viết, artifact | Đủ để người khác dựng sạch và hoàn thiện hồ sơ. |
| D13–D15 | Cả nhóm | Gói nghiệm thu | Lỗi chặn đã sửa, review và bằng chứng được ghi nhận. |

TV3 có thể dựng UI bằng fixture từ D3; không cần chờ toàn bộ ML. TV1 hỗ trợ TV2 benchmark/phân vùng và TV3 hỗ trợ đối soát để tránh dồn tải lên TV2.

## 5. Checklist mốc chung của nhóm

- [ ] **M1 — Cuối D5:** NiFi → HDFS → Spark silver/gold → dashboard tối thiểu chạy bằng dữ liệu thật.
- [ ] **M2 — Cuối D7:** gói tiến độ gồm đề cương, lý thuyết, kiến trúc, kết quả sơ bộ, demo, đóng góp tuần 1.
- [ ] **M3 — Cuối D9:** chốt mô hình, baseline/test metrics, kiểm tra rò rỉ và phân tích lỗi.
- [ ] **M4 — Cuối D11:** dashboard hoàn chỉnh, pipeline ổn định, benchmark và đối soát đạt.
- [ ] **M5 — Cuối D12:** ứng viên bàn giao có source/config, README, Word/PPT và artifact cần thiết.
- [ ] **M6 — Cuối D15:** kiểm chứng V1–V10 trong Plan.md, hoàn thiện bài nộp và lưu bằng chứng.

Các mốc trên là nội bộ. Hạn nộp/thuyết trình do GV xác nhận vẫn là mốc chính thức.

## 6. Kiểm chứng và điều kiện đóng công việc

- [ ] **Chấp thuận/quy định:** nhóm 3 người, đề tài và lịch báo cáo đã được xác nhận; hồ sơ đúng yêu cầu môn học.
- [ ] **Kiến trúc:** domain/application độc lập framework; adapter nằm đúng lớp; entry point ghép dependency qua bootstrap; UI không chạy ETL.
- [ ] **Dữ liệu:** CSV lỗi/thiếu/trùng được xử lý và đếm; manifest/schema/run_id rõ; replay không nhân đôi review duy nhất.
- [ ] **Phân tán:** có bằng chứng DataNode/replication và Spark executor/task; ghi đúng cụm container một máy hay nhiều máy.
- [ ] **Mô hình:** baseline và LR cùng test, không rò rỉ, metrics từng lớp và hạn chế có giải thích; không báo kết quả chưa chạy.
- [ ] **Dashboard:** ít nhất 6 biểu đồ/4 trang, filter đúng, dữ liệu rỗng không gây lỗi; KPI khớp gold và cùng run_id.
- [ ] **Tái lập:** thành viên không viết thành phần đó chạy được theo README, có artifact và dữ liệu mẫu cần thiết.
- [ ] **Hồ sơ:** source/config, Word, PPT, demo, liên kết dataset, hướng dẫn và đóng góp đầy đủ; không để bí mật trong gói.
- [ ] **Phối hợp:** mỗi nhiệm vụ có bằng chứng và review; giờ/tỷ lệ đóng góp là số thực tế, tổng tỷ lệ cuối bằng 100%.
- [ ] **Nộp bài:** đúng lịch GV, quyền truy cập hợp lệ, tệp mở/tải lại được, có bản sao và bằng chứng nộp.
