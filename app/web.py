"""Giao diện web nhẹ cho agent API."""

from __future__ import annotations

import secrets

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

_NONCE_TOKEN = "__CSP_NONCE__"
_PAGE = """<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Cloud Agent</title>
  <style nonce="__CSP_NONCE__">
    :root {
      color-scheme: dark;
      --bg: #07111f;
      --panel: rgba(14, 29, 49, 0.82);
      --panel-strong: #10233b;
      --line: rgba(148, 180, 213, 0.18);
      --text: #f5f8fc;
      --muted: #9db0c5;
      --primary: #62e6c8;
      --primary-strong: #2ed7b1;
      --accent: #77a9ff;
      --danger: #ff8f9b;
      --success: #62e6c8;
      --shadow: 0 24px 80px rgba(0, 0, 0, 0.38);
    }

    * { box-sizing: border-box; }
    [hidden] { display: none !important; }

    body {
      min-height: 100vh;
      margin: 0;
      color: var(--text);
      background:
        radial-gradient(circle at 12% 8%, rgba(52, 126, 255, 0.22), transparent 30rem),
        radial-gradient(circle at 88% 16%, rgba(46, 215, 177, 0.16), transparent 28rem),
        var(--bg);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
    }

    body::before {
      position: fixed;
      inset: 0;
      z-index: -1;
      content: "";
      opacity: 0.2;
      background-image:
        linear-gradient(rgba(255, 255, 255, 0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
      background-size: 42px 42px;
      mask-image: linear-gradient(to bottom, black, transparent 78%);
    }

    button, input, textarea { font: inherit; }

    .shell {
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 64px 0 28px;
    }

    .hero {
      max-width: 760px;
      margin-bottom: 28px;
    }

    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 9px;
      margin-bottom: 18px;
      color: var(--muted);
      font-size: 0.82rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .dot {
      width: 9px;
      height: 9px;
      border-radius: 999px;
      background: #f6bd5b;
      box-shadow: 0 0 0 5px rgba(246, 189, 91, 0.11);
    }

    .dot.online {
      background: var(--success);
      box-shadow: 0 0 0 5px rgba(98, 230, 200, 0.12);
    }

    .dot.offline {
      background: var(--danger);
      box-shadow: 0 0 0 5px rgba(255, 143, 155, 0.12);
    }

    h1 {
      margin: 0;
      font-size: clamp(2.5rem, 7vw, 5.2rem);
      line-height: 0.98;
      letter-spacing: -0.055em;
    }

    .gradient-text {
      color: transparent;
      background: linear-gradient(110deg, var(--primary), #a9c7ff 62%, #d9b8ff);
      background-clip: text;
      -webkit-background-clip: text;
    }

    .hero p {
      max-width: 620px;
      margin: 18px 0 0;
      color: var(--muted);
      font-size: clamp(1rem, 2vw, 1.12rem);
      line-height: 1.7;
    }

    .workspace {
      display: grid;
      grid-template-columns: minmax(0, 0.92fr) minmax(0, 1.08fr);
      gap: 18px;
      align-items: stretch;
    }

    .panel {
      border: 1px solid var(--line);
      border-radius: 24px;
      background: var(--panel);
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
      -webkit-backdrop-filter: blur(18px);
    }

    .form-panel { padding: 26px; }

    .panel-title {
      margin: 0 0 6px;
      font-size: 1.12rem;
      letter-spacing: -0.02em;
    }

    .panel-copy {
      margin: 0 0 24px;
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.55;
    }

    .field { margin-bottom: 17px; }

    .field-row {
      display: grid;
      grid-template-columns: 0.8fr 1.2fr;
      gap: 12px;
    }

    label {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 8px;
      color: #dce8f4;
      font-size: 0.86rem;
      font-weight: 700;
    }

    label span {
      color: var(--muted);
      font-size: 0.75rem;
      font-weight: 500;
    }

    input, textarea {
      width: 100%;
      border: 1px solid rgba(157, 176, 197, 0.22);
      border-radius: 14px;
      outline: none;
      color: var(--text);
      background: rgba(4, 13, 25, 0.68);
      transition: border-color 160ms ease, box-shadow 160ms ease, background 160ms ease;
    }

    input { height: 48px; padding: 0 14px; }

    textarea {
      min-height: 152px;
      padding: 14px;
      line-height: 1.55;
      resize: vertical;
    }

    input::placeholder, textarea::placeholder { color: #70849a; }

    input:focus, textarea:focus {
      border-color: var(--primary);
      background: rgba(4, 13, 25, 0.9);
      box-shadow: 0 0 0 4px rgba(98, 230, 200, 0.1);
    }

    .privacy-note {
      display: flex;
      gap: 8px;
      margin: -5px 0 18px;
      color: var(--muted);
      font-size: 0.76rem;
      line-height: 1.45;
    }

    .privacy-note strong { color: var(--primary); }

    .submit {
      display: inline-flex;
      width: 100%;
      height: 52px;
      align-items: center;
      justify-content: center;
      gap: 10px;
      border: 0;
      border-radius: 15px;
      color: #041711;
      background: linear-gradient(120deg, var(--primary), var(--primary-strong));
      box-shadow: 0 12px 28px rgba(46, 215, 177, 0.2);
      cursor: pointer;
      font-weight: 800;
      transition: transform 160ms ease, box-shadow 160ms ease, opacity 160ms ease;
    }

    .submit:hover:not(:disabled) {
      transform: translateY(-1px);
      box-shadow: 0 15px 34px rgba(46, 215, 177, 0.28);
    }

    .submit:disabled { cursor: wait; opacity: 0.65; }

    .spinner {
      display: none;
      width: 17px;
      height: 17px;
      border: 2px solid rgba(4, 23, 17, 0.25);
      border-top-color: #041711;
      border-radius: 50%;
      animation: spin 700ms linear infinite;
    }

    .submit.loading .spinner { display: inline-block; }

    .response-panel {
      display: flex;
      min-height: 460px;
      flex-direction: column;
      overflow: hidden;
    }

    .response-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 22px 24px;
      border-bottom: 1px solid var(--line);
    }

    .response-head h2 { margin: 0; font-size: 1rem; }

    .status {
      color: var(--muted);
      font-size: 0.8rem;
      font-weight: 700;
    }

    .status.success { color: var(--success); }
    .status.error { color: var(--danger); }

    .response-body {
      display: flex;
      min-height: 0;
      flex: 1;
      flex-direction: column;
      padding: 26px;
    }

    .empty {
      display: grid;
      min-height: 100%;
      flex: 1;
      place-items: center;
      color: var(--muted);
      text-align: center;
    }

    .empty-mark {
      display: grid;
      width: 62px;
      height: 62px;
      margin: 0 auto 16px;
      place-items: center;
      border: 1px solid var(--line);
      border-radius: 20px;
      color: var(--primary);
      background: rgba(98, 230, 200, 0.06);
      font-size: 1.55rem;
    }

    .empty p { max-width: 300px; margin: 0; line-height: 1.6; }

    .answer {
      margin: 0;
      color: #eaf2fb;
      font-size: 1.03rem;
      line-height: 1.78;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }

    .meta {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      margin: 28px 0 0;
    }

    .meta div {
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 13px;
      background: rgba(4, 13, 25, 0.42);
    }

    .meta dt {
      margin-bottom: 5px;
      color: var(--muted);
      font-size: 0.7rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }

    .meta dd {
      margin: 0;
      overflow: hidden;
      font-size: 0.86rem;
      font-weight: 750;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .error-box {
      padding: 14px 16px;
      border: 1px solid rgba(255, 143, 155, 0.3);
      border-radius: 14px;
      color: #ffd6da;
      background: rgba(255, 91, 108, 0.08);
      line-height: 1.55;
    }

    footer {
      display: flex;
      justify-content: space-between;
      gap: 20px;
      padding: 22px 4px 0;
      color: #7489a0;
      font-size: 0.78rem;
    }

    footer nav { display: flex; gap: 16px; }
    footer a { color: #a9bdd2; text-decoration: none; }
    footer a:hover { color: var(--primary); }

    :focus-visible {
      outline: 3px solid rgba(119, 169, 255, 0.72);
      outline-offset: 3px;
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    @media (max-width: 760px) {
      .shell { padding-top: 36px; }
      .workspace { grid-template-columns: 1fr; }
      .response-panel { min-height: 390px; }
    }

    @media (max-width: 520px) {
      .shell { width: min(100% - 20px, 1120px); }
      .form-panel, .response-body { padding: 20px; }
      .field-row, .meta { grid-template-columns: 1fr; }
      footer { flex-direction: column; }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
      }
    }
  </style>
</head>
<body>
  <main class="shell">
    <header class="hero">
      <div class="eyebrow" aria-live="polite">
        <span class="dot" id="health-dot" aria-hidden="true"></span>
        <span id="health-text">Đang kiểm tra dịch vụ</span>
      </div>
      <h1>Hỏi nhanh.<br><span class="gradient-text">Hiểu rõ hơn.</span></h1>
      <p>Gửi câu hỏi tới Cloud Agent và xem ngay câu trả lời, token cùng chi phí của mỗi lượt.</p>
    </header>

    <div class="workspace">
      <form class="panel form-panel" id="ask-form" novalidate>
        <h2 class="panel-title">Tạo câu hỏi</h2>
        <p class="panel-copy">Điền thông tin xác thực rồi bắt đầu cuộc trò chuyện.</p>

        <div class="field">
          <label for="question">Câu hỏi <span>Tối đa 2.000 ký tự</span></label>
          <textarea id="question" name="question" maxlength="2000" required
            placeholder="Ví dụ: Triển khai cloud an toàn cần những gì?"></textarea>
        </div>

        <div class="field-row">
          <div class="field">
            <label for="user-id">User ID <span>Không bắt buộc</span></label>
            <input id="user-id" name="user-id" type="text" maxlength="100"
              autocomplete="off" placeholder="sv-test">
          </div>
          <div class="field">
            <label for="api-key">API key</label>
            <input id="api-key" name="api-key" type="password" required
              autocomplete="off" spellcheck="false" aria-describedby="api-key-note"
              placeholder="Nhập AGENT_API_KEY">
          </div>
        </div>

        <p class="privacy-note" id="api-key-note"><strong>Riêng tư:</strong> API key chỉ dùng cho request hiện tại và không được lưu.</p>

        <button class="submit" id="submit-button" type="submit">
          <span class="button-label">Gửi câu hỏi</span>
          <span class="spinner" aria-hidden="true"></span>
        </button>
      </form>

      <section class="panel response-panel" aria-labelledby="response-title">
        <div class="response-head">
          <h2 id="response-title">Phản hồi</h2>
          <span class="status" id="request-status" aria-live="polite">Sẵn sàng</span>
        </div>
        <div class="response-body" id="response-body" tabindex="-1" aria-busy="false">
          <div class="empty" id="empty-state">
            <div>
              <div class="empty-mark" aria-hidden="true">↗</div>
              <p>Câu trả lời và thông tin sử dụng sẽ xuất hiện tại đây.</p>
            </div>
          </div>

          <div id="result" hidden>
            <p class="answer" id="answer"></p>
            <dl class="meta">
              <div><dt>User</dt><dd id="meta-user">—</dd></div>
              <div><dt>Lịch sử</dt><dd id="meta-history">—</dd></div>
              <div><dt>Tokens / Chi phí</dt><dd id="meta-usage">—</dd></div>
            </dl>
          </div>

          <div class="error-box" id="error-box" role="alert" hidden></div>
        </div>
      </section>
    </div>

    <footer>
      <span>Day 12 · Cloud Services & Deployment</span>
      <nav aria-label="Liên kết kỹ thuật">
        <a href="/docs">API Docs</a>
        <a href="/health">Health</a>
        <a href="/ready">Ready</a>
      </nav>
    </footer>
  </main>

  <script nonce="__CSP_NONCE__">
    "use strict";

    const form = document.getElementById("ask-form");
    const questionInput = document.getElementById("question");
    const userInput = document.getElementById("user-id");
    const keyInput = document.getElementById("api-key");
    const submitButton = document.getElementById("submit-button");
    const responseBody = document.getElementById("response-body");
    const requestStatus = document.getElementById("request-status");
    const emptyState = document.getElementById("empty-state");
    const result = document.getElementById("result");
    const errorBox = document.getElementById("error-box");
    const answer = document.getElementById("answer");
    const metaUser = document.getElementById("meta-user");
    const metaHistory = document.getElementById("meta-history");
    const metaUsage = document.getElementById("meta-usage");
    const healthDot = document.getElementById("health-dot");
    const healthText = document.getElementById("health-text");
    const requestTimeoutMs = 30000;

    const httpMessages = {
      401: "API key không đúng hoặc đang để trống.",
      402: "Ngân sách tháng đã hết.",
      422: "Câu hỏi không hợp lệ.",
      429: "Bạn gửi quá nhanh. Hãy thử lại sau một phút.",
      502: "Không thể kết nối tới mô hình AI. Vui lòng thử lại sau.",
      503: "Dịch vụ chưa sẵn sàng. Hãy kiểm tra Redis."
    };

    function setRequestStatus(text, kind = "") {
      requestStatus.textContent = text;
      requestStatus.className = `status ${kind}`.trim();
    }

    function resetOutput() {
      emptyState.hidden = true;
      result.hidden = true;
      errorBox.hidden = true;
      errorBox.textContent = "";
    }

    function showError(message) {
      resetOutput();
      errorBox.textContent = message;
      errorBox.hidden = false;
      setRequestStatus("Có lỗi", "error");
    }

    async function checkHealth() {
      try {
        const response = await fetch("/health", { cache: "no-store" });
        if (!response.ok) throw new Error("unhealthy");
        healthDot.className = "dot online";
        healthText.textContent = "Dịch vụ đang hoạt động";
      } catch (_error) {
        healthDot.className = "dot offline";
        healthText.textContent = "Không kết nối được dịch vụ";
      }
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const question = questionInput.value.trim();
      const userId = userInput.value.trim();
      const apiKey = keyInput.value.trim();

      if (!question) {
        showError("Vui lòng nhập câu hỏi.");
        questionInput.focus();
        return;
      }
      if (!apiKey) {
        showError("Vui lòng nhập API key.");
        keyInput.focus();
        return;
      }

      resetOutput();
      submitButton.disabled = true;
      submitButton.classList.add("loading");
      responseBody.setAttribute("aria-busy", "true");
      setRequestStatus("Đang xử lý");

      const headers = {
        "Content-Type": "application/json",
        "X-API-Key": apiKey
      };
      if (userId) headers["X-User-Id"] = userId;

      const controller = new AbortController();
      const timeoutId = window.setTimeout(() => controller.abort(), requestTimeoutMs);

      try {
        const response = await fetch("/ask", {
          method: "POST",
          headers,
          body: JSON.stringify({ question }),
          signal: controller.signal
        });
        const contentType = response.headers.get("content-type") || "";
        let payload = null;
        if (contentType.includes("application/json")) {
          payload = await response.json().catch(() => null);
        }

        if (!response.ok) {
          const detail = payload && typeof payload.detail === "string" ? payload.detail : "";
          throw new Error(httpMessages[response.status] || detail || `HTTP ${response.status}`);
        }

        if (!payload || typeof payload.answer !== "string" || !payload.answer.trim()) {
          throw new Error("Phản hồi từ dịch vụ không hợp lệ.");
        }

        answer.textContent = payload.answer;
        metaUser.textContent = payload.user_id || "anonymous";
        const historyLength = Number(payload.history_length);
        metaHistory.textContent = Number.isInteger(historyLength) && historyLength >= 0
          ? `${historyLength} tin nhắn`
          : "—";

        const tokensIn = Number(payload.tokens?.in);
        const tokensOut = Number(payload.tokens?.out);
        const tokenText = Number.isFinite(tokensIn) && Number.isFinite(tokensOut)
          ? String(tokensIn + tokensOut)
          : "—";
        const cost = Number(payload.cost_usd);
        const costText = Number.isFinite(cost) && cost >= 0 ? `$${cost.toFixed(6)}` : "—";
        metaUsage.textContent = `${tokenText} / ${costText}`;

        result.hidden = false;
        setRequestStatus("Hoàn tất", "success");
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          showError("Yêu cầu hết thời gian chờ và có thể vẫn đang được xử lý. Hãy kiểm tra trước khi gửi lại.");
        } else if (error instanceof TypeError) {
          showError("Không thể kết nối tới dịch vụ.");
        } else {
          showError(error instanceof Error ? error.message : "Đã xảy ra lỗi.");
        }
      } finally {
        window.clearTimeout(timeoutId);
        keyInput.value = "";
        submitButton.disabled = false;
        submitButton.classList.remove("loading");
        responseBody.setAttribute("aria-busy", "false");
        responseBody.focus();
      }
    });

    window.addEventListener("pageshow", () => { keyInput.value = ""; });
    checkHealth();
  </script>
</body>
</html>
"""


def _security_headers(nonce: str) -> dict[str, str]:
    policy = (
        "default-src 'none'; "
        f"script-src 'nonce-{nonce}'; "
        f"style-src 'nonce-{nonce}'; "
        "connect-src 'self'; base-uri 'none'; form-action 'self'; "
        "frame-ancestors 'none'"
    )
    return {
        "Cache-Control": "no-store",
        "Pragma": "no-cache",
        "Referrer-Policy": "no-referrer",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Content-Security-Policy": policy,
    }


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def home() -> HTMLResponse:
    """Trả về UI với CSP nonce mới cho mỗi request."""
    nonce = secrets.token_urlsafe(18)
    return HTMLResponse(
        _PAGE.replace(_NONCE_TOKEN, nonce),
        headers=_security_headers(nonce),
    )
