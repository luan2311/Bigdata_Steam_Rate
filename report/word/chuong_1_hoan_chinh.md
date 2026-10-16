# CHƯƠNG 1: GIỚI THIỆU VÀ BÀI TOÁN

---

## 1.1. Bối cảnh và Tính cấp thiết của đề tài

Trong kỷ nguyên kinh tế số và sự bùng nổ của ngành công nghiệp giải trí tương tác, trò chơi điện tử (video games) đã vươn lên trở thành một trong những ngành công nghiệp có quy mô doanh thu và tốc độ tăng trưởng hàng đầu thế giới, vượt qua cả điện ảnh và âm nhạc cộng lại. Đứng ở trung tâm của hệ sinh thái phân phối trò chơi toàn cầu trên nền tảng máy tính cá nhân (PC) là **Steam** – nền tảng phát hành kỹ thuật số do Valve Corporation phát triển và vận hành. Với hàng chục nghìn tựa game đa dạng cùng hàng trăm triệu người dùng hoạt động tích cực mỗi tháng trên khắp thế giới, Steam không chỉ đơn thuần là một kênh thương mại điện tử phân phối phần mềm, mà còn là một không gian mạng xã hội tương tác quy mô lớn. 

Tại Steam, tính năng **Đánh giá của người dùng (User Reviews)** đóng vai trò là chiếc cầu nối thông tin trực tiếp, minh bạch và quan trọng nhất giữa cộng đồng người chơi và các nhà phát triển/phát hành game. Khác biệt với các hệ thống chấm điểm thang 5 sao truyền thống, cơ chế đánh giá của Steam yêu cầu người viết đưa ra quyết định nhị phân dứt khoát: **Khuyến nghị (Recommended - Vote Positive)** hoặc **Không khuyến nghị (Not Recommended - Vote Negative)**, kèm theo một bài viết nhận xét tự do (Review Text) trình bày lý do, trải nghiệm, ưu và nhược điểm của trò chơi. Tỷ lệ phần trăm đánh giá tích cực tổng hợp trên Steam là thước đo sống còn trực tiếp chi phối quyết định mua hàng của người tiêu dùng mới, đồng thời ảnh hưởng sâu sắc đến thuật toán đề xuất hiển thị trò chơi trên toàn bộ hệ thống.

Tuy nhiên, việc khai thác và thấu hiểu khối lượng dữ liệu phản hồi khổng lồ này đặt ra những thách thức công nghệ rất lớn, mang đầy đủ các đặc trưng kinh điển của bài toán **Dữ liệu lớn (Big Data)**:
1. **Dung lượng và quy mô cực lớn (Volume):** Số lượng đánh giá tích lũy trên toàn hệ thống Steam đã vượt qua con số hàng trăm triệu bản ghi. Ngay cả một tập mẫu trích xuất đại diện (như *Steam Reviews Dataset 2021* được sử dụng trong đồ án) đã lên tới hơn 21 triệu dòng dữ liệu thô với dung lượng tệp vượt quá 8 Gigabyte, khiến các công cụ xử lý đơn luồng hoặc các hệ quản trị cơ sở dữ liệu quan hệ truyền thống trên một máy đơn lập tức gặp sự cố tràn bộ nhớ (Out-Of-Memory) hoặc thời gian xử lý kéo dài không thể chấp nhận.
2. **Tốc độ sinh dữ liệu và biến động liên tục (Velocity):** Đánh giá được gửi lên liên tục theo thời gian thực, đặc biệt bùng nổ vào các đợt phát hành phiên bản cập nhật (Patch/DLC), các mùa giảm giá định kỳ (Steam Sales) hoặc những sự kiện khủng hoảng truyền thông trong cộng đồng game thủ (Review Bombing). Việc phân tích đòi hỏi các công nghệ có khả năng xử lý theo lô lớn (Batch Processing) linh hoạt và hỗ trợ mở rộng luồng tiếp nhận.
3. **Tính đa dạng và phi cấu trúc (Variety):** Dữ liệu thu thập là sự kết hợp phức tạp giữa các trường thuộc tính có cấu trúc (ID trò chơi, thời gian tạo, thời gian chơi thực tế bằng phút, số lượt bình chọn hữu ích) và trường văn bản hoàn toàn phi cấu trúc (`review_text`). Văn bản của game thủ thường chứa đựng ngôn ngữ mạng tự do, tiếng lóng, biểu tượng cảm xúc, ngôn ngữ mỉa mai/châm biếm, viết hoa không theo quy tắc và đặc biệt là hiện tượng xuống dòng ngẫu nhiên ngay trong nội dung đánh giá – điều này dễ dàng làm phá vỡ các trình phân tích cú pháp (parser) CSV thông thường nếu không được thiết kế chuyên biệt.
4. **Vấn đề chất lượng và độ nhiễu dữ liệu (Veracity):** Trong thực tế, dữ liệu tồn tại một lượng lớn các bản ghi trùng lặp do cơ chế chỉnh sửa đánh giá, các bản ghi khuyết thiếu ID, thiếu nội dung nhận xét hoặc sai lệch định dạng mốc thời gian. Ngoài ra, sự mâu thuẫn giữa nội dung khen ngợi bề ngoài nhưng lại bấm nhãn không khuyến nghị (hoặc ngược lại) đòi hỏi quy trình tiền xử lý, kiểm soát chất lượng và lọc dữ liệu phải được tổ chức khoa học, minh bạch và chặt chẽ.

