# VNU-MOOC — trang giới thiệu

Bản gốc soạn thảo của trang giới thiệu VNU-MOOC: trang tĩnh `index.html` (tiếng Việt) và `en/index.html` (tiếng Anh), CSS/JS/ảnh/logo dùng chung trong `assets/about/`. Đường dẫn tài nguyên đều tương đối, mở thẳng file là xem được; nút chọn ngôn ngữ ở góc phải chuyển qua lại giữa hai file.

Trang đang chạy thật ở `https://mooc.vnuhcm.edu.vn/clients` (khách chưa đăng nhập) là **bản chuyển sang Liquid** trên theme của Cohota, không tự đồng bộ với repo này.

## Cập nhật lên trang thật

Hướng dẫn đầy đủ nằm ở repo `vnumooc-canvas`, file `docs/GIAO_DIEN_TRANG_CHU.md`. Tóm tắt:

1. Đăng nhập `mooc.vnuhcm.edu.vn` bằng admin → tài khoản VNUHCM → **"Trình chỉnh sửa giao diện khách hàng"** (`/accounts/5/client_theme_editor`). Trang mở Cohota Code Editor (VS Code bản web), workspace `2 [Client Workspace]`. Token API không dùng được.
2. File tương ứng:

   | Repo này | Theme Cohota |
   |---|---|
   | `index.html` (VI) + `en/index.html` (EN) | `snippets/_about_landing.liquid` (một file, hai ngôn ngữ) |
   | `assets/about/*` | `assets/about/*` (cùng tên) |

3. **Không dán đè nguyên `index.html`.** Snippet đã khác bản gốc:
   - song ngữ `{% if ui_lang == 'en' %}…{% else %}…{% endif %}` (`ui_lang` lấy từ `'about._locale' | translate`); chữ tiếng Việt lấy ở `index.html`, chữ tiếng Anh ở `en/index.html`. Sửa chữ thì sửa cả hai file;
   - nút chọn ngôn ngữ trên theme trỏ `?locale=vi` / `?locale=en` (máy chủ ghi cookie `client_locale`), ở đây trỏ sang file kia;
   - không có `<head>`, ẩn header/footer của theme (`.k12-hdr`, `.k12-ft`);
   - Open Sans + Be Vietnam Pro tự host trong theme, chỉ nạp Patrick Hand từ Google Fonts;
   - ảnh/CSS/JS đi qua filter `asset_url`, không dùng đường dẫn tương đối.
4. Trước khi lưu, chép nội dung snippet hiện tại sang `state/rollback/giao_dien/_about_landing_<YYYYMMDD>.liquid` ở repo `vnumooc-canvas`.
5. Chỉ chuyển đúng đoạn đã đổi, Cmd+S (lưu là trang thật đổi ngay), kiểm tra `/clients` trong cửa sổ ẩn danh, cả hai ngôn ngữ.
6. Commit thay đổi ở đây để bản gốc khớp trang thật.

`en/index.html` dựng ngày 20/10/2026 từ bản tiếng Anh đang chạy trên `/clients?locale=en`; phần CSS/JS và bản tiếng Việt cũng đã khớp trang thật ngày đó.

**27/10/2026: bản gốc đi trước trang thật.** Đã sửa theo góp ý "Chỉnh sửa giao diện VNU-MOOC" (Google Docs, chữ xanh là mục mới) nhưng chưa đưa lên theme. Khi chuyển sang snippet:

- HTML đổi gần như mọi mục: mục Con số có khung danh mục 33 môn (`.numbers-grid`, `.catalog`), Đội ngũ đổi sang 4 nhóm đội ngũ + quy trình 3 bước (`.build-flow`, thay `.production-flow`), hàng 9 đơn vị thành viên (`.member-grid-main`) và đơn vị trực thuộc PTNK + VIH, Đồng hành bỏ đánh số bước (`.journey-grid`, thay `.timeline`), CTA bỏ ba ô tắt.
- CSS: thêm khối cuối `about.css`, sửa nhiều chỗ trong `notebook.css` (màu nền nhạt từng mục, ô số liệu màu, giảm khoảng cách). Đưa CSS và snippet lên **cùng lúc**, vì `.stats`/`.stat` đổi kiểu.
- JS: `about.js` nhận `data-format="en"` (in "5,000").
- Tài sản mới: `logos/ier-mark.svg`, `logos/vih.svg` (PNG nhúng base64 trong SVG, giống `ier.svg`).
- Danh mục môn trong mục Con số chép tay từ `data/ma_mon_2026S1.tsv` của `vnumooc-canvas` (38 dòng trừ 5 môn bổ sung 28/09); đổi danh sách môn thì sửa cả hai file HTML.

Ô Search toàn workspace của editor không chạy; mở file rồi dùng Cmd+F.
