# Dữ liệu

Thư mục này không đưa lên GitHub (trừ file này). Mỗi thành viên tự tải dữ liệu về máy mình.

## 1. Tải dữ liệu

1. Đăng nhập Kaggle, mở dataset **`grouplens/movielens-20m-dataset`**
   (https://www.kaggle.com/datasets/grouplens/movielens-20m-dataset) và tải file `archive.zip`.
2. Giải nén vào `data/ml-20m/`. Sau khi giải nén phải có (tên file **số ít**):

   ```
   data/ml-20m/
   ├── rating.csv   (~690 MB, 20.000.263 dòng)
   ├── movie.csv    (27.278 dòng)
   └── tag.csv      (465.564 dòng)
   ```

   Các file khác trong archive (`link.csv`, `genome_*.csv`) không dùng, có thể bỏ.

> **Lưu ý:** không dùng bản tải từ grouplens.org. Bản đó có tên file khác (`ratings.csv`, `movies.csv`, …)
> và cột `timestamp` lưu dạng số giây, không khớp với code của nhóm.

## 2. Tạo Parquet

Khởi động container (`docker compose up -d`), mở Jupyter tại http://localhost:8889 (token `bigdata`)
và chạy hết notebook `notebooks/00_chuan_bi_du_lieu.ipynb` **một lần**. Notebook tạo:

```
data/ml-20m-parquet/
├── full/{rating,movie,tag}     <- toàn bộ dữ liệu
└── sample/{rating,movie,tag}   <- 5% rating (seed 42), movie và tag giữ nguyên
```

Các notebook 01–03 đọc dữ liệu từ thư mục Parquet này.
