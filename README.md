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

**28/10/2026: đã lưu lên theme** bản sửa theo góp ý "Chỉnh sửa giao diện VNU-MOOC" (Google Docs, chữ xanh là mục mới) và bản tiếng Anh: assets lên CDN ngay, snippet `theme/_about_landing.liquid` đã lưu trên editor và **đã lên `/clients` lúc 00:38** (6 phút sau khi lưu), bản gốc ở repo này khớp trang thật. Rollback và nhật ký ở `docs/GIAO_DIEN_TRANG_CHU.md` của `vnumooc-canvas`. Những gì đã đổi so với bản 20/10:

- HTML đổi gần như mọi mục: mục Con số có danh mục 33 môn ở hàng riêng dưới ô số liệu (`.catalog`, `.cat-grid`), Đội ngũ đổi sang 4 nhóm đội ngũ + quy trình 3 bước (`.build-flow`, thay `.production-flow`), 9 đơn vị thành viên thành slideshow lặp vô tận, mỗi đơn vị một nút trên thanh điều hướng ở giữa, giống slideshow đầu trang (`.member-slider`, `.member-dots`, thẻ ngang `.member-row`) và đơn vị trực thuộc PTNK + VIH cùng cỡ thẻ (VIH: innovationhub.vnuhcm.edu.vn), Đồng hành bỏ đánh số bước (`.journey-grid`, thay `.timeline`), CTA bỏ ba ô tắt.
- CSS: thêm khối cuối `about.css`, sửa nhiều chỗ trong `notebook.css` (màu nền nhạt từng mục, ô số liệu màu, giảm khoảng cách). Đưa CSS và snippet lên **cùng lúc**, vì `.stats`/`.stat` đổi kiểu.
- JS: `about.js` nhận `data-format="en"` (in "5,000"); slideshow đơn vị thành viên: nhân đôi danh sách để nối vòng (sau ô cuối là ô đầu), mỗi 3 giây dịch một ô, vuốt ngang để chuyển, dừng khi rê chuột/focus, không tự chạy khi người dùng chọn giảm chuyển động; slideshow đầu trang chỉ chọn `.hero .scene-dot`.
- Tài sản mới: `logos/ier-mark.svg`, `logos/ptnk-mark.svg`, `logos/vih-mark.svg` (biểu trưng cắt bằng `viewBox` cho thẻ ngang), `logos/vih.svg` (PNG nhúng base64 trong SVG, giống `ier.svg`).
- Danh mục môn theo phong cách infographic Canva "[2.1] 33 môn MOOC" (nhãn trắng đè khối xanh đậm, không hình minh họa); nhóm, thứ tự và tên môn theo Canva, khớp `data/ma_mon_2026S1.tsv` của `vnumooc-canvas` (38 dòng trừ 5 môn bổ sung 28/09). Tiêu đề và nhãn nhóm dùng font **Oswald**: khi đưa lên theme phải thêm `family=Oswald:wght@500;600` vào link Google Fonts đang nạp Patrick Hand. Đổi danh sách môn thì sửa cả hai file HTML.

Ô Search toàn workspace của editor không chạy; mở file rồi dùng Cmd+F.

## Dựng snippet từ hai file HTML (`tools/`)

`theme/_about_landing.liquid` là bản snippet đang (hoặc sắp) chạy trên theme, dựng từ `index.html` + `en/index.html` của cùng commit. Lần sau sửa trang thì dựng lại bằng script, không sửa tay snippet:

1. Đọc snippet đang chạy trên editor ra một file, đối chiếu với `theme/_about_landing.liquid` (khác thì Cohota đã sửa, xem kỹ trước).
2. `python3 tools/build_snippet.py <snippet đang chạy> <index.html cũ> <en/index.html cũ> index.html en/index.html <bản mới>`: "cũ" là cặp HTML của commit đã dựng ra snippet đang chạy (`git show <commit>:index.html`). Script lấy phần đầu (`<style>`, font) từ bản đang chạy, trộn thân từ hai file HTML, rồi áp lại các chỉnh riêng cho theme (link `linklist`, `?locale=`, nhãn `translate`) rút ra từ chênh lệch giữa cặp HTML cũ và bản đang chạy. Script tự kiểm: dựng ngược mỗi ngôn ngữ phải khớp từng ký tự với file HTML.
3. Xem trước: `python3 tools/render_liquid.py <bản mới> vi|en <đường dẫn tới assets> out.html` (giả lập tối giản `asset_url`, `translate`, `linklist`, `if/else`).

**Ghi lên editor đừng dùng clipboard của máy** khi có phiên khác đang chạy: ngày 28/10/2026 clipboard bị ghi đè giữa lúc chép và dán, `about.css` trên editor thành một dòng chữ lạ (đã Cmd+Z kịp, CDN không đổi). Cách an toàn: đưa file lên GitHub Pages của repo này, trong trang editor `fetch` file đó, kiểm sha256, rồi dán bằng sự kiện `paste` giả lập (`DataTransfer`) vào vùng soạn thảo; đọc ngược bằng cách bắt sự kiện `copy` trong trang và so sha256 trước khi lưu.
