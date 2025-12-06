class RecommendApi {
  constructor(base = "/api") {
    this.base = base;
  }

  async fetchRecommendations({ tf = "1M", page = 1, page_size = 20 } = {}) {
    const url = `${this.base}/recommendations?tf=${encodeURIComponent(
      tf
    )}&page=${page}&page_size=${page_size}`;
    const res = await fetch(url, { cache: "no-cache" });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    const json = await res.json();
    if (!json || json.status !== "ok") {
      throw new Error("Invalid response");
    }
    return json;
  }
}

function safeGet(rec, keys) {
  for (const k of keys) {
    if (rec[k] !== undefined && rec[k] !== null) return rec[k];
  }
  return null;
}

function parseDate(value) {
  if (!value) return null;
  if (typeof value === "number") return new Date(value);
  if (
    !isNaN(value) &&
    String(value).length >= 10 &&
    String(value).length <= 13
  ) {
    const n = Number(value);
    return new Date(n);
  }
  const d = new Date(value);
  if (!isNaN(d)) return d;
  return null;
}

function fmtDate(dt) {
  if (!dt) return "—";
  try {
    const opts = {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    };
    return dt.toLocaleString(undefined, opts).replace(",", "");
  } catch (e) {
    return dt.toString();
  }
}

function mapLabel(label) {
  if (!label) return { text: "—", cls: "badge bg-secondary" };
  const low = String(label).toLowerCase();
  switch (low) {
    case "buy":
      return { text: "MUA", cls: "badge bg-success" };
    case "sell":
      return { text: "BÁN", cls: "badge bg-danger" };
    case "strong":
      return { text: "MẠNH", cls: "badge bg-primary" };
    case "weak":
      return { text: "YẾU", cls: "badge bg-warning text-dark" };
    case "none":
    default:
      return { text: String(label).toUpperCase(), cls: "badge bg-secondary" };
  }
}

class RecommendApp {
  constructor(opts = {}) {
    this.tf = opts.tf || "1M";
    this.page = 1;
    this.pageSize = opts.pageSize || 20;
    this.api = new RecommendApi(opts.base || "/api");
    this.tfButtons = document.querySelectorAll(".tf-btn");
    this.tbody = document.querySelector("#reco-table tbody");
    this.pagination = document.getElementById("pagination");
    this.init();
  }

  init() {
    this.setupTfButtons();
    this.loadPage(1);
  }

  setupTfButtons() {
    if (!this.tfButtons) return;
    this.tfButtons.forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        const tf = btn.dataset.tf;
        if (!tf) return;
        this.tf = tf;
        this.tfButtons.forEach((b) => {
          b.classList.remove("active", "btn-primary");
          b.classList.add("btn-outline-primary");
        });
        btn.classList.add("active", "btn-primary");
        btn.classList.remove("btn-outline-primary");
        await this.loadPage(1);
      });
    });
  }

  showLoadingRow() {
    if (!this.tbody) return;
    this.tbody.innerHTML = `
      <tr>
        <td colspan="3" class="text-center py-4">
          <div class="spinner-border" role="status" aria-hidden="true"></div>
          <div class="small mt-2">Đang tải...</div>
        </td>
      </tr>`;
  }

  showEmpty() {
    if (!this.tbody) return;
    this.tbody.innerHTML = `
      <tr>
        <td colspan="3" class="text-center text-muted py-4">Không có dữ liệu</td>
      </tr>`;
  }

  async loadPage(page = 1) {
    this.page = page;
    if (!this.tbody) return;
    this.showLoadingRow();
    try {
      const res = await this.api.fetchRecommendations({
        tf: this.tf,
        page: this.page,
        page_size: this.pageSize,
      });
      const records = Array.isArray(res.records) ? res.records : [];
      const totalPages = Number(res.total_pages) || 1;
      if (!records.length) {
        this.showEmpty();
      } else {
        this.renderRows(records);
      }
      this.renderPagination(totalPages, this.page);
    } catch (err) {
      console.error("Error loading recommendations", err);
      this.tbody.innerHTML = `
        <tr>
          <td colspan="3" class="text-center text-danger py-4">Lỗi khi tải dữ liệu: ${err.message}</td>
        </tr>`;
      this.pagination.innerHTML = "";
    }
  }

  renderRows(records) {
    const rows = records.map((rec) => {
      const t0v = safeGet(rec, [
        "t0",
        "t0_str",
        "timestamp_start",
        "timestamp0",
        "start",
        "from",
      ]);
      const t1v = safeGet(rec, [
        "t1",
        "t1_str",
        "timestamp_end",
        "timestamp1",
        "end",
        "to",
      ]);
      const d0 = parseDate(t0v);
      const d1 = parseDate(t1v);
      const lbl = safeGet(rec, ["label", "Label", "recommendation", "action"]);
      const mapped = mapLabel(lbl);

      return `
        <tr>
          <td style="width:40%">${fmtDate(d0)}</td>
          <td style="width:40%">${fmtDate(d1)}</td>
          <td style="width:20%"><span class="${mapped.cls}">${
        mapped.text
      }</span></td>
        </tr>`;
    });
    this.tbody.innerHTML = rows.join("\n");
  }

  renderPagination(totalPages, current) {
    const maxButtons = 7;
    const ul = this.pagination;
    if (!ul) return;
    if (totalPages <= 1) {
      ul.innerHTML = "";
      return;
    }
    const createLi = (text, disabled, active, page) => {
      const cls = `page-item ${disabled ? "disabled" : ""} ${
        active ? "active" : ""
      }`.trim();
      const aria = active ? 'aria-current="page"' : "";
      const inner = `<a class="page-link" href="#" data-page="${page}" ${aria}>${text}</a>`;
      return `<li class="${cls}">${inner}</li>`;
    };
    const parts = [];
    parts.push(createLi("Prev", current <= 1, false, current - 1));
    let start = Math.max(1, current - Math.floor(maxButtons / 2));
    let end = start + maxButtons - 1;
    if (end > totalPages) {
      end = totalPages;
      start = Math.max(1, end - maxButtons + 1);
    }
    if (start > 1) {
      parts.push(createLi("1", false, current === 1, 1));
      if (start > 2)
        parts.push(
          `<li class="page-item disabled"><span class="page-link">…</span></li>`
        );
    }
    for (let p = start; p <= end; p++) {
      parts.push(createLi(String(p), false, p === current, p));
    }
    if (end < totalPages) {
      if (end < totalPages - 1)
        parts.push(
          `<li class="page-item disabled"><span class="page-link">…</span></li>`
        );
      parts.push(
        createLi(String(totalPages), false, current === totalPages, totalPages)
      );
    }
    parts.push(createLi("Next", current >= totalPages, false, current + 1));
    ul.innerHTML = parts.join("\n");
    ul.querySelectorAll("a.page-link").forEach((a) => {
      a.addEventListener("click", (e) => {
        e.preventDefault();
        const li = a.closest(".page-item");
        if (
          !li ||
          li.classList.contains("disabled") ||
          li.classList.contains("active")
        )
          return;
        const p = Number(a.dataset.page) || 1;
        this.loadPage(p);
      });
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (!document.querySelector("#reco-table")) return;
  window.recommendApp = new RecommendApp({ pageSize: 15 });
});
