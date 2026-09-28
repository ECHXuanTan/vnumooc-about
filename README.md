# VNU-MOOC About

Trang giới thiệu tĩnh. Chạy tại thư mục này bằng `python3 -m http.server 8000`, rồi mở `http://localhost:8000/`.

## Dữ liệu giảng viên: nguồn gốc và seed

| File | Vai trò | Nguồn |
| --- | --- | --- |
| `../../eportfolio/data/giang_vien_mooc.json` | **Dữ liệu gốc** về tên, học hàm/học vị, chức vụ, trường, môn học và trưởng nhóm | Tổng hợp từ hồ sơ/quyết định nội bộ; xem `eportfolio/tao_json_giang_vien.py` ở repo VNUMOOC |
| `data/instructors.json` | Bản xuất cho danh bạ và hồ sơ web. `dot` ghi đợt đầu tiên của GV trong từng môn, `lead_mon` ghi các môn GV làm trưởng nhóm; **không phải dữ liệu crawl** | `python3 eportfolio/xuat_giang_vien_about.py` ở repo VNUMOOC; chạy lại sẽ ghi đè file này |
| `data/featured.json` | Mục "Giảng viên tiêu biểu" ở `giang-vien.html` và slideshow ở `index.html` (`assets/about/featured.js`): 6 người, thành tích biên tập tay kèm URL nguồn báo chí/trang trường, kiểm tra ngày 29/09/2026. `status: pending` hiện nhãn đang rà soát | Sửa tay; không có script sinh |
| `data/dot.json` | Sổ các đợt quyết định: ngày, số GV lần đầu tham gia, các môn lần đầu có tổ | Cùng lệnh xuất ở trên |
| `data/instructors_seed.json` | **Seed ứng viên từ Google**, chưa xác minh và chưa hiển thị; được Git bỏ qua | `scripts/crawl_instructors.py` dùng Google Search qua Serper, rồi đọc trang chính thức của trường |
| `data/instructors_profiles.json` | Bản seed đầy đủ 184 hồ sơ: 8 field gốc cùng 5 field bổ sung; trang chi tiết đọc file này | `scripts/crawl_instructors.py --publish-seed` xuất cả hồ sơ chờ duyệt; `--publish` chỉ xuất hồ sơ đã duyệt |
| `data/instructors_education_seed.json` | Seed timeline học vấn cho 184 hồ sơ; **không phải dữ liệu gốc**. 6 hồ sơ có mốc chép từ trang trường, 178 hồ sơ còn lại là mốc giao diện minh họa `20XX` | `scripts/seed_instructor_education.py`; mỗi hồ sơ ghi `status` và `source_url` |

Đường dẫn dữ liệu gốc tính từ **repo VNUMOOC** là `eportfolio/data/giang_vien_mooc.json`. `vnu-mooc-about` là repo riêng đặt trong `VNUMOOC/vnumooc/`; không tự đẩy thay đổi của hai repo cùng nhau. Google chỉ dùng để tìm nguồn. Tên, môn và vai trò MOOC vẫn lấy từ dữ liệu gốc; không suy đoán chúng từ kết quả tìm kiếm.

## Tạo seed

Từ thư mục này, cài `requests` và `beautifulsoup4` (đã có trong `requirements.txt` của repo VNUMOOC), rồi chạy:

```bash
python3 scripts/crawl_instructors.py --init
python3 scripts/crawl_instructors.py --limit 5
python3 scripts/crawl_instructors.py             # tiếp tục các hồ sơ chưa tìm
python3 scripts/crawl_instructors.py --name 'Lê Hoài Bắc' --refresh
python3 scripts/cache_instructor_photos.py        # lưu ảnh ứng viên từ trang trường
python3 scripts/crawl_instructors.py --publish-seed
python3 scripts/seed_instructor_education.py       # tạo timeline học vấn và mốc minh họa
```

