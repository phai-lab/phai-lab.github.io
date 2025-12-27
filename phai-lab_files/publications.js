(function () {
  const root = document.getElementById("pubs-root");
  const errorEl = document.getElementById("pubs-error");

  function el(tag, attrs, children) {
    const node = document.createElement(tag);
    if (attrs) {
      for (const [k, v] of Object.entries(attrs)) {
        if (k === "class") node.className = v;
        else if (k === "text") node.textContent = v;
        else node.setAttribute(k, v);
      }
    }
    if (children) {
      for (const c of children) node.appendChild(c);
    }
    return node;
  }

  function showError(msg) {
    if (!errorEl) return;
    errorEl.style.display = "block";
    errorEl.textContent = msg;
  }

  function groupByYear(items) {
    const map = new Map();
    for (const it of items) {
      const year = it.year || "Unknown";
      if (!map.has(year)) map.set(year, []);
      map.get(year).push(it);
    }
    // years desc, Unknown last
    const years = Array.from(map.keys()).sort((a, b) => {
      if (a === "Unknown") return 1;
      if (b === "Unknown") return -1;
      return Number(b) - Number(a);
    });
    return years.map((y) => [y, map.get(y)]);
  }

  function render(items) {
    if (!root) return;
    root.innerHTML = "";

    const grouped = groupByYear(items);
    for (const [year, yearItems] of grouped) {
      root.appendChild(el("h3", { class: "pub-year", text: String(year) }));
      const list = el("ol", null);

      for (const it of yearItems) {
        const linkHref = it.external_url || it.scholar_url || "#";
        const titleLink = el("a", {
          href: linkHref,
          target: "_blank",
          rel: "noopener",
          class: "pub-title",
        });
        titleLink.textContent = it.title || "(untitled)";

        const metaLines = [];
        if (it.authors) metaLines.push(it.authors);
        if (it.venue) metaLines.push(it.venue);

        const meta = el("div", { class: "pub-meta", text: metaLines.join(" · ") });
        const li = el("li", { class: "pub-item" }, [titleLink, meta]);
        list.appendChild(li);
      }

      root.appendChild(list);
    }
  }

  fetch("./data/publications_since_2020.json", { cache: "no-store" })
    .then((r) => {
      if (!r.ok) throw new Error(`Failed to load publications: ${r.status}`);
      return r.json();
    })
    .then((data) => {
      const items = (data && data.items) || [];
      render(items);
    })
    .catch((err) => {
      showError(String(err && err.message ? err.message : err));
    });
})();



