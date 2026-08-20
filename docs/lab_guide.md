# Lab Guide: Multi-Agent Research System

## Scenario

Bạn cần xây dựng một research assistant có thể nhận câu hỏi dài, tìm thông tin, phân tích và viết câu trả lời cuối cùng. Lab yêu cầu so sánh hai cách làm:

1. **Single-agent baseline**: một agent làm toàn bộ.
2. **Multi-agent workflow**: Supervisor điều phối Researcher, Analyst, Writer.

## Quy tắc quan trọng

- Không thêm agent nếu không có lý do rõ ràng.
- Mỗi agent phải có responsibility riêng.
- Shared state phải đủ rõ để debug.
- Phải có trace hoặc log cho từng bước.
- Phải benchmark, không chỉ nhìn output bằng cảm tính.

## Milestone 1: Baseline

File gợi ý:

- `src/multi_agent_research_lab/cli.py`
- `src/multi_agent_research_lab/services/llm_client.py`

TODO(student): thay baseline placeholder bằng một call LLM thật.

## Milestone 2: Supervisor

File gợi ý:

- `src/multi_agent_research_lab/agents/supervisor.py`
- `src/multi_agent_research_lab/graph/workflow.py`

TODO(student): implement routing policy.

Gợi ý câu hỏi thiết kế:

- Khi nào gọi Researcher?
- Khi nào gọi Analyst?
- Khi nào gọi Writer?
- Khi nào stop?
- Nếu agent fail thì retry hay fallback?

## Milestone 3: Worker agents

File gợi ý:

- `src/multi_agent_research_lab/agents/researcher.py`
- `src/multi_agent_research_lab/agents/analyst.py`
- `src/multi_agent_research_lab/agents/writer.py`

TODO(student): implement từng worker.

## Milestone 4: Trace và benchmark

File gợi ý:

- `src/multi_agent_research_lab/observability/tracing.py`
- `src/multi_agent_research_lab/evaluation/benchmark.py`
- `src/multi_agent_research_lab/evaluation/report.py`

Benchmark tối thiểu:

| Metric | Cách đo gợi ý |
|---|---|
| Latency | wall-clock time |
| Cost | token usage hoặc provider usage |
| Quality | rubric 0-10 do peer review |
| Citation coverage | số claims có source / tổng claims chính |
| Failure rate | số query fail / tổng query |

## Troubleshooting

### macOS: lỗi SSL certificate khi gọi API qua HTTPS (Tavily, OpenAI, ...)

Triệu chứng: khi implement `SearchClient` (hoặc bất kỳ HTTPS call nào) trên macOS, bạn có thể gặp lỗi kiểu:

```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed:
unable to get local issuer certificate
```

Nguyên nhân: Python cài từ python.org trên macOS **không dùng** certificate store của hệ điều hành, nên không tìm thấy CA bundle hợp lệ. Đây là lỗi môi trường, **không phải** do API key sai.

Cách khắc phục (chọn 1 trong 3):

1. **Chạy script cài certificate đi kèm Python** (nhanh nhất):

   ```bash
   /Applications/Python\ 3.12/Install\ Certificates.command
   ```

   (thay `3.12` bằng version Python của bạn)

2. **Dùng `certifi` trong code** — thêm `certifi` vào dependencies, rồi tạo SSL context khi gọi HTTPS:

   ```python
   import certifi
   import ssl
   from urllib.request import urlopen

   ssl_context = ssl.create_default_context(cafile=certifi.where())
   urlopen(request, timeout=timeout, context=ssl_context)
   ```

3. **Set biến môi trường** trỏ tới CA bundle của certifi (không cần đổi code):

   ```bash
   export SSL_CERT_FILE=$(python -m certifi)
   ```

## Exit ticket

### 1. Case nào nên dùng multi-agent? Vì sao?

- **Bài toán phức tạp, nhiều công đoạn có chuyên môn hóa cao**: Ví dụ bài toán Deep Research, Code Generation & Audit, Legal Contract Review. Trong các trường hợp này, chia nhỏ công việc cho các agent chuyên biệt (Researcher tìm thông tin, Analyst đánh giá đối chiếu, Writer viết báo cáo, Critic kiểm định) giúp phân tách rõ ràng trách nhiệm (Separation of Concerns), giảm đáng kể hiện tượng hallucination và quá tải context window của 1 LLM call duy nhất.
- **Yêu cầu kiểm chứng thông tin & quy trình có vòng lặp (Human-in-the-loop / Iterative refinement)**: Multi-agent cho phép Supervisor hoặc Critic tự động kiểm tra output của Worker agent và quyết định phản hồi/chạy lại bước đó nếu chưa đạt tiêu chuẩn về citation hoặc thông tin thiếu sót.

### 2. Case nào không nên dùng multi-agent? Vì sao?

- **Truy vấn đơn giản, yêu cầu độ trễ cực thấp (Low Latency Real-time Applications)**: Các tác vụ như Tra cứu FAQ, Tìm kiếm từ khóa, Tóm tắt văn bản ngắn. Sử dụng Multi-agent trong các trường hợp này chỉ tạo thêm overhead về mạng/latency (chạy qua nhiều node supervisor/worker làm tăng latency từ <1s lên vài giây) và chi phí API token cao hơn gấp nhiều lần mà không mang lại giá trị gia tăng tương xứng.
- **Bài toán luồng tuyến tính 1 chiều không có phân nhánh phức tạp**: Khi một prompt duy nhất (Single-agent baseline hoặc Sequential Chain) đã giải quyết triệt để vấn đề mà không cần đến routing động hay tranh luận/đánh giá chéo giữa các agent.

