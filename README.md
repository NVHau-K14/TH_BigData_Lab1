# Lab 1 – Apache Spark và xử lý dữ liệu bằng PySpark

Bài lab nhóm môn **Thực hành Nhập môn Big Data**. Dữ liệu: **MovieLens 20M** (20 triệu lượt đánh giá phim).

| Thành viên | MSSV | Phần việc |
|---|---|---|
| A – Nguyễn Văn Hậu | 2001230225 | Môi trường, khảo sát dữ liệu, notebook 00 và 01, ghép báo cáo |
| B – Nguyễn Đắc Pin | 2033230213 | Spark DataFrame, notebook 02 |
| C – Nguyễn Thị Yến Vy | 2001231068 | RDD, notebook 03, kết luận |

## 1. Yêu cầu

- Windows 10/11 + **Docker Desktop** (bật WSL2). Không cần cài Python, Java, Spark trên Windows: mọi thứ chạy trong container.
- RAM: khuyến nghị **16 GB** (máy 8 GB vẫn chạy được, xem mục 5).
- Ổ đĩa: khoảng **7 GB** cho Docker image, khoảng **1 GB** cho dữ liệu (CSV + Parquet).

## 2. Cài đặt (làm một lần)

1. **Clone repo**
   ```bash
   git clone https://github.com/NVHau-K14/TH_BigData_Lab1.git
   cd TH_BigData_Lab1
   ```
2. **Tải dữ liệu:** trên Kaggle tải dataset `grouplens/movielens-20m-dataset`, giải nén `rating.csv`, `movie.csv`,
   `tag.csv` vào `data/ml-20m/`. Chi tiết xem [data/README.md](data/README.md).
3. **Khởi động container** (lần đầu sẽ tải image, mất vài phút):
   ```bash
   docker compose up -d
   ```
4. **Mở Jupyter:** http://localhost:8889, token `bigdata`. Hoặc trong VS Code: mở notebook → *Select Kernel* →
   *Existing Jupyter Server* → nhập `http://localhost:8889/?token=bigdata`.
5. **Tạo Parquet:** chạy hết `notebooks/00_chuan_bi_du_lieu.ipynb` **một lần** (khoảng 1 phút). Các notebook khác đọc
   dữ liệu từ `data/ml-20m-parquet/`.

Spark UI (khi đang chạy Spark): http://localhost:4041. Làm xong: `docker compose down` (file không mất).

## 3. Chạy notebook từ dòng lệnh

```bash
docker exec TH_BigData_Lab1 jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 /home/jovyan/work/notebooks/<ten>.ipynb
```

Kết quả được ghi luôn vào file `.ipynb`; mở bằng VS Code hoặc Jupyter để xem.

## 4. Cấu trúc thư mục

```
TH_BigData_Lab1/
├── docker-compose.yml        cấu hình container (image Spark 4.2.0, cổng 8889/4041)
├── data/                     dữ liệu, KHÔNG đưa lên GitHub (trừ data/README.md)
│   ├── ml-20m/               CSV gốc từ Kaggle
│   └── ml-20m-parquet/       Parquet do notebook 00 tạo: full/ và sample/
├── notebooks/
│   ├── 00_chuan_bi_du_lieu.ipynb     (A) chuyển CSV sang Parquet, ai cũng chạy một lần
│   ├── 01_moi_truong_khao_sat.ipynb  (A) môi trường, khảo sát dữ liệu bằng Pandas và PySpark
│   ├── 02_dataframe.ipynb            (B) thao tác với Spark DataFrame
│   └── 03_rdd.ipynb                  (C) thao tác với RDD
├── results/                  CSV kết quả nhỏ để đối chiếu giữa các thành viên
├── report/images/            ảnh kết quả cho báo cáo, chia theo số notebook
├── tools/render_outputs.py   xuất output của notebook thành ảnh PNG
└── docs/                     kế hoạch thực hiện
```

## 5. Quy ước chung

- Đầu mọi notebook là **cell khởi tạo chung** (tạo `spark`, `sc`, các biến `SIZE`, `CSV`, `DATA`). Chỉ được đổi `SIZE`
  và hai dòng cấu hình bộ nhớ; không đổi tên biến, đường dẫn, tên cột.
- `SIZE = "sample"` (5% dữ liệu, chạy nhanh) khi viết code; đổi thành `SIZE = "full"` khi chạy lấy số liệu cuối.
- Máy RAM **8 GB**: đổi `.master("local[*]")` thành `.master("local[2]")` và `spark.driver.memory` thành `"2g"`.
- **Chỉ sửa notebook của mình.** Notebook phải chạy được từ đầu đến cuối (Restart & Run All).
- Kết quả dùng để đối chiếu giữa B và C ghi vào `results/genre_count_B.csv` và `results/genre_count_C.csv`.

## 6. Lưu ý

- Ai đã tạo container từ trước: sau khi `git pull` hãy chạy lại `docker compose up -d`, vì `docker-compose.yml` đã thêm
  biến `PYTHONPATH` (cần để chạy notebook bằng lệnh ở mục 3).
- Xuất ảnh kết quả cho báo cáo: đặt dòng đầu của cell là `# ANH: <mã> | <chú thích>` (vd `# ANH: 02_03 | Top 10 phim`),
  chạy notebook, rồi:
  ```bash
  docker exec TH_BigData_Lab1 python /home/jovyan/work/tools/render_outputs.py /home/jovyan/work/notebooks/<ten>.ipynb
  ```
  Ảnh được lưu vào `report/images/<số notebook>/<mã>.png`, kèm danh sách `danh_sach_anh.md`.

## 7. Lỗi thường gặp

| Lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| `port is already allocated` (8889 hoặc 4041) | Cổng đang bị chương trình/container khác dùng | Tắt chương trình đó, hoặc đổi cổng bên trái trong `docker-compose.yml` (vd `"8890:8888"`) |
| `error during connect` / `cannot find the file specified` | Docker Desktop chưa chạy hoặc WSL2 chưa bật | Mở Docker Desktop, chờ trạng thái *Engine running*; nếu cần chạy `wsl --install` rồi khởi động lại máy |
| `[PATH_NOT_FOUND] Path does not exist: .../data/ml-20m/rating.csv` | Giải nén sai chỗ (thừa thư mục con) hoặc sai tên file | Kiểm tra có đúng `data/ml-20m/rating.csv` (tên số ít) |
| `Path does not exist: .../ml-20m-parquet/...` | Chưa chạy notebook 00 | Chạy `00_chuan_bi_du_lieu.ipynb` một lần |
| `OutOfMemoryError` / kernel bị khởi động lại | Thiếu RAM | Dùng `SIZE = "sample"`, `local[2]`, `spark.driver.memory 2g`; tăng RAM cho WSL2 (`memory=` trong `%UserProfile%\.wslconfig`, rồi `wsl --shutdown`) |
