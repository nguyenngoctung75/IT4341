# Kế hoạch Xây dựng Hệ thống Hỗ trợ Ra quyết định (DSS) - Tìm địa điểm mở cửa hàng tiện lợi

## 1. Giới thiệu
Tài liệu này mô tả kế hoạch xây dựng hệ thống hỗ trợ ra quyết định (Decision Support System - DSS) để lựa chọn địa điểm tối ưu cho việc mở cửa hàng tiện lợi. Kế hoạch được xây dựng dựa trên cơ sở lý thuyết từ các tài liệu "Hệ trợ giúp quyết định" (Chương 3, 4, 12) và dữ liệu thực tế từ cơ sở dữ liệu `convenience_store_db`.

## 2. Định nghĩa Bài toán
Bài toán thuộc lớp **Ra quyết định đa thuộc tính (Multi-Attribute Decision Making - MADM)**.
- **Mục tiêu**: Xếp hạng và lựa chọn các địa điểm thuê (rental shops) tốt nhất từ một tập hợp các ứng viên.
- **Bối cảnh**: Người ra quyết định cần cân nhắc nhiều yếu tố mâu thuẫn nhau (ví dụ: chi phí thuê thấp nhưng diện tích phải rộng, vị trí đẹp nhưng tránh cạnh tranh).

## 3. Các Định nghĩa và Biến số

### 3.1. Biến Quyết định (Decision Variables) - $CV$
Trong bài toán lựa chọn địa điểm (Selection Problem), biến quyết định là:
- **Phương án lựa chọn ($A_i$)**: Mỗi địa điểm cho thuê (`rental_shops`) là một phương án.
- **Tập phương án**: $A = \{A_1, A_2, ..., A_n\}$ với $n$ là số lượng cửa hàng trong bảng `rental_shops`.

### 3.2. Biến Môi trường (Environment Variables) - $UV$
Là các yếu tố ảnh hưởng đến kết quả nhưng người ra quyết định không thể kiểm soát trực tiếp từng giá trị đơn lẻ mà chỉ có thể lựa chọn dựa trên chúng:
- **Giá thuê thị trường**: Phản ánh qua `price`.
- **Mật độ dân số/Lưu lượng khách**: Phản ánh qua `ward_demographics` và `foot_traffic`.
- **Vị trí đối thủ cạnh tranh**: Phản ánh qua bảng `opponent_stores`.
- **Chi phí vận hành**: Phản ánh qua `employee_cost`, `utilities_cost`.

### 3.3. Input (Dữ liệu đầu vào)
Dữ liệu được lấy từ `convenience_store_db`:

1.  **Danh sách Ứng viên (Alternative Set)**:
    - Nguồn: Bảng `rental_shops`.
    - Dữ liệu: ID, Địa chỉ.

2.  **Các Tiêu chí Đánh giá (Criteria)** - $C_j$:
    Được xây dựng từ các bảng `rental_shops`, `other_factors`, `shop_opponent_distances`.

    | Tiêu chí ($C_j$) | Mô tả | Nguồn dữ liệu | Loại tiêu chí | Mục tiêu |
    | :--- | :--- | :--- | :--- | :--- |
    | $C_1$: Giá thuê | Chi phí thuê hàng tháng | `rental_shops.price` | Chi phí (Cost) | Min |
    | $C_2$: Diện tích | Diện tích mặt bằng ($m^2$) | `rental_shops.area` | Lợi ích (Benefit) | Max |
    | $C_3$: Mặt tiền | Độ rộng mặt tiền (m) | `rental_shops.frontage` | Lợi ích (Benefit) | Max |
    | $C_4$: Lưu lượng khách | Mức độ đông đúc | `other_factors.foot_traffic` | Lợi ích (Benefit) | Max |
    | $C_5$: Chi phí nhân viên | Lương nhân viên dự kiến | `other_factors.employee_cost` | Chi phí (Cost) | Min |
    | $C_6$: Chi phí điện nước | Tiền điện nước dự kiến | `other_factors.utilities_cost` | Chi phí (Cost) | Min |
    | $C_7$: Khoảng cách đối thủ | Khoảng cách đến đối thủ gần nhất | `shop_opponent_distances` (Min aggregation) | Lợi ích (Benefit) | Max (*) |

    *(*) Giả định chiến lược là tránh xa đối thủ cạnh tranh trực tiếp để khai thác thị trường mới.*

