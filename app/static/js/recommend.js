class RecommendApi {
  constructor(base = "/api") {
    this.base = base;
  }

  async fetchRecommendations({ tf = "1M", page = 1, page_size = 20 } = {}) {
    const url = `${this.base}/recommendations?tf=${encodeURIComponent(
      tf
    )}&page=${page}&page_size=${page_size}`;
    const res = await fetch(url, { cache: "no-cache" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (!json || json.status !== "ok") throw new Error("Invalid response");
    return json;
  }
}

function parseDate(v) {
  if (!v) return null;
  const d = new Date(v);
  return isNaN(d) ? null : d;
}

function labelKey(v) {
  return v ? String(v).toLowerCase() : "none";
}

const DEFAULT_COLORS = {
  buy: "#0f9d58",
  sell: "#db4437",
  strong: "#4285f4",
  weak: "#f4b400",
};

class TimelineGantt {
  constructor(opts = {}) {
    this.tf = opts.tf || "1M";
    this.pageSize = opts.pageSize || 15;

    this.chartEl = document.getElementById(opts.chartId || "ganttChart");
    this.paginationEl = document.getElementById(
      opts.paginationId || "pagination"
    );

    this.api = new RecommendApi(opts.base || "/api");
    this.page = 1;
    this.totalPages = 1;
    this.tfButtons = document.querySelectorAll(".tf-btn");
    google.charts.load("current", { packages: ["timeline"] });
    google.charts.setOnLoadCallback(() => {
      this.setupTfButtons();
      this.loadPage(1);
    });
  }

  setupTfButtons() {
    if (!this.tfButtons) return;
    this.tfButtons.forEach((btn) => {
      btn.addEventListener("click", async () => {
        const tf = btn.dataset.tf;
        if (!tf) return;
        this.tf = tf;
        console.log("Timeframe changed to:", this.tf);
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

  async loadPage(page = 1) {
    page = Math.max(1, Math.floor(page));
    this.page = page;
    try {
      const res = await this.api.fetchRecommendations({
        tf: this.tf,
        page: this.page,
        page_size: this.pageSize,
      });
      const records = Array.isArray(res.records) ? res.records : [];
      this.totalPages = Math.max(1, Number(res.total_pages) || 1);
      console.log("DATA RAW (first 2) =>", records.slice(0, 2));
      if (this.page > this.totalPages) {
        this.page = this.totalPages;
        const res2 = await this.api.fetchRecommendations({
          tf: this.tf,
          page: this.page,
          page_size: this.pageSize,
        });
        this.renderTimeline(res2.records || []);
        this.renderPagination(this.totalPages, this.page);
        return;
      }
      this.renderTimeline(records);
      this.renderPagination(this.totalPages, this.page);
    } catch (err) {
      console.error("loadPage error:", err);
      if (this.chartEl)
        this.chartEl.innerHTML =
          "<div class='text-center text-danger p-3'>Lỗi tải dữ liệu</div>";
      if (this.paginationEl) this.paginationEl.innerHTML = "";
    }
  }

  renderTimeline(records) {
    if (!this.chartEl) return;
    const dataTable = new google.visualization.DataTable();
    dataTable.addColumn({ type: "string", id: "Row" });
    dataTable.addColumn({ type: "string", id: "Bar" });
    dataTable.addColumn({ type: "date", id: "Start" });
    dataTable.addColumn({ type: "date", id: "End" });
    const rows = records
      .map((r) => {
        const start = parseDate(r.t0);
        const end = parseDate(r.t1);
        if (!start || !end) return null;
        return {
          key: labelKey(r.label),
          start,
          end,
        };
      })
      .filter((x) => x);
    if (!rows.length) {
      this.chartEl.innerHTML =
        "<div class='text-center text-muted p-3'>Không có dữ liệu</div>";
      return;
    }
    const labelOrder = Object.keys(DEFAULT_COLORS);
    const extra = [
      ...new Set(rows.map((r) => r.key).filter((k) => !labelOrder.includes(k))),
    ];
    const uniqueLabels = labelOrder.concat(extra);
    const rowMap = {};
    uniqueLabels.forEach((key) => (rowMap[key] = []));
    rows.forEach((r) => rowMap[r.key].push(r));
    const tableRows = [];
    uniqueLabels.forEach((key) => {
      if (rowMap[key].length === 0) {
        const now = new Date();
        tableRows.push([
          key.toUpperCase(),
          "",
          now,
          new Date(now.getTime() + 1),
        ]);
      } else {
        rowMap[key].forEach((r) =>
          tableRows.push([key.toUpperCase(), "", r.start, r.end])
        );
      }
    });
    dataTable.addRows(tableRows);
    const colors = uniqueLabels.map(
      (k) => DEFAULT_COLORS[k] || DEFAULT_COLORS.none
    );
    const rowCount = uniqueLabels.length;
    const height = Math.max(200, rowCount * 50 + 80);
    this.chartEl.style.width = "100%";
    this.chartEl.style.height = height + "px";
    const starts = rows.map((r) => r.start.getTime());
    const ends = rows.map((r) => r.end.getTime());
    const minT = new Date(Math.min(...starts));
    const maxT = new Date(Math.max(...ends));
    const ticks = [];
    if (this.tf === "1M") {
      let d = new Date(minT.getFullYear(), minT.getMonth(), 1);
      const lim = new Date(maxT.getFullYear(), maxT.getMonth() + 1, 1);
      while (d <= lim) {
        ticks.push(new Date(d));
        d.setMonth(d.getMonth() + 1);
      }
    } else if (this.tf === "1D") {
      let d = new Date(minT);
      while (d <= maxT) {
        ticks.push(new Date(d));
        d.setDate(d.getDate() + 1);
      }
    } else if (this.tf === "1H") {
      let d = new Date(minT);
      while (d <= maxT) {
        ticks.push(new Date(d));
        d.setHours(d.getHours() + 1);
      }
    }
    const options = {
      height,
      colors,
      timeline: {
        colorByRowLabel: true,
        showRowLabels: true,
      },
      hAxis: { ticks },
    };
    const chart = new google.visualization.Timeline(this.chartEl);
    chart.draw(dataTable, options);
  }

  renderPagination(totalPages, current) {
    const ul = this.paginationEl;
    if (!ul) return;
    if (totalPages <= 1) {
      ul.innerHTML = "";
      return;
    }
    const maxButtons = 5;
    const make = (text, page, disabled, active) => `
      <li class="page-item ${disabled ? "disabled" : ""} ${
      active ? "active" : ""
    }">
        <a class="page-link" data-page="${page}" href="#">${text}</a>
      </li>
    `;
    let html = "";
    html += make("Prev", Math.max(1, current - 1), current <= 1, false);
    let start = Math.max(1, current - 2);
    let end = Math.min(totalPages, start + maxButtons - 1);
    if (end - start < maxButtons - 1) {
      start = Math.max(1, end - maxButtons + 1);
    }
    if (start > 1) {
      html += make("1", 1, false, current === 1);
      if (start > 2)
        html += `<li class="page-item disabled"><span class="page-link">…</span></li>`;
    }
    for (let p = start; p <= end; p++) {
      html += make(String(p), p, false, p === current);
    }
    if (end < totalPages) {
      if (end < totalPages - 1)
        html += `<li class="page-item disabled"><span class="page-link">…</span></li>`;
      html += make(
        String(totalPages),
        totalPages,
        false,
        current === totalPages
      );
    }
    if (current >= totalPages) {
      html += make("Next", totalPages, true, false);
    } else {
      html += make("Next", current + 1, false, false);
    }
    ul.innerHTML = html;
    ul.querySelectorAll("a.page-link").forEach((a) => {
      a.addEventListener("click", (e) => {
        e.preventDefault();
        const p = Number(a.dataset.page);
        if (!p || p < 1 || p > totalPages) return;
        if (p === this.page) return;
        this.loadPage(p);
      });
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (!document.getElementById("ganttChart")) return;
  window.TimelineGanttApp = new TimelineGantt({
    chartId: "ganttChart",
    paginationId: "pagination",
    pageSize: 15,
    tf: "1M",
  });
});
