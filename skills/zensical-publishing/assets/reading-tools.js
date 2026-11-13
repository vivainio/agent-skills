// Reading tools for Zensical books (styles in reading-tools.css; installed by
// the zensical-publishing skill):
//  - toolbar on wide screens: hide the navigation ( [ ), hide the table of
//    contents ( ] ), use the full window width ( \ ); remembered across pages
//  - "Full screen" button above every plain table
//  - click a Mermaid diagram to open it full screen, scaled to fit, with zoom
//    (buttons, + / - / 0, Ctrl or pinch + wheel) and drag to pan
//  Esc closes a full-screen view.
// Layout toggles adapted from basware/rosetta-docs.
(function () {
  // Zensical renders each Mermaid diagram into a closed shadow root, which
  // leaves no way to read the SVG back. Opening it only for diagram hosts
  // lets the zoom view copy the rendered diagram instead of re-rendering it.
  // This script loads before the diagrams render, which waits for Mermaid.
  var attachShadow = Element.prototype.attachShadow;
  Element.prototype.attachShadow = function (init) {
    if (init && init.mode === "closed" && this.classList.contains("mermaid")) {
      init = Object.assign({}, init, { mode: "open" });
    }
    return attachShadow.call(this, init);
  };

  var KEY = "onp-docs-layout";
  var FLAGS = { nav: "od-hide-nav", toc: "od-hide-toc", wide: "od-wide" };

  function load() {
    try {
      return JSON.parse(localStorage.getItem(KEY)) || {};
    } catch (e) {
      return {};
    }
  }
  function save(state) {
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
    } catch (e) {
      /* storage unavailable: the toggle still works for this page */
    }
  }

  var state = load();

  function apply() {
    Object.keys(FLAGS).forEach(function (k) {
      document.documentElement.classList.toggle(FLAGS[k], !!state[k]);
    });
    document.querySelectorAll(".od-toolbar button").forEach(function (b) {
      b.setAttribute("aria-pressed", String(!!state[b.dataset.key]));
    });
  }

  function toggle(key) {
    state[key] = !state[key];
    save(state);
    apply();
  }

  function button(text, title, onClick, className) {
    var b = document.createElement("button");
    b.type = "button";
    b.textContent = text;
    if (title) b.title = title;
    if (className) b.className = className;
    b.addEventListener("click", onClick);
    return b;
  }

  function buildToolbar() {
    if (document.querySelector(".od-toolbar")) return;
    var bar = document.createElement("div");
    bar.className = "od-toolbar";
    [
      ["nav", "Nav", "Hide or show the navigation ( [ )"],
      ["toc", "TOC", "Hide or show the table of contents ( ] )"],
      ["wide", "Wide", "Use the full window width ( \\ )"],
    ].forEach(function (d) {
      var b = button(d[1], d[2], function () {
        toggle(d[0]);
      });
      b.dataset.key = d[0];
      bar.appendChild(b);
    });
    document.body.appendChild(bar);
  }

  // Full-screen overlay shared by tables and diagrams. Returns its body;
  // extra controls go into the bar before the Close button.
  var onOverlayKey = null;

  function closeOverlay() {
    var o = document.querySelector(".od-overlay");
    if (o) o.remove();
    onOverlayKey = null;
    document.documentElement.classList.remove("od-overlay-open");
  }

  function openOverlay(controls) {
    closeOverlay();
    var overlay = document.createElement("div");
    overlay.className = "od-overlay md-typeset";
    var bar = document.createElement("div");
    bar.className = "od-overlay__bar";
    var label = document.createElement("span");
    label.textContent = document.title.replace(/ - .*$/, "") + " (Esc to close)";
    var tools = document.createElement("span");
    tools.className = "od-overlay__tools";
    (controls || []).forEach(function (c) {
      tools.appendChild(c);
    });
    tools.appendChild(button("Close", null, closeOverlay));
    bar.appendChild(label);
    bar.appendChild(tools);
    var body = document.createElement("div");
    body.className = "od-overlay__body";
    overlay.appendChild(bar);
    overlay.appendChild(body);
    document.body.appendChild(overlay);
    document.documentElement.classList.add("od-overlay-open");
    return body;
  }

  function buildTableTools() {
    document.querySelectorAll(".md-typeset table:not([class])").forEach(function (table) {
      if (table.closest(".od-overlay")) return;
      var anchor = table.closest(".md-typeset__scrollwrap") || table;
      var prev = anchor.previousElementSibling;
      if (prev && prev.classList.contains("od-table-tools")) return;
      var tools = document.createElement("div");
      tools.className = "od-table-tools";
      tools.appendChild(
        button("Full screen", "Open this table in a full-screen view", function () {
          openOverlay().appendChild(table.cloneNode(true));
        })
      );
      anchor.parentNode.insertBefore(tools, anchor);
    });
  }

  // Diagrams ---------------------------------------------------------------

  var MIN_SCALE = 0.1;
  var MAX_SCALE = 8;
  var STEP = 1.25;

  function openDiagram(host) {
    var source = host.shadowRoot && host.shadowRoot.querySelector("svg");
    if (!source) return;
    var box = source.viewBox && source.viewBox.baseVal;
    var width = box && box.width ? box.width : source.getBoundingClientRect().width;
    var height = box && box.height ? box.height : source.getBoundingClientRect().height;

    var scale = 1;
    var fitScale = 1;
    var svg;

    function render() {
      svg.style.width = width * scale + "px";
      svg.style.height = height * scale + "px";
    }

    // Zoom around a point in the viewport (the centre by default), so the
    // part of the diagram under the pointer stays where it is.
    function zoomTo(next, clientX, clientY) {
      next = Math.min(MAX_SCALE, Math.max(MIN_SCALE, next));
      var rect = body.getBoundingClientRect();
      var x = (clientX === undefined ? rect.left + rect.width / 2 : clientX) - rect.left;
      var y = (clientY === undefined ? rect.top + rect.height / 2 : clientY) - rect.top;
      var stageRect = stage.getBoundingClientRect();
      var fx = (x + rect.left - stageRect.left) / stageRect.width;
      var fy = (y + rect.top - stageRect.top) / stageRect.height;
      scale = next;
      render();
      body.scrollLeft = fx * stage.offsetWidth - x;
      body.scrollTop = fy * stage.offsetHeight - y;
    }

    function fit() {
      scale = fitScale;
      render();
      body.scrollLeft = 0;
      body.scrollTop = 0;
    }

    var body = openOverlay([
      button("−", "Zoom out ( - )", function () {
        zoomTo(scale / STEP);
      }),
      button("Fit", "Fit to window ( 0 )", fit),
      button("+", "Zoom in ( + )", function () {
        zoomTo(scale * STEP);
      }),
    ]);
    body.classList.add("od-overlay__body--diagram");

    var stage = document.createElement("div");
    stage.className = "od-diagram-stage mermaid";
    body.appendChild(stage);
    // An open shadow root of its own keeps the diagram's styles and ids
    // isolated from the page, as on the page itself.
    var root = attachShadow.call(stage, { mode: "open" });
    root.innerHTML = host.shadowRoot.innerHTML;
    svg = root.querySelector("svg");
    svg.removeAttribute("width");
    svg.removeAttribute("height");
    svg.style.maxWidth = "none";
    svg.style.display = "block";

    // clientWidth/Height include the body padding; leave it plus a margin.
    var pad = 48;
    fitScale = Math.min((body.clientWidth - pad) / width, (body.clientHeight - pad) / height);
    fitScale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, fitScale));
    fit();

    body.addEventListener(
      "wheel",
      function (e) {
        // Ctrl + wheel, and trackpad pinch (reported as Ctrl + wheel), zoom;
        // a plain wheel scrolls.
        if (!e.ctrlKey && !e.metaKey) return;
        e.preventDefault();
        zoomTo(scale * Math.exp(-e.deltaY * 0.01), e.clientX, e.clientY);
      },
      { passive: false }
    );

    var drag = null;
    body.addEventListener("pointerdown", function (e) {
      if (e.button !== 0) return;
      drag = { x: e.clientX, y: e.clientY, left: body.scrollLeft, top: body.scrollTop };
      body.setPointerCapture(e.pointerId);
      body.classList.add("od-dragging");
    });
    body.addEventListener("pointermove", function (e) {
      if (!drag) return;
      body.scrollLeft = drag.left - (e.clientX - drag.x);
      body.scrollTop = drag.top - (e.clientY - drag.y);
    });
    function endDrag() {
      drag = null;
      body.classList.remove("od-dragging");
    }
    body.addEventListener("pointerup", endDrag);
    body.addEventListener("pointercancel", endDrag);

    onOverlayKey = function (key) {
      if (key === "+" || key === "=") zoomTo(scale * STEP);
      else if (key === "-") zoomTo(scale / STEP);
      else if (key === "0") fit();
      else return false;
      return true;
    };
  }

  function diagramHost(target) {
    var host = target && target.closest && target.closest(".md-typeset div.mermaid");
    if (!host || host.closest(".od-overlay") || !host.shadowRoot) return null;
    return host;
  }

  function markDiagram(host) {
    if (host.dataset.odZoom || host.closest(".od-overlay")) return;
    host.dataset.odZoom = "1";
    host.tabIndex = 0;
    host.setAttribute("role", "button");
    host.title = "Open this diagram full screen";
  }

  document.addEventListener("click", function (e) {
    var host = diagramHost(e.target);
    if (host) openDiagram(host);
  });

  // Diagrams render asynchronously after the page loads; mark each one as it
  // appears so it is focusable and shows a hint.
  new MutationObserver(function () {
    document.querySelectorAll(".md-typeset div.mermaid").forEach(markDiagram);
  }).observe(document.documentElement, { childList: true, subtree: true });

  document.addEventListener("keydown", function (e) {
    var t = e.target;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key === "Escape") {
      closeOverlay();
      return;
    }
    if (document.querySelector(".od-overlay")) {
      if (onOverlayKey && onOverlayKey(e.key)) e.preventDefault();
      return;
    }
    var host = diagramHost(t);
    if (host && (e.key === "Enter" || e.key === " ")) {
      e.preventDefault();
      openDiagram(host);
    } else if (e.key === "[") toggle("nav");
    else if (e.key === "]") toggle("toc");
    else if (e.key === "\\") toggle("wide");
  });

  function init() {
    closeOverlay();
    buildToolbar();
    buildTableTools();
    apply();
  }

  // Apply the saved state immediately to avoid a layout jump, then build the UI.
  apply();
  if (window.document$ && window.document$.subscribe) window.document$.subscribe(init);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