Script đọc khóa từ biến môi trường `SERPER_API_KEY` trước, hoặc từ `../../config/serper_api_key.json` của repo VNUMOOC với dạng `{"api_key":"..."}`. File cấu hình này nằm ngoài thư mục web, được Git bỏ qua và nên có quyền đọc chỉ cho chủ sở hữu (`chmod 600`). Không lưu khóa vào repo hoặc vào `data/` của trang. [Serper](https://serper.dev/) trả kết quả tìm kiếm Google qua API; từ đó script chỉ đọc HTML ở domain chính thức của trường. Mỗi người dùng tối đa hai truy vấn (truy vấn theo tên + trường, rồi truy vấn trong domain trường nếu thông tin còn ít); `--limit` giúp kiểm soát số người được tìm. Mặc định xử lý đồng thời 6 người; chỉnh bằng `--workers`. `--refresh` tìm lại hồ sơ đang chờ duyệt. Kết quả được lưu sau từng người để tiếp tục khi gián đoạn. Trang chặn truy cập, thiếu thông tin hoặc không khớp tên sẽ để field rỗng.

Mỗi seed có 5 field: `photo`, `bio`, `expertise`, `education`, `links`. `sources` ghi URL nguồn theo field, `candidate_urls` giữ các kết quả từ domain trường để rà soát thủ công, `searched_at` ghi thời điểm tìm, `review_status` mặc định là `pending`. `cache_instructor_photos.py` lưu nguyên bản ảnh ứng viên vào `assets/about/instructors/` và ghi `photo.local_url`; bước này chỉ giúp bản seed tải ảnh ổn định, không duyệt danh tính hay quyền sử dụng. Sau khi kiểm tra đúng người và quyền sử dụng, đặt `photo.usage_status` thành `approved`.

Để dùng toàn bộ 184 hồ sơ làm seed trên trang đang phát triển, chạy `python3 scripts/crawl_instructors.py --publish-seed`. Lệnh này giữ cả field rỗng và trạng thái `pending` trong `data/instructors_profiles.json`. Ảnh ứng viên từ trang trường chỉ dùng trong bản seed đang phát triển, kèm nhãn đang rà soát và chữ viết tắt dự phòng nếu ảnh lỗi. Trước khi công bố chính thức, cần kiểm tra đúng người và quyền sử dụng ảnh.

Sau khi đối chiếu **từng hồ sơ** với nguồn, biên tập `bio` thành 2–3 câu ngắn, loại bỏ thông tin sai/đã cũ, đặt `review_status` thành `approved`, rồi chạy:

```bash
python3 scripts/crawl_instructors.py --publish
```

Lệnh `--publish` chỉ xuất hồ sơ đã duyệt vào `data/instructors_profiles.json`; ảnh chưa được duyệt quyền sử dụng sẽ không xuất. Trang vẫn hoạt động khi chưa có hồ sơ bổ sung. Không dùng email, số điện thoại, ngày sinh hoặc danh sách công bố trong đợt seed này.

## Timeline học vấn

`scripts/seed_instructor_education.py` đọc danh sách gốc `data/instructors.json` và tạo một bản ghi timeline cho từng người. `status: "source_candidate"` gồm mốc năm, văn bằng, ngành và trường được chép từ hồ sơ trường, có `source_url` để đối chiếu. Các chỗ nguồn không ghi chuyên ngành được để rỗng; năm tốt nghiệp không được đổi thành khoảng thời gian học. Đây vẫn là ứng viên đang chờ rà soát.

`status: "demo"` chỉ tạo các ô minh họa giao diện với năm `20XX`, tên mốc có chữ “minh họa” và trường/ngành “đang cập nhật”. **Không xem các mốc này là học vấn thật của giảng viên.** Trang chi tiết gắn nhãn “Dữ liệu minh họa” ngay phía trên timeline. Khi tìm được nguồn, thay bản ghi `demo` bằng `source_candidate` cùng URL nguồn; sau khi xác minh, có thể lưu timeline đã duyệt trong `instructors_profiles.json` qua field `education_timeline` để ưu tiên hiển thị. File seed timeline độc lập với lệnh `--publish-seed`, nên chạy lại crawler không ghi đè các mốc này.
