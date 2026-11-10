# Team

> Mỗi thành viên tự bổ sung thông tin và phần đóng góp của mình. Không ghi email, số điện thoại hoặc API key vào file này.

## Thông tin nhóm

- Tên nhóm: (nhóm tự điền)
- Bài lab: Day 03 — Research Agent Tool Eval

## Thành viên

| STT | Họ và tên | MSSV | Vai trò trong nhóm | Tài khoản GitHub |
|---:|---|---|---|---|
| 1 | Bùi Quang Hiếu | 2A202603639 | Agent & eval | (tự điền) |
| 2 | (tự điền) | (tự điền) | Tool & kiểm thử | (tự điền) |
| 3 | Nguyễn Văn Đăng | 2A202603371 | UI & demo | (tự điền) |

## Phân công công việc

| Phụ trách | Công việc chính | Sản phẩm / bằng chứng |
|---|---|---|
| Bùi Quang Hiếu — Agent & eval | Cấu hình provider; chạy baseline `v0`; phân tích các case lỗi; tối ưu prompt và tool descriptions theo từng giả thuyết, chạy lần lượt `v1`, `v2`, `v3`. | `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv`, `runs/*.json` |
| Thành viên 2 — Tool & kiểm thử | Viết ít nhất một tool mới và đăng ký tool; viết tối thiểu 3 unit test cho tool mới; soạn 10 eval case gồm 5 single-turn và 5 multi-turn; giữ `pytest` xanh. | `tools/<tên_tool>/tool.py`, `TOOL.md`, `tools/__init__.py`, `tests/`, `data/eval_group.json` |
| Nguyễn Văn Đăng — UI & demo | Dựng UI Streamlit hoặc Vercel; chuẩn bị câu hỏi demo; chạy ít nhất 3 lượt chat live; viết Phần A của report trước 16:30 và Phần B sau khi có run log. | UI và link dùng thử, `transcripts/*.transcript.json`, `artifacts/REPORT.md` |

## Phối hợp theo checkpoint

| Mốc | Người chính | Việc cần bàn giao |
|---|---|---|
| 15:00 — Baseline và UI | Hiếu, Đăng | Preflight, run `v0`; bản UI đầu tiên |
| 15:30 — Tool mới và `v1` | Thành viên 2, Hiếu | Tên/schema tool mới cho Hiếu đồng bộ `tools.yaml`; run `v1` |
| 16:00 — Team eval và `v2` | Thành viên 2, Hiếu | `eval_group.json`; run `v2` |
| 16:30 — Demo | Đăng | UI hoạt động, `REPORT.md` Phần A và câu hỏi mẫu |
| 17:30 — `v3` và report chi tiết | Hiếu, Đăng | Metric/run log `v0`–`v3` cho Phần B |

## Cá nhân

Mỗi thành viên tự cập nhật mục của mình; chỉ ghi đóng góp và bằng chứng đã thực hiện.

### BuiQuangHieu-2A202603639

**Phần việc phụ trách:**

- Agent & eval: cấu hình provider, chạy `v0`–`v3`, phân tích lỗi routing/arguments, tối ưu prompt và tool declarations, ghi version log.

**Đóng góp cụ thể:**

- Đề xuất phân công ba mảng Agent & eval, Tool & kiểm thử, UI & demo; tạo template `TEAM.md`.

**Bằng chứng:**

- `TEAM.md`; bổ sung đường dẫn run và version log sau khi hoàn thành eval.

**Điều mình học được từ phần nhóm:**

- (tự bổ sung sau khi hoàn thành lab)

### ThanhVien2-MSSV

**Phần việc phụ trách:**

- Tool & kiểm thử.

**Đóng góp cụ thể:**

- (thành viên tự điền)

**Bằng chứng:**

- (thành viên tự điền)

**Điều mình học được từ phần nhóm:**

- (thành viên tự điền)

### NguyenVanDang-2A202603371

**Phần việc phụ trách:**

- UI & demo: dựng UI, chuẩn bị câu hỏi demo, chạy chat live, viết `REPORT.md` Phần A và Phần B.

**Đóng góp cụ thể:**

- Dựng UI Streamlit `starter_v0/app.py`, dùng chung vòng lặp tool với `chat.py`: chọn provider/model/version, hiển thị tool đã gọi kèm args và kết quả, báo trạng thái thiếu API key (không hiện giá trị key), lưu transcript cùng format với `chat.py` và cho tải transcript JSON.
- Viết `REPORT.md` Phần A: mô tả agent, bảng 10 tool, 6 câu hỏi mẫu, cách chạy UI và mở link public bằng Cloudflare Tunnel; điền dòng UI ở mục B5.
- Viết `starter_v0/scripts/report_tables.py` để sinh bảng B1–B4 của Phần B từ `version_log.csv`, `runs/*.json`, `eval_group.json` và `transcripts/`.
- Thêm `streamlit` vào `requirements.txt`.
- Thêm provider DeepSeek (`providers/deepseek_provider.py`, `--provider deepseek`): tắt thinking mode để `tool_choice="required"` của eval không bị lỗi 400; preflight pass với `deepseek-flash` và `deepseek-v4-pro`.
- Chạy chat live bằng DeepSeek (5 lượt qua `chat.py`, 2 lượt qua UI) và điền bảng B4 kèm nhận xét: phát hiện agent v0 tự đoán tài khoản `sama` thay vì hỏi lại, và gọi `send(confirmed=true)` mà không xin xác nhận.

**Bằng chứng:**

- `starter_v0/app.py`, `starter_v0/providers/deepseek_provider.py`, `starter_v0/scripts/report_tables.py`, `starter_v0/artifacts/REPORT.md` (Phần A, B4, B5).
- Transcript chat live (v0, DeepSeek): `starter_v0/transcripts/v0_deepseek_20261110T142834839230.transcript.json` (chat.py, 5 lượt), `starter_v0/transcripts/v0_deepseek_ui_20261110T142953447844.transcript.json` (UI, 2 lượt).
- Link dùng thử: (bổ sung link trycloudflare khi demo).

**Điều mình học được từ phần nhóm:**

- (thành viên tự điền)