Từ những thách thức công nghệ và yêu cầu thực tiễn nêu trên, việc nghiên cứu và ứng dụng một hệ sinh thái công nghệ dữ liệu lớn phân tán hiện đại (gồm Apache NiFi, Hadoop HDFS, Apache Spark và Streamlit) để xây dựng một quy trình xử lý, phân tích thống kê và dự đoán hành vi khuyến nghị của game thủ là đề tài có **tính cấp thiết rất cao**, mang ý nghĩa thực tiễn to lớn cả về mặt công nghệ lẫn giá trị ứng dụng kinh doanh.

---

## 1.2. Mục tiêu nghiên cứu của đề tài

Đồ án tập trung vào việc nghiên cứu, thiết kế và hiện thực hóa một hệ thống toàn diện có khả năng xử lý dữ liệu lớn theo chu trình khép kín, từ khâu tiếp nhận thô ban đầu đến sản phẩm ứng dụng đầu cuối. Cụ thể, các mục tiêu cốt lõi của đề tài bao gồm:

1. **Xây dựng Pipeline xử lý dữ liệu lớn phân tán, tự động và có khả năng chạy lại (Reproducible Data Pipeline):**
   * Hiện thực hóa giải pháp thu thập, kiểm tra cấu trúc, chia lô (batching) và vận chuyển dữ liệu an toàn vào hệ thống lưu trữ phân tán Hadoop HDFS thông qua nền tảng điều phối Apache NiFi.
   * Xây dựng quy trình làm sạch dữ liệu, xử lý các bản ghi khuyết thiếu/bất thường, cơ chế khử trùng lặp đa phiên bản (Deduplication) và tối ưu hóa định dạng lưu trữ phân tích dạng cột (Parquet Partitioning) dựa trên nền tảng tính toán phân tán Apache Spark.
2. **Khai phá dữ liệu và trực quan hóa phân tích đa chiều (Exploratory Data Analysis & Interactive Dashboard):**
   * Phát triển ứng dụng Web Dashboard đa màn hình bằng Streamlit và Plotly, tuân thủ nguyên tắc kiến trúc phần mềm sạch (Clean Architecture).
   * Cung cấp các công cụ tương tác thời gian thực, lọc và trực quan hóa số liệu phân tích thống kê chuyên sâu về xu hướng thị trường, giúp nhà phát triển game và người dùng có cái nhìn trực quan, chính xác nhất về dữ liệu quan sát được.
3. **Nghiên cứu và xây dựng Mô hình Học máy phân tán (Distributed Machine Learning Model):**
   * Ứng dụng thư viện Spark MLlib để xây dựng quy trình tiền xử lý ngôn ngữ tự nhiên (NLP) phân tán (Tokenization, Stopwords Removal, HashingTF, Inverse Document Frequency - IDF).
   * Huấn luyện mô hình phân loại nhị phân (Logistic Regression) trên tập dữ liệu quy mô lớn nhằm dự đoán nhãn hành vi khuyến nghị của người chơi dựa trên nội dung văn bản nhận xét tiếng Anh; tiến hành đánh giá khách quan so với mô hình cơ sở (Majority Baseline) và phân tích định tính các trường hợp dự đoán sai (Error Analysis).
4. **Kiểm chứng tính ổn định, đo lường hiệu năng và bảo đảm khả năng tái lập hệ thống:**
   * Triển khai toàn bộ hệ sinh thái dịch vụ trên nền tảng ảo hóa Docker Compose (mô phỏng cụm nhiều nút gồm NameNode, nhiều DataNode, Spark Master và nhiều Spark Worker).
   * Đo đạc hiệu năng (Benchmark) cụm phân tán và thực hiện kiểm thử độc lập đối soát số liệu (Audit Check) nhằm đảm bảo hệ thống vận hành ổn định, dữ liệu không bị sai lệch và mọi kết quả thực nghiệm đều có thể tái tạo từ mã nguồn.

---

## 1.3. Năm câu hỏi phân tích cốt lõi (Core Research Questions)

Để định hướng xuyên suốt cho các khâu từ thiết kế luồng dữ liệu, xây dựng bảng tổng hợp đến trực quan hóa giao diện và huấn luyện học máy, nhóm nghiên cứu đã xác định và giải quyết triệt để **5 câu hỏi phân tích trọng tâm** sau:

