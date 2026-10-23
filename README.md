# 🎵 Music Player Pro (PySide6 + uv)

Ứng dụng phát nhạc hiện đại, chuyên nghiệp viết bằng **Python** và **PySide6** (Qt 6), quản lý dự án tối ưu bằng **uv**.

---

## ✨ Tính Năng Nổi Bật

1. **Phát Đa Định Dạng Âm Thanh**:
   - Hỗ trợ đầy đủ: `.mp3`, `.flac`, `.wav`, `.ogg`, `.m4a`, `.aac`, `.wma`, `.opus`, `.alac`, `.aiff`.
   - Đọc siêu dữ liệu (Metadata Tags) chuyên sâu bằng `mutagen`: Tiêu đề bài hát, Nghệ sĩ, Album, Năm phát hành, Ảnh bìa Album (Cover Art).

2. **Quản Lý Thư Viện Folder & Playlist Linh Hoạt**:
   - **Thư viện Thư mục (Folders)**: Thêm/quản lý nhiều thư mục nhạc trên máy tính, duyệt bài hát nhanh chóng với cơ chế quét nền bất đồng bộ (`QThread`) không đơ lag giao diện.
   - **Danh sách phát (Playlists)**: Tạo playlist mới, đổi tên, xoá, thêm file từ nhiều nguồn khác nhau, quản lý danh sách dễ dàng qua chuột phải.

3. **Ghi Nhớ Quá Trình Phát Riêng Biệt (Smart Playback Memory)**:
   - **Lưu trạng thái độc lập cho từng Folder và từng Playlist**:
     - Đang phát bài hát nào.
     - Vị trí phát chính xác tới từng giây/mili-giây.
   - Khi chuyển đổi giữa Folder A ⇄ Playlist B ⇄ Folder C, ứng dụng tự động lưu tiến trình của nguồn cũ và phục hồi chính xác bài hát + mốc thời gian của nguồn mới.
   - Hiển thị huy hiệu **"Đang nghe dở: [Tên bài] ([Thời gian]) - Nhấn để tiếp tục"** ngay trên giao diện.
   - Tự động lưu ngầm định kỳ và khi đóng ứng dụng để không bao giờ bị mất vị trí nghe.

4. **Giao Diện Đồ Hoạ Đẳng Cấp (Modern Professional Dark Theme)**:
   - Phong cách giao diện lấy cảm hứng từ Spotify & Apple Music với tông màu Dark Slate thanh lịch và điểm nhấn Emerald Green.
   - Bộ icon vector SVG sắc nét, không bị vỡ hạt trên màn hình độ phân giải cao (Retina, 2K, 4K).
   - Thanh trượt bài hát tương tác thông minh (Seek Slider): bấm chuột vào bất kỳ điểm nào để tua tới điểm đó ngay lập tức, hiển thị tooltip thời gian khi rê chuột.
   - Thanh điều khiển âm lượng với nút tắt/bật tiếng nhanh (Mute Toggle).
   - Bảng bài hát với hiệu ứng soundwave / animated equalizer khi bài hát đang phát.
   - Ô tìm kiếm tức thời (Real-time Filter) giúp tìm bài hát theo tên, ca sĩ, album ngay khi gõ.

5. **Chạy Ngầm Dưới Khay Hệ Thống (Hide to System Tray)**:
   - Nút bấm **"Ẩn Tray"** trên thanh công cụ hoặc click nút **[X]** đóng cửa sổ sẽ tự động thu nhỏ ứng dụng xuống khay hệ thống mà không làm gián đoạn bài nhạc đang nghe.
   - Nhấp vào biểu tượng ở khay hệ thống để Ẩn / Hiện cửa sổ ngay lập tức.
   - Menu chuột phải tại System Tray:
     - 👁 Hiện / Ẩn cửa sổ
     - ▶ Phát / ⏸ Tạm dừng
     - ⏭ Bài kế tiếp / ⏮ Bài trước
     - ❌ Thoát ứng dụng hoàn toàn
   - Tự động hiện thông báo nổi (Balloon Notification) ở góc màn hình khi chuyển bài hát lúc cửa sổ đang ẩn.

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy

Dự án được quản lý hoàn toàn bằng **uv** (công cụ quản lý Python cực nhanh).

