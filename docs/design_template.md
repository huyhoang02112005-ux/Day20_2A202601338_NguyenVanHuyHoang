# Design Specification: Multi-Agent Research System

## Problem

Xây dựng hệ thống **Multi-Agent Research Assistant** có khả năng xử lý các truy vấn nghiên cứu chuyên sâu, tự động tìm kiếm nguồn thông tin tin cậy, tổng hợp và đánh giá chất lượng bằng chứng, và sản xuất bài báo cáo kỹ thuật hoàn chỉnh kèm trích dẫn (citations) chính xác.

## Why multi-agent?

Single-agent baseline khi nhận một query phức tạp thường gặp các hạn chế:
1. **Context Bloat & Hallucination**: Xử lý đồng thời cả việc retrieve, phân tích và trình bày khiến LLM dễ bị ảo giác thông tin hoặc bỏ sót các chi tiết quan trọng.
2. **Thiếu kiểm tra chéo (Verification)**: Không có thành phần kiểm định độc lập nguồn trích dẫn.
3. **Multi-agent Advantage**: Phân tách trách nhiệm thành các vai trò chuyên biệt (Supervisor, Researcher, Analyst, Writer, Critic) giúp từng node tập trung tối đa vào nhiệm vụ chuyên môn, cải thiện đáng kể độ sâu phân tích và độ chính xác trích dẫn.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Điều phối luồng thực thi và quyết định route tiếp theo | `ResearchState` | `next_route` ("researcher", "analyst", "writer", "done") | Routing loop vô hạn nếu không có max iterations |
| Researcher | Thu thập nguồn tài liệu từ Search API / Corpus và tóm tắt thông tin | `request.query`, `max_sources` | `sources`, `research_notes` | Search API 404/500 hoặc không có kết quả |
| Analyst | Bóc tách luận điểm, so sánh góc nhìn, đánh giá độ tin cậy nguồn | `research_notes`, `sources` | `analysis_notes` | Phân tích hời hợt hoặc bỏ qua mâu thuẫn giữa các nguồn |
| Writer | Tổng hợp báo cáo kỹ thuật hoàn chỉnh theo yêu cầu audience kèm citations | `analysis_notes`, `sources` | `final_answer` | Quên chèn inline citations `[1]`, `[2]` |
| Critic | Đánh giá độ phủ trích dẫn và tính nhất quán thực tế | `final_answer`, `sources` | `citation_score`, trace events | Đánh giá sai định dạng trích dẫn |

## Shared state

- `request` (`ResearchQuery`): Lưu thông tin query ban đầu, max_sources, audience target.
- `iteration` (`int`): Đếm số vòng lặp supervisor điều phối để tránh loop vô hạn.
- `route_history` (`list[str]`): Ghi vết thứ tự các node agent đã thực thi.
- `sources` (`list[SourceDocument]`): Danh sách các nguồn tài liệu đã thu thập.
- `research_notes` (`str`): Ghi chú tóm tắt thông tin thô từ Researcher.
- `analysis_notes` (`str`): Phân tích chuyên sâu và so sánh bằng chứng từ Analyst.
- `final_answer` (`str`): Báo cáo kỹ thuật cuối cùng sản xuất bởi Writer.
- `agent_results` (`list[AgentResult]`): Kết quả chi tiết từ từng agent step để audit.
- `trace` (`list[dict]`): Telemetry tracing log phục vụ observability (LangSmith/Langfuse).

## Routing policy

```
                 +-------------------+
                 |    START / INIT   |
                 +---------+---------+
                           |
                           v
                 +---------+---------+
                 |    SUPERVISOR     | <-----------+
                 +---------+---------+             |
                           |                       |
        +------------------+------------------+    |
        |                  |                  |    |
        v                  v                  v    |
+-------+-------+  +-------+-------+  +-------+-------+
|  RESEARCHER   |  |    ANALYST    |  |    WRITER     |
+-------+-------+  +-------+-------+  +-------+-------+
        |                  |                  |
        +------------------+                  v
                           |          +-------+-------+
                           |          |    CRITIC     |
                           |          +-------+-------+
                           |                  |
                           +------------------+
                                              | (route == "done" or max_iterations)
                                              v
                                           +-----+
                                           | END |
                                           +-----+
```

## Guardrails

- **Max iterations**: Giới hạn mặc định `max_iterations = 6` trong `Settings` để ngắt loop bắt buộc.
- **Timeout**: Mỗi LLM call / HTTP request có timeout tối đa (mặc định 60s).
- **Retry**: Sử dụng retry có exponential backoff khi gọi LLM client và Search client.
- **Fallback**: Nếu Search API lỗi, hệ thống tự động chuyển sang Offline Corpus Search hoặc Structured Mock Generator.
- **Validation**: Strict schema validation với Pydantic v2 cho toàn bộ state và messages.

## Benchmark plan

- **Queries**: "Research GraphRAG state-of-the-art", "Multi-agent framework trade-offs".
- **Metrics**: Latency (seconds), Cost (USD), Quality score (0-10), Citation coverage (0-100%), Failure rate (0-100%).
- **Expected outcome**: Multi-agent đạt quality score >= 9.0 và citation coverage 100%, vượt trội hơn hẳn single-agent baseline.
