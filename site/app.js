(function () {
  var FAQ = window.FAQ || [];
  var $ = function (s) { return document.querySelector(s); };
  var fold = function (t) { return (t || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); };
  var strip = function (html) { var d = document.createElement("div"); d.innerHTML = html; return d.textContent || ""; };

  function itemHtml(it, open) {
    return '<details class="qa"' + (open ? " open" : "") + "><summary>" + it.q + "</summary><div>" + it.a + "</div></details>";
  }

  function score(it, terms) {
    var hay = fold(it.q + " " + strip(it.a) + " " + (it.k || ""));
    var qf = fold(it.q), s = 0;
    for (var i = 0; i < terms.length; i++) {
      if (hay.indexOf(terms[i]) === -1) continue;
      s += 1 + (qf.indexOf(terms[i]) !== -1 ? 2 : 0);
    }
    return s;
  }

  function search(query) {
    var terms = fold(query).split(/[^a-z0-9.]+/).filter(function (t) { return t.length > 2; });
    if (!terms.length) return [];
    return FAQ.map(function (it) { return { it: it, s: score(it, terms) }; })
      .filter(function (x) { return x.s > 0; })
      .sort(function (a, b) { return b.s - a.s; })
      .slice(0, 5).map(function (x) { return x.it; });
  }

  // lista completa
  var list = $("#faqList");
  function renderList(items) {
    list.innerHTML = items.length ? items.map(function (it) { return itemHtml(it, false); }).join("") : '<p class="empty">Nenhuma pergunta encontrada.</p>';
  }
  renderList(FAQ);
  $("#faqFilter").addEventListener("input", function (e) {
    var v = e.target.value.trim();
    renderList(v ? search(v).concat([]) : FAQ);
  });

  // busca do topo
  var box = $("#faq-resultado"), res = $("#faqResults");
  function ask(query) {
    var found = search(query);
    box.classList.remove("hidden");
    res.innerHTML = found.length
      ? found.map(function (it, i) { return itemHtml(it, i === 0); }).join("")
      : '<p class="empty">Não achei isso nesta página. Veja a <a href="#faq">lista completa de perguntas</a> ou o <a href="https://github.com/Andre-Atlas/SUSANNA-HEALTHCHECK/tree/main/docs">repositório</a>.</p>';
    box.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  $("#askForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var v = $("#q").value.trim();
    if (v) ask(v);
  });
  var chips = $("#chips");
  ["Como o ChromaDB funciona?", "Quais modelos de ML são usados?", "Como foi o treinamento?", "O que é SDD?", "O que é o MLflow aqui?", "E em uma emergência?"].forEach(function (t) {
    var b = document.createElement("button");
    b.type = "button"; b.textContent = t;
    b.addEventListener("click", function () { $("#q").value = t; ask(t); });
    chips.appendChild(b);
  });

  // menu: seção ativa
  var links = [].slice.call(document.querySelectorAll("#nav a"));
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (a) { a.classList.toggle("on", a.getAttribute("href") === "#" + en.target.id); });
      });
    }, { rootMargin: "-40% 0px -55% 0px" });
    links.forEach(function (a) { var s = document.querySelector(a.getAttribute("href")); if (s) io.observe(s); });
  }

  // diagramas
  function fallback() {
    [].forEach.call(document.querySelectorAll("pre.mermaid"), function (p) {
      p.classList.add("failed");
      p.setAttribute("title", "Diagrama indisponível (sem acesso ao CDN). Mostrando a descrição em texto.");
    });
  }
  if (window.mermaid) {
    var dark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    window.mermaid.initialize({
      startOnLoad: false, securityLevel: "strict", theme: "base",
      flowchart: { curve: "basis", htmlLabels: true, useMaxWidth: true },
      sequence: { useMaxWidth: true },
      themeVariables: dark
        ? { fontFamily: "Inter, system-ui, sans-serif", fontSize: "14px", background: "#121b2e", primaryColor: "#16233f", primaryBorderColor: "#3b6fd8", primaryTextColor: "#e8eefc", lineColor: "#6aa0ff", secondaryColor: "#1b2c52", tertiaryColor: "#0f1a30", clusterBkg: "#0f1a30", clusterBorder: "#24324f", edgeLabelBackground: "#121b2e", noteBkgColor: "#16233f", actorBkg: "#16233f", actorBorder: "#3b6fd8", actorTextColor: "#e8eefc", signalColor: "#6aa0ff", signalTextColor: "#e8eefc" }
        : { fontFamily: "Inter, system-ui, sans-serif", fontSize: "14px", background: "#ffffff", primaryColor: "#e8f0ff", primaryBorderColor: "#2563eb", primaryTextColor: "#0f1b3d", lineColor: "#2563eb", secondaryColor: "#dbe7ff", tertiaryColor: "#f6f9ff", clusterBkg: "#f6f9ff", clusterBorder: "#dbe4f5", edgeLabelBackground: "#ffffff", actorBkg: "#e8f0ff", actorBorder: "#2563eb", actorTextColor: "#0f1b3d", signalColor: "#2563eb", signalTextColor: "#0f1b3d" }
    });
    window.mermaid.run({ querySelector: "pre.mermaid" }).catch(function () { /* erro de sintaxe isolado */ });
  } else {
    fallback();
  }
})();