### Yêu cầu tiên quyết
- **Python >= 3.10** (Khuyên dùng Python 3.12 - 3.14)
- **uv**: Nếu chưa có, cài đặt nhanh qua:
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### Cài đặt dự án

```bash
# Clone repository
git clone https://github.com/hieu-gui-tools/music_player_pro.git
cd music_player_pro

# Cài đặt môi trường ảo và thư viện dependencies tự động
uv sync
```

### Khởi chạy ứng dụng

- **Cách 1 (CLI)**:
  ```bash
  uv run music-player-pro
  # hoặc
  uv run python -m music_player_pro.main
  ```
- **Cách 2 (Khuyên dùng trên Windows)**: Nhấp đúp vào shortcut **Music Player Pro** trên màn hình Desktop.
- **Cách 3**: Nhấp đúp vào file `run.vbs` trong thư mục dự án (chạy êm không nhấp nháy cửa sổ console).
- **Cách 4**: Nhấp đúp vào file `run.cmd` trong thư mục dự án (hiển thị log console nếu cần debug).

### Tạo / Phục hồi Shortcut ra Desktop

Nếu cần tạo lại shortcut trên Desktop:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_shortcut.ps1
```

---

## 🧪 Kiểm Thử Tự Động (Tests)

Chạy bộ kiểm thử tự động tích hợp:
```bash
# Chạy toàn bộ tests
uv run python tests/test_player.py
uv run python tests/test_resume_position.py
uv run python tests/test_settings_and_tray.py
```

---

## 📂 Cấu Trúc Dự Án

```
music_player_pro/
├── pyproject.toml               # Cấu hình dự án & dependencies uv
├── uv.lock                      # Khóa phiên bản dependencies uv
├── README.md                    # Tài liệu hướng dẫn
├── .gitignore                   # Quy tắc bỏ qua file rác / nhị phân
├── assets/                      # Tài nguyên biểu tượng ứng dụng (icon.ico, icon.png)
├── scripts/                     # Scripts hỗ trợ tạo shortcut Desktop, convert icon
│   ├── create_shortcut.ps1
│   ├── create_shortcut.py
│   └── make_icon.py
├── src/
│   └── music_player_pro/
│       ├── __init__.py
│       ├── main.py              # Điểm khởi chạy ứng dụng (Entry point)
│       ├── core/
│       │   ├── __init__.py
│       │   ├── models.py        # Data models (Track, Playlist, PlaybackMemory)
│       │   ├── db.py            # SQLite storage lưu folder, playlist & playback memory
│       │   ├── scanner.py       # Quét file âm thanh, trích xuất metadata mutagen
│       │   └── player.py        # QMediaPlayer + QAudioOutput wrapper & auto-save logic
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── icons.py         # Bộ vector icons SVG chất lượng cao
│       │   ├── theme.py         # Stylesheet Dark Mode chuyên nghiệp
│       │   ├── main_window.py   # Cửa sổ chính điều phối các widget
│       │   └── widgets/
│       │       ├── header_banner.py    # Banner thông tin, thống kê & nút khôi phục
│       │       ├── player_bar.py       # Thanh phát nhạc dưới cùng + album cover
│       │       ├── seek_slider.py      # Thanh tua tương tác & tooltip
│       │       ├── settings_dialog.py  # Hộp thoại cài đặt ứng dụng
│       │       ├── sidebar.py          # Thanh điều hướng Folder & Playlist
│       │       ├── track_table.py      # Bảng danh sách bài hát + chuột phải
│       │       └── volume_slider.py    # Điều khiển âm lượng & mute
│       └── utils/
│           ├── __init__.py
│           └── formatters.py    # Định dạng thời gian (mm:ss) và dung lượng file
└── tests/
    ├── test_player.py           # Kiểm thử lõi phát nhạc, DB & scanner
    ├── test_resume_position.py  # Kiểm thử ghi nhớ mốc phát riêng biệt
    └── test_settings_and_tray.py# Kiểm thử cấu hình & system tray
```

---

## 📜 Giấy Phép & Tác Giả

- **Tác giả**: Hieu Python GUI dev tools (drhieuvn@gmail.com)
- **GitHub**: [@hieu-gui-tools](https://github.com/hieu-gui-tools)
