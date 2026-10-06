# VNU-MOOC — trang giới thiệu

Bản gốc soạn thảo của trang giới thiệu VNU-MOOC: một trang tĩnh `index.html`, CSS/JS/ảnh/logo trong `assets/about/`. Đường dẫn tài nguyên đều tương đối, mở thẳng `index.html` là xem được.

Trang đang chạy thật ở `https://mooc.ctlt.tech/clients` (khách chưa đăng nhập) là **bản chuyển sang Liquid** trên theme của Cohota, không tự đồng bộ với repo này.

## Cập nhật lên trang thật

Hướng dẫn đầy đủ nằm ở repo `vnumooc-canvas`, file `docs/GIAO_DIEN_TRANG_CHU.md`. Tóm tắt:

1. Đăng nhập `mooc.ctlt.tech` bằng admin → tài khoản VNUHCM → **"Trình chỉnh sửa giao diện khách hàng"** (`/accounts/5/client_theme_editor`). Trang mở Cohota Code Editor (VS Code bản web), workspace `2 [Client Workspace]`. Token API không dùng được.
2. File tương ứng:

   | Repo này | Theme Cohota |
   |---|---|
   | `index.html` | `snippets/_about_landing.liquid` |
   | `assets/about/*` | `assets/about/*` (cùng tên) |

3. **Không dán đè nguyên `index.html`.** Snippet đã khác bản gốc:
   - song ngữ `{% if ui_lang == 'en' %}…{% else %}…{% endif %}`; sửa chữ phải viết cả bản tiếng Anh;
   - không có `<head>`, ẩn header/footer của theme (`.k12-hdr`, `.k12-ft`);
   - Open Sans + Be Vietnam Pro tự host trong theme, chỉ nạp Patrick Hand từ Google Fonts;
   - ảnh/CSS/JS đi qua filter `asset_url`, không dùng đường dẫn tương đối.
4. Trước khi lưu, chép nội dung snippet hiện tại sang `state/rollback/giao_dien/_about_landing_<YYYYMMDD>.liquid` ở repo `vnumooc-canvas`.
5. Chỉ chuyển đúng đoạn đã đổi, Cmd+S (lưu là trang thật đổi ngay), kiểm tra `/clients` trong cửa sổ ẩn danh, cả hai ngôn ngữ.
6. Commit thay đổi ở đây để bản gốc khớp trang thật.

Ô Search toàn workspace của editor không chạy; mở file rồi dùng Cmd+F.
