# Team

> Mỗi thành viên tự bổ sung thông tin và phần đóng góp của mình. Không ghi email, số điện thoại hoặc API key vào file này.

## Thông tin nhóm

- Tên nhóm: DHQ
- Bài lab: Day 03 — Research Agent Tool Eval

## Thành viên

| STT | Họ và tên | MSSV | Vai trò trong nhóm | Tài khoản GitHub |
|---:|---|---|---|---|
| 1 | Bùi Quang Hiếu | 2A202603639 | Agent & eval | (tự điền) |
| 2 | Nguyễn Công Quân | 2A202603675 | Tool & kiểm thử | nguyencongquana2 |
| 3 | Nguyễn Văn Đăng | 2A202603371 | UI & demo | nguyenvandang2201 |

## Phân công công việc

| Phụ trách | Công việc chính | Sản phẩm / bằng chứng |
|---|---|---|
| Bùi Quang Hiếu — Agent & eval | Cấu hình provider; chạy baseline `v0`; phân tích các case lỗi; tối ưu prompt và tool descriptions theo từng giả thuyết, chạy lần lượt `v1`, `v2`, `v3`. | `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv`, `runs/*.json` |
| Nguyễn Công Quân — Tool & kiểm thử | Viết ít nhất một tool mới và đăng ký tool; viết tối thiểu 3 unit test cho tool mới; soạn 10 eval case gồm 5 single-turn và 5 multi-turn; giữ `pytest` xanh. | `tools/<tên_tool>/tool.py`, `TOOL.md`, `tools/__init__.py`, `tests/`, `data/eval_group.json` |
| Nguyễn Văn Đăng — UI & demo | Dựng UI Streamlit hoặc Vercel; chuẩn bị câu hỏi demo; chạy ít nhất 3 lượt chat live; viết Phần A của report trước 16:30 và Phần B sau khi có run log. | UI và link dùng thử, `transcripts/*.transcript.json`, `artifacts/REPORT.md` |

## Phối hợp theo checkpoint

| Mốc | Người chính | Việc cần bàn giao |
|---|---|---|
| 15:00 — Baseline và UI | Hiếu, Đăng | Preflight, run `v0`; bản UI đầu tiên |
| 15:30 — Tool mới và `v1` | Quân, Hiếu | Tên/schema tool mới cho Hiếu đồng bộ `tools.yaml`; run `v1` |
| 16:00 — Team eval và `v2` | Quân, Hiếu | `eval_group.json`; run `v2` |
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

### NguyenCongQuan-2A202603675

**Phần việc phụ trách:**

- Tool & kiểm thử.

**Đóng góp cụ thể:**

- Xây dựng tool `deduplicate` để loại kết quả nghiên cứu trùng theo URL chuẩn hóa hoặc tiêu đề; hỗ trợ ba chiến lược `url_or_title`, `url`, `title` và xử lý input lỗi bằng error dict.
- Đăng ký tool trong registry và khai báo schema/description để agent phân biệt thao tác làm sạch dữ liệu với tìm kiếm hoặc định dạng.
- Hoàn thiện toàn bộ unit-test stub cho các tool có sẵn và viết 3 test cho `deduplicate` (happy path, input sai kiểu, strategy không hợp lệ).
- Soạn 10 team eval case gồm 5 single-turn và 5 multi-turn, bao phủ routing, argument, boundary và missing-info của tool mới.
- Thiết lập môi trường kiểm thử cục bộ và xác minh toàn bộ test suite đạt `84 passed, 0 failed, 0 skipped`.

**Bằng chứng:**

- `starter_v0/tools/deduplicate/tool.py`, `starter_v0/tools/deduplicate/TOOL.md`.
- `starter_v0/tools/__init__.py`, `starter_v0/artifacts/tools.yaml`.
- `starter_v0/tests/test_tools_todo.py`, `starter_v0/data/eval_group.json`.
- Kết quả `python -m pytest -q`: `84 passed in 0.37s`.

**Điều mình học được từ phần nhóm:**

- Phân biệt model eval (đo quyết định routing/arguments) với unit test (đo hành vi code của tool), đồng thời giữ tên và schema tool đồng bộ giữa declaration, registry, tài liệu và eval cases.

### NguyenVanDang-2A202603371

**Phần việc phụ trách:**