3.  **Trọng số (Weights) - $w_j$**:
    - Độ quan trọng của từng tiêu chí (ví dụ: Giá thuê quan trọng hơn Diện tích).
    - Tổng trọng số $\sum w_j = 1$.
    - Có thể được xác định bởi người dùng hoặc dùng phương pháp AHP (Chương 3).

### 3.4. Output (Đầu ra)
- **Bảng xếp hạng**: Danh sách các cửa hàng sắp xếp theo độ ưu tiên giảm dần.
- **Điểm số ($Score$)**: Giá trị định lượng ($0 \le S \le 1$) thể hiện độ tốt của từng địa điểm.
- **Khuyến nghị**: Top $k$ địa điểm tốt nhất nên thuê.

## 4. Mô hình và Thuật toán: TOPSIS
Dựa trên tài liệu "Chuơng 3 - Mô hình hóa và các mô hình định lượng", phương pháp **TOPSIS** (Technique for Order Preference by Similarity to Ideal Solution) được lựa chọn vì phù hợp với bài toán xếp hạng có nhiều tiêu chí định lượng.

### Quy trình Thuật toán:

**Bước 1: Xây dựng Ma trận Quyết định (Decision Matrix)**
- Tạo ma trận $X$ kích thước $n \times m$ ($n$ cửa hàng, $m$ tiêu chí).
- $x_{ij}$ là giá trị của tiêu chí $j$ tại cửa hàng $i$.
- *Lưu ý*: Với tiêu chí "Khoảng cách đối thủ", cần truy vấn `shop_opponent_distances` để tìm khoảng cách nhỏ nhất (`MIN(distance_km)`) cho mỗi `shop_id`.

**Bước 2: Chuẩn hóa Ma trận (Normalization)**
Chuyển đổi các đơn vị đo khác nhau (VND, $m^2$, mét, km) về cùng một miền giá trị vector đơn vị để so sánh.
$$r_{ij} = \frac{x_{ij}}{\sqrt{\sum_{k=1}^n x_{kj}^2}}$$

**Bước 3: Tính Ma trận Chuẩn hóa có Trọng số**
Nhân ma trận chuẩn hóa với trọng số $w_j$ của từng tiêu chí.
$$v_{ij} = w_j \times r_{ij}$$

**Bước 4: Xác định Giải pháp Lý tưởng (Ideal Solutions)**
- **Giải pháp Lý tưởng Tốt nhất ($A^*$):** Tập hợp các giá trị tốt nhất của mỗi tiêu chí (Max của Lợi ích, Min của Chi phí).
  $$A^* = \{v_1^*, v_2^*, ..., v_m^*\}$$
- **Giải pháp Lý tưởng Tệ nhất ($A^-$):** Tập hợp các giá trị tệ nhất của mỗi tiêu chí (Min của Lợi ích, Max của Chi phí).
  $$A^- = \{v_1^-, v_2^-, ..., v_m^-\}$$

**Bước 5: Tính khoảng cách Euclidean**
Tính khoảng cách từ mỗi phương án $i$ đến $A^*$ và $A^-$.
- Khoảng cách đến tốt nhất: $S_i^* = \sqrt{\sum_{j=1}^m (v_{ij} - v_j^*)^2}$
- Khoảng cách đến tệ nhất: $S_i^- = \sqrt{\sum_{j=1}^m (v_{ij} - v_j^-)^2}$

**Bước 6: Tính độ tương tự (Similarity Score)**
$$C_i^* = \frac{S_i^-}{S_i^* + S_i^-}$$
- $0 \le C_i^* \le 1$.
- $C_i^*$ càng gần 1 thì phương án càng tốt.

**Bước 7: Xếp hạng**
Sắp xếp các cửa hàng theo $C_i^*$ giảm dần và đưa ra kết quả.

## 5. Tổ chức Dữ liệu (Dựa trên Schema)
Mối quan hệ giữa các bảng trong thuật toán:
```sql
SELECT
    r.id AS shop_id,
    r.price,                 -- C1
    r.area,                  -- C2
    r.frontage,              -- C3
    o.foot_traffic,          -- C4
    o.employee_cost,         -- C5
    o.utilities_cost,        -- C6
    MIN(sod.distance_km) AS min_opponent_dist -- C7
FROM rental_shops r
JOIN other_factors o ON r.id = o.rental_shop_id
LEFT JOIN shop_opponent_distances sod ON r.id = sod.shop_id
GROUP BY r.id;
```
