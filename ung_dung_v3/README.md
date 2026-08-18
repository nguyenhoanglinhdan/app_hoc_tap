# Học Tiếng Anh 🦉

Ứng dụng học từ vựng tiếng Anh trên máy tính, giao diện theo phong cách Duolingo,
viết bằng Python + CustomTkinter.

## Chạy thử

```bash
pip install -r requirements.txt
python main.py
```

Muốn có thêm phần nghe và chấm phát âm thì cài bản đầy đủ:

```bash
pip install -r requirements-am-thanh.txt
```

Cần Python 3.12 trở lên (mã nguồn dùng `match`, `StrEnum`, `Self` và cú pháp
`X | None`).

## Có gì trong ứng dụng

### Học
- **Lộ trình học** uốn lượn với các chặng hình tròn, mở khoá dần: xong chặng
  trước mới đi tiếp được chặng sau.
- **Sáu dạng bài tập**: chọn nghĩa tiếng Việt, chọn từ tiếng Anh, tự gõ từ, ghép
  cặp Anh - Việt, **nghe rồi chọn từ**, và **đọc to cho máy chấm phát âm**.
- **Năm trái tim mỗi lượt học**. Trả lời sai mất một tim và câu đó bị hỏi lại ở
  cuối; hết tim thì phải học lại từ đầu. Ghép sai trong bài ghép đôi không bị
  trừ tim.
- **XP, cấp độ và chuỗi ngày học** được lưu lại giữa các lần mở ứng dụng.
- **Phím tắt**: `1`–`4` chọn phương án, `Enter` để kiểm tra và đi tiếp.

### Nghe và nói
- Nút 🔊 đọc từ tiếng Anh ở thẻ đề bài, bài nghe và bài nói.
- Bài **Nghe chọn** giấu chữ đi, người học phải nghe rồi mới chọn.
- Bài **Nói theo** thu giọng người học, gửi đi nhận dạng rồi so với từ mục tiêu;
  đạt từ 70/100 điểm giống nhau trở lên là qua.
- Có nút **"Không nói được lúc này"** để bỏ qua bài nói mà không bị trừ tim.

### Luyện tập
- **Ôn từ tới hạn** theo lịch lặp ngắt quãng.
- **Luyện từ hay sai**, ưu tiên từ có tỷ lệ đúng thấp nhất.
- **Trộn ngẫu nhiên** các từ đã gặp ở mọi chủ đề.
- Bảng **mức độ thuộc** (Từ mới / Đang học / Quen thuộc / Thuộc lòng) và danh
  sách từ cần chú ý nhất.
- Buổi luyện tập chỉ cộng XP, không đánh dấu chặng nào trong lộ trình.

### Sổ tay và soạn từ
- **Sổ tay từ vựng** tra cứu được, tìm kiếm không cần gõ dấu.
- **Soạn từ vựng ngay trong ứng dụng**: thêm/sửa/xoá chủ đề và từ, có kiểm tra
  trùng lặp và xác nhận trước khi xoá, ghi thẳng vào `du_lieu/tu_vung.json`.

### Khác
- **Chế độ sáng/tối**, đổi trong màn hình Hồ sơ.
- Thống kê XP, chuỗi ngày, số bài và số từ đã học.

## Cấu trúc mã nguồn

```
ung_dung_v3/
├── main.py                       # điểm khởi động
├── du_lieu/
│   ├── tu_vung.json              # nội dung học
│   └── tien_do.json              # tiến độ người dùng (tự sinh)
├── hoc_tieng_anh/
│   ├── mo_hinh.py                # TuVung, BaiHoc, DonVi, GiaoTrinh
│   ├── bai_tap.py                # sinh câu hỏi + máy trạng thái phiên học
│   ├── on_tap.py                 # lặp ngắt quãng (SM-2 rút gọn)
│   ├── tien_do.py                # XP, cấp độ, chuỗi ngày, lịch ôn từng từ
│   ├── am_thanh.py               # đọc từ và chấm phát âm
│   ├── kho_du_lieu.py            # đọc/ghi JSON (ranh giới vào ra duy nhất)
│   └── giao_dien/
│       ├── chu_de.py             # bảng màu, phông chữ, hằng số bố cục
│       ├── thanh_phan.py         # widget dùng lại (nút nổi khối, thẻ, tim...)
│       ├── hop_thoai.py          # hộp thoại nhập từ và chủ đề
│       ├── man_hinh_goc.py       # lớp nền + giao ước điều hướng
│       ├── man_hinh_chinh.py     # lộ trình học
│       ├── man_hinh_bai_hoc.py   # màn hình làm bài
│       ├── man_hinh_luyen_tap.py # luyện tập tổng hợp
│       ├── man_hinh_tu_vung.py   # sổ tay từ vựng
│       ├── man_hinh_soan_tu.py   # soạn nội dung học
│       ├── man_hinh_ho_so.py     # thống kê và tuỳ chọn
│       └── ung_dung.py           # cửa sổ chính, thanh điều hướng
└── tests/                        # kiểm thử phần lõi
```