- UI & demo: dựng UI, chuẩn bị câu hỏi demo, chạy chat live, viết `REPORT.md` Phần A và Phần B.

**Đóng góp cụ thể:**

- **UI Streamlit** (`starter_v0/app.py`): dùng chung vòng lặp tool với `chat.py`; chọn provider/model/version; hiển thị tool đã gọi kèm args và kết quả; báo key nào còn thiếu (không hiện giá trị key); lưu transcript cùng format với `chat.py` và cho tải transcript JSON.
- **Provider DeepSeek** (`providers/deepseek_provider.py`, `--provider deepseek`): tắt thinking mode vì chế độ này trả lỗi 400 với `tool_choice="required"` mà eval dùng; preflight pass với `deepseek-flash` và `deepseek-v4-pro`.
- **Chat live:** chạy cùng 5 lượt hỏi trên v0 và v3, cộng 2 lượt qua UI. So sánh cho thấy hai lỗi nặng của v0 (tự đoán tài khoản `sama`, tự gọi `send(confirmed=true)`) đã hết ở v3.
- **Eval bổ sung trên v3:** eval nhóm 10/10 PASS, eval mở rộng 6/10 (phát hiện agent gọi `policy` thừa và chọn sai `policy_area`).
- **Sửa 2 bug trong code có sẵn**, mỗi bug kèm bằng chứng:
  - `tools/send/tool.py`: guardrail coi `confirmed="false"`, `"yes"`, `1` là đã xác nhận. Viết regression test (code cũ gửi tin ở 4/5 trường hợp), sửa thành `confirmed is not True`.
  - `versioning.py`: hash prompt khác nhau giữa Windows (CRLF) và macOS/Linux; chuẩn hoá xuống dòng trước khi băm để `artifact_version` thống nhất trên mọi máy.
- **Report:** viết Phần A (mô tả agent, bảng 11 tool, câu hỏi mẫu, cách chạy UI và tunnel) và toàn bộ Phần B (B1–B7); viết `scripts/report_tables.py` để sinh bảng B1–B4 từ log.

**Bằng chứng:**

- Code: `starter_v0/app.py`, `starter_v0/providers/deepseek_provider.py`, `starter_v0/scripts/report_tables.py`, `starter_v0/versioning.py`, `starter_v0/tools/send/tool.py`, `starter_v0/tests/test_tools_todo.py` (`test_send_only_accepts_boolean_true_as_confirmation`).
- Run eval v3: `starter_v0/runs/v3_B_group_deepseek_20261110T225728735212.json`, `starter_v0/runs/v3_B_extension_deepseek_20261110T225746086818.json`.
- Transcript chat live: `starter_v0/transcripts/v0_deepseek_20261110T142834839230.transcript.json` (v0, 5 lượt), `starter_v0/transcripts/v3_deepseek_20261110T230446456847.transcript.json` (v3, 5 lượt), `starter_v0/transcripts/v0_deepseek_ui_20261110T142953447844.transcript.json` (UI, 2 lượt).
- Report: `starter_v0/artifacts/REPORT.md`.

**Điều mình học được từ phần nhóm:**

- **Eval và live chat bổ sung cho nhau.** Base eval cho biết v3 sửa được R10, nhưng chỉ khi chạy cùng một kịch bản trên v0 và v3 mới thấy rõ người dùng nhận được gì khác nhau, ví dụ agent tự đăng Telegram ở v0 so với hỏi xác nhận ở v3.
- **Guardrail an toàn phải nằm trong code, không chỉ trong prompt.** Prompt v3 khiến model xin xác nhận, nhưng nếu model gửi `confirmed="false"` thì chỉ dòng kiểm tra trong `send` mới chặn được. Lỗi này eval không phát hiện được, unit test thì có.
- **Đo lường phải tái lập được.** Cùng một prompt nhưng ra hai mã hash khác nhau chỉ vì ký tự xuống dòng khiến version log khó so sánh giữa các máy. Phải đảm bảo cách đo nhất quán trước khi tin vào số liệu.
- **Không phải FAIL nào cũng là lỗi agent.** Với R12, agent hỏi lại nội dung là hợp lý nhưng vẫn bị chấm FAIL; với E01–E03, câu trả lời đúng nhưng có tool call thừa. Cần đọc log để tách lỗi của agent khỏi lỗi của tiêu chí chấm.