### Câu hỏi 1: Những trò chơi nào sở hữu lượng đánh giá cao và tỷ lệ người chơi khuyến nghị tích cực nhất hoặc tiêu cực nhất?
* **Ý nghĩa thực tiễn:** Giúp xác định các tựa game thành công vượt bậc (được cộng đồng đánh giá rất cao) và các tựa game gây thất vọng lớn trên thị trường, làm bài học kinh nghiệm cho các nhà sản xuất.
* **Yêu cầu kỹ thuật:** Tỷ lệ khuyến nghị phải luôn được trình bày gắn liền với quy mô mẫu số (tổng số lượng đánh giá hợp lệ). Để tránh sai lệch thống kê do hiện tượng các trò chơi chỉ có vài lượt đánh giá nhưng đạt tỷ lệ 100%, hệ thống phải thiết lập **ngưỡng lọc số lượng tối thiểu tin cậy (mặc định $\ge 100$ reviews)** trước khi đưa vào bảng xếp hạng.

### Câu hỏi 2: Số lượng đánh giá và mức độ hài lòng của cộng đồng biến động như thế nào theo các mốc thời gian (tháng UTC)?
* **Ý nghĩa thực tiễn:** Cho phép theo dõi vòng đời của trò chơi, đánh giá tác động của các sự kiện ra mắt bản cập nhật, sửa lỗi hay khủng hoảng truyền thông đến tâm lý game thủ theo dòng thời gian.
* **Yêu cầu kỹ thuật:** Trường thời gian tạo (`timestamp_created`) phải được chuẩn hóa đồng nhất về múi giờ quốc tế UTC và gom nhóm theo đơn vị Năm-Tháng (`YYYY-MM`). Các bản ghi sai lệch hoặc khuyết thiếu mốc thời gian phải được loại trừ riêng khỏi biểu đồ thời gian mà không làm mất tính toàn vẹn của bản ghi ở các phân tích khác.

### Câu hỏi 3: Phân bố của các cộng đồng ngôn ngữ và sự khác biệt về tỷ lệ khuyến nghị giữa các nhóm ngôn ngữ là gì?
* **Ý nghĩa thực tiễn:** Hỗ trợ các nhà phát hành đánh giá quy mô thị trường quốc tế và mức độ thành công của công tác bản địa hóa (Localization/Dịch thuật game). Một trò chơi có thể được cộng đồng nói tiếng Anh khen ngợi nhưng lại bị phản đối dữ dội ở các cộng đồng ngôn ngữ khác nếu khâu chuyển ngữ kém hoặc thiếu máy chủ khu vực.
* **Yêu cầu kỹ thuật:** Thống kê phân loại theo trường `language` đã chuẩn hóa; bảo tồn nhóm bản ghi chưa xác định ngôn ngữ dưới nhãn `unknown`; tuyệt đối không tự ý suy diễn từ mã ngôn ngữ thành quốc tịch người dùng nhằm đảm bảo tính chính xác khoa học.

### Câu hỏi 4: Thời gian chơi thực tế tại thời điểm đánh giá liên hệ như thế nào với quyết định khuyến nghị trò chơi?
* **Ý nghĩa thực tiễn:** Trả lời cho băn khoăn: Liệu người chơi dành hàng trăm giờ vào game có xu hướng khắt khe hơn hay ưu ái trò chơi hơn so với những người chỉ chơi thử trong vài giờ đầu? Kết quả này cung cấp chỉ dấu quan trọng về chiều sâu nội dung (End-game content) của các tựa game.
* **Yêu cầu kỹ thuật:** Thuộc tính thời gian chơi được chuyển đổi chính xác từ phút sang giờ và phân đoạn thành các khoảng giá trị rời rạc không chồng chéo nhau theo chuẩn: $[0, 2h)$, $[2h, 10h)$, $[10h, 50h)$, $[50h, 100h)$, $[100h, +\infty)$. Phân tích này được xác định rõ là **phân tích tương quan quan sát trên dữ liệu thực tế**, không diễn giải thành quan hệ nhân quả tuyệt đối.

### Câu hỏi 5: Mô hình học máy dựa trên nội dung bài viết tiếng Anh có khả năng dự đoán nhãn khuyến nghị tốt hơn mô hình cơ sở (Baseline) ở mức độ nào?
* **Ý nghĩa thực tiễn:** Khẳng định tiềm năng của việc ứng dụng xử lý ngôn ngữ tự nhiên phân tán để tự động phân loại, giám sát chất lượng và thấu hiểu phản hồi của khách hàng ở quy mô lớn thay vì đọc duyệt thủ công.
* **Yêu cầu kỹ thuật:** Sử dụng tập dữ liệu đánh giá tiếng Anh hợp lệ; phân chia tập huấn luyện/kiểm thử theo hàm băm văn bản (Hash-based Split) cố định seed để chống rò rỉ dữ liệu (Data Leakage); đánh giá hiệu năng khách quan thông qua các độ đo phù hợp với dữ liệu mất cân bằng nhãn như **Macro-F1**, Precision, Recall từng lớp, PR-AUC và Ma trận nhầm lẫn (Confusion Matrix).