Nguyên tắc chia lớp: **`mo_hinh`, `bai_tap`, `on_tap`, `tien_do` không import
tkinter**. Nhờ vậy toàn bộ luật chơi (sinh câu hỏi, tính điểm, trừ tim, chuỗi
ngày, lịch ôn tập) chạy kiểm thử được mà không cần mở cửa sổ. Phần `giao_dien`
chỉ lo hiển thị, và các màn hình phụ thuộc vào giao ước `DieuHuong` chứ không
phụ thuộc thẳng vào lớp `UngDung`.

## Kiểm thử

```bash
pip install -r requirements-dev.txt
python -m pytest tests -q
```

## Thêm từ vựng mới

Cách nhanh nhất là dùng màn hình **Soạn từ** ngay trong ứng dụng. Nếu muốn sửa
tay thì mở `du_lieu/tu_vung.json` và thêm một đơn vị vào danh sách `cac_don_vi`:

```json
{
  "ma": "the-thao",
  "ten": "Thể thao",
  "mo_ta": "Các môn thể thao thường gặp",
  "mau": "cam",
  "bieu_tuong": "⚽",
  "tu_vung": [
    { "en": "football", "vi": "bóng đá", "phien_am": "/ˈfʊtbɔːl/" }
  ]
}
```

- `ma` phải là duy nhất, không trùng với đơn vị khác.
- `mau` chọn một trong: `xanh_la`, `xanh_duong`, `tim`, `cam`, `hong`, `vang`.
- `phien_am` có thể bỏ trống.
- Ứng dụng tự cắt mỗi đơn vị thành các bài học 5 từ (`SO_TU_MOI_BAI` trong
  `mo_hinh.py`).

## Ghi chú kỹ thuật

**Nút nổi khối.** Duolingo dùng nút có một lớp bóng đậm màu nằm dưới, và mặt nút
tụt xuống khi bấm. CustomTkinter không có sẵn hiệu ứng này nên `NutDuo` và
`TheLuaChon` xếp chồng hai widget: một khung màu đậm làm bóng, một nút đặt đè
lên trên, khi bấm thì dời nút xuống đúng bằng độ dày lớp bóng.

**Bề ngang của nút tròn.** `CTkButton` tự nới rộng theo bề ngang của chữ, nên
chặng học hình tròn và nút loa không đặt biểu tượng làm chữ của nút mà phủ một
nhãn riêng lên trên, đồng thời buộc bề ngang nút bằng `relwidth=1`. Nếu bỏ hai
chi tiết này, hình tròn sẽ bị méo thành hình bầu dục.

**Âm thanh là tuỳ chọn.** `am_thanh.py` tự dò xem máy có thư viện, có micro và
có giọng đọc hay không. Thiếu thứ gì thì ứng dụng ẩn nút tương ứng và trình sinh
câu hỏi bỏ luôn hai dạng bài cần âm thanh, chứ không báo lỗi. Bộ đọc SAPI chạy
trong một luồng riêng vì `pyttsx3` không cho gọi `runAndWait` lồng nhau, còn
việc thu âm chạy ở luồng khác để giao diện không bị treo.

**Chọn micro.** Ứng dụng không dùng thiết bị thu mặc định của hệ điều hành: nhiều
máy không đặt thiết bị mặc định và PortAudio sẽ báo `Error querying device -1`.
Thay vào đó `_chon_micro()` tự duyệt danh sách, bỏ qua các cổng thu âm hệ thống
(Stereo Mix, loopback) và ưu tiên micro có tần số lấy mẫu cao nhất.

**Lặp ngắt quãng.** `on_tap.py` dùng SM-2 rút gọn: mỗi từ có khoảng cách ôn và hệ
số dễ, đúng thì giãn khoảng cách, sai thì đưa về ôn lại ngay. Khoảng cách bị chặn
trần ở 365 ngày - không có trần thì nó nhân dồn theo cấp số nhân và `date` sẽ
tràn số sau vài chục lần trả lời đúng liên tiếp.

**Lưu tiến độ an toàn.** `KhoDuLieu._ghi_json` ghi ra tệp tạm rồi mới
`os.replace`, dùng chung cho cả tiến độ lẫn giáo trình, nên tắt máy giữa chừng
cũng không làm hỏng tệp. Tệp tiến độ hỏng hoặc thiếu chỉ khiến ứng dụng bắt đầu
lại từ đầu, không làm treo chương trình.
