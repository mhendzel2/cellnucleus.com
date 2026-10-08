(function () {
    "use strict";

    if (document.querySelector(".cn-site-sidebar")) {
        return;
    }

    var rootPrefix = getRootPrefix();
    var currentPath = normalizePath(window.location.pathname || "");

    var items = [
        {
            label: "Home",
            href: "index.html",
            match: ["index.html", ""],
            icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 10.8 12 3l9 7.8v9.7a.8.8 0 0 1-.8.8h-5.1v-6.7H8.9v6.7H3.8a.8.8 0 0 1-.8-.8v-9.7Z"/></svg>'
        },
        {
            label: "Nuclear Structure",
            href: "structures_enhanced.html",
            match: ["structures_enhanced.html", "enhanced_structures_database.html"],
            icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.2c2.9 0 5.3 3.9 5.3 8.8s-2.4 8.8-5.3 8.8S6.7 16.9 6.7 12 9.1 3.2 12 3.2Zm0 2c-1.4 0-3.3 2.7-3.3 6.8s1.9 6.8 3.3 6.8 3.3-2.7 3.3-6.8S13.4 5.2 12 5.2Z"/><path d="M4 7.2c1.4-2.5 5.9-2.3 10.1.1s6.6 6.2 5.1 8.7-5.9 2.3-10.1-.1S2.5 9.7 4 7.2Zm1.7 1c-.7 1.2 1 4 4.4 5.9s6.7 2.1 7.4.8-1-4-4.4-5.9-6.7-2-7.4-.8Z"/><circle cx="12" cy="12" r="2.1"/></svg>'
        },
        {
            label: "Microscopy",
            href: "video_gallery.html",
            match: ["video_gallery.html", "live_cell_enhanced.html"],
            icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10.4 4.2h3.2v7.2h-3.2V4.2Zm-1.8 8.9h6.8v2H8.6v-2Zm-2.8 3.4h12.4v2H5.8v-2Z"/><path d="m14.3 5.6 2.9-1.5 3.4 6.5-2.9 1.5-3.4-6.5ZM4.8 19.2h14.4v2H4.8v-2Z"/></svg>'
        },
        {
            label: "Research Reviews",
            href: "research_reviews_directory.html",
            match: ["research_reviews_directory.html", "complete_reviews_index_final.html", "nuclear_biology_reviews_index.html"],
            icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4.5c0-.6.4-1 1-1h12c.6 0 1 .4 1 1v15c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-15Zm2 1v13h10v-13H7Z"/><path d="M8.7 8h6.6v1.8H8.7V8Zm0 3.1h6.6v1.8H8.7v-1.8Zm0 3.1h4.4V16H8.7v-1.8Z"/></svg>'
        },
        {
            label: "Hypothesis Reviews",
            href: "hypothesis_reviews_index.html",
            match: ["hypothesis_reviews_index.html"],
            icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M11 3.5h2v11h-2v-11Zm0 13h2v2h-2v-2Z"/><path d="M4.8 4.8h4.5v2H6.8v10.4h10.4v-2.5h2v4.5H4.8V4.8Zm9.9 0h4.5v4.5h-2V8.2l-5.1 5.1-1.4-1.4 5.1-5.1h-1.1v-2Z"/></svg>'
        },
        {
            label: "Research Resources",
            href: "resources_databases.html",
            match: ["resources_databases.html", "resources_tools.html", "resources_protocols.html", "resources_literature.html", "resources_consortia.html", "resources_community.html", "resources_funding.html"],
            icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 4.2h7.2c1.2 0 2.2.4 2.8 1.1.6-.7 1.6-1.1 2.8-1.1H20v14.6h-3.2c-1 0-1.8.2-2.4.7l-.4.3-.4-.3c-.6-.5-1.4-.7-2.4-.7H4V4.2Zm2 2v10.6h5.2c.7 0 1.4.1 1.8.3V7c-.3-.5-.9-.8-1.8-.8H6Zm9 10.9c.5-.2 1.1-.3 1.8-.3H18V6.2h-1.2c-.9 0-1.5.3-1.8.8v10.1Z"/></svg>'
        },
        {
            label: "All Reviews",
            href: "reviews_index.html",
            match: ["reviews_index.html"],
            icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.2h16v2H4v-2Zm0 5.8h16v2H4v-2Zm0 5.8h16v2H4v-2Z"/></svg>'
        },
        {
            label: "Downloads",
            href: "downloads.html",
            match: ["downloads.html"],
            icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M11 4h2v8.2l2.8-2.8 1.4 1.4L12 16l-5.2-5.2 1.4-1.4 2.8 2.8V4Z"/><path d="M5 18h14v2H5v-2Z"/></svg>'
        },
        {
            label: "Educational Resources",
            href: "live_cell_enhanced.html",
            match: ["live_cell_enhanced.html", "phase1_complete.html"],
            icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 10 5-10 5L2 8l10-5Zm0 7.8L17.5 8 12 5.2 6.5 8l5.5 2.8Z"/><path d="M5 10.6 7 11.7v4.1c0 .8 2 2.2 5 2.2s5-1.4 5-2.2v-4.1l2-1.1v5.2c0 2.6-3.5 4.2-7 4.2s-7-1.6-7-4.2v-5.2Z"/></svg>'
        },
        {
            label: "Review Audit",
            href: "review_audit.html",
            match: ["review_audit.html"],
            icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 3h14v18H5V3Zm2 2v14h10V5H7Zm2 3h6v2H9V8Zm0 4h6v2H9v-2Zm0 4h4v2H9v-2Z"/></svg>'
        },
        {
            label: "About",
            href: "about.html",
            match: ["about.html"],
            icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M11 10h2v8h-2v-8Zm0-4h2v2h-2V6Z"/><path d="M12 2.8a9.2 9.2 0 1 1 0 18.4 9.2 9.2 0 0 1 0-18.4Zm0 2a7.2 7.2 0 1 0 0 14.4 7.2 7.2 0 0 0 0-14.4Z"/></svg>'
        }
    ];

    removeLegacySidebar();

    var sidebar = document.createElement("aside");
    sidebar.className = "cn-site-sidebar";
    sidebar.id = "cn-site-navigation";
    sidebar.style.overflowY = "auto";
    sidebar.setAttribute("aria-label", "Site navigation");
    sidebar.innerHTML = [
        '<div class="cn-sidebar-brand">',
        '  <a class="cn-brand-link" href="' + rootPrefix + 'index.html">',
        '    <img src="' + rootPrefix + 'assets/images/logo.png" alt="CellNucleus logo">',
        '    <span><strong>CellNucleus.com</strong><small>Owned and operated by Gnometrix Labs</small></span>',
        '  </a>',
        '  <p style="margin:0.75rem 0 0;font-size:0.8rem;color:#475569">Owned and operated by <a href="https://www.gnometrix.com/">Gnometrix Labs</a></p>',
        '</div>',
        '<nav class="cn-sidebar-menu">',
        items.map(renderItem).join(""),
        '</nav>',
        '<p style="padding:0 1.25rem 1.25rem;font-size:0.8rem;overflow-wrap:anywhere"><a href="mailto:cellnucleus@gnometrix.com">cellnucleus@gnometrix.com</a></p>'
    ].join("");

    var toggle = document.createElement("button");
    toggle.className = "cn-sidebar-toggle";
    toggle.type = "button";
    toggle.setAttribute("aria-label", "Toggle site navigation");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-controls", sidebar.id);
    toggle.innerHTML = '<span></span><span></span><span></span>';

    var scrim = document.createElement("div");
    scrim.className = "cn-sidebar-scrim";
    scrim.setAttribute("aria-hidden", "true");

    document.body.insertBefore(scrim, document.body.firstChild);
    document.body.insertBefore(sidebar, document.body.firstChild);
    document.body.insertBefore(toggle, document.body.firstChild);
    document.body.classList.add("cn-sidebar-mounted");

    var mobileLayout = window.matchMedia("(max-width: 1023px)");
    syncSidebar();
    if (mobileLayout.addEventListener) {
        mobileLayout.addEventListener("change", syncSidebar);
    } else {
        mobileLayout.addListener(syncSidebar);
    }

    toggle.addEventListener("click", function () {
        if (document.body.classList.contains("cn-sidebar-open")) {
            closeSidebar();
        } else {
            document.body.classList.add("cn-sidebar-open");
            toggle.setAttribute("aria-expanded", "true");
            syncSidebar();
            sidebar.querySelector("a").focus();
        }
    });

    scrim.addEventListener("click", closeSidebar);
    document.addEventListener("keydown", function (event) {
        if (!mobileLayout.matches || !document.body.classList.contains("cn-sidebar-open")) {
            return;
        }
        if (event.key === "Escape") {
            closeSidebar();
        } else if (event.key === "Tab") {
            var links = sidebar.querySelectorAll("a[href]");
            var lastLink = links[links.length - 1];
            if (event.shiftKey && document.activeElement === toggle) {
                event.preventDefault();
                lastLink.focus();
            } else if (!event.shiftKey && document.activeElement === lastLink) {
                event.preventDefault();
                toggle.focus();
            }
        }
    });

    function renderItem(item) {
        var href = rootPrefix + item.href;
        var active = isActive(item);
        return [
            '<a class="cn-sidebar-link' + (active ? " is-active" : "") + '" href="' + href + '"' + (active ? ' aria-current="page"' : "") + '>',
            '  <span class="cn-sidebar-icon">' + item.icon + '</span>',
            '  <span>' + item.label + '</span>',
            '</a>'
        ].join("");
    }

    function isActive(item) {
        var filename = currentPath.split("/").pop() || "index.html";
        if (item.match.indexOf(filename) !== -1) {
            return true;
        }
        if (currentPath.indexOf("/nuclear_biology_reviews/reviews/") !== -1 && item.href === "research_reviews_directory.html") {
            return true;
        }
        if (currentPath.indexOf("/hypothesis_reviews/") !== -1 && item.href === "hypothesis_reviews_index.html") {
            return true;
        }
        return false;
    }

    function closeSidebar() {
        document.body.classList.remove("cn-sidebar-open");
        toggle.setAttribute("aria-expanded", "false");
        syncSidebar();
        if (mobileLayout.matches) {
            toggle.focus();
        }
    }

    function syncSidebar() {
        var hidden = mobileLayout.matches && !document.body.classList.contains("cn-sidebar-open");
        sidebar.inert = hidden;
        if (hidden) {
            sidebar.setAttribute("aria-hidden", "true");
        } else {
            sidebar.removeAttribute("aria-hidden");
        }
        if (!mobileLayout.matches) {
            document.body.classList.remove("cn-sidebar-open");
            toggle.setAttribute("aria-expanded", "false");
        }
    }

    function getRootPrefix() {
        var script = document.currentScript;
        if (script && script.src) {
            return new URL("../../", script.src).href;
        }
        var path = normalizePath(window.location.pathname || "");
        if (path.indexOf("/nuclear_biology_reviews/reviews/") !== -1) {
            return "../../";
        }
        if (path.indexOf("/nuclear_biology_reviews/") !== -1) {
            return "../";
        }
        if (path.indexOf("/hypothesis_reviews/") !== -1 || path.indexOf("/education/") !== -1) {
            return "../";
        }
        return "";
    }

    function normalizePath(path) {
        return path.replace(/\\/g, "/");
    }

    function removeLegacySidebar() {
        var legacy = document.querySelector("body > .flex.min-h-screen > .w-72");
        if (legacy && legacy.querySelector(".sidebar-link")) {
            legacy.remove();
        }
    }
}());

/* Archived Word status runs independently of sidebar mounting and URL confidence. */
(function () {
    "use strict";
    var warning = "Archived Word draft — not reconciled with the revised HTML; scientific validation incomplete.";
    var labels = {download: "Download Word draft", open: "Open Word draft", correction: "Suggest a draft correction"};
    function classify(link) {
        if (labels[link.getAttribute("data-cn-word-archive")]) { return link.getAttribute("data-cn-word-archive"); }
        var url;
        try { url = new URL(link.getAttribute("href"), document.baseURI); } catch (error) { return null; }
        if (url.origin !== window.location.origin) { return null; }
        if (/\.doc(?:x|m)?$/i.test(url.pathname)) { return "download"; }
        if (/\/review_source_viewer\.html$/i.test(url.pathname)) {
            return url.hash === "#suggestion-form" || /suggest/i.test(link.textContent) ? "correction" : "open";
        }
        return null;
    }
    function qualify(link) {
        var action = classify(link);
        if (!action) { return; }
        var status = link.querySelector(".cn-word-link-status");
        var label = link.querySelector(".cn-word-action-label");
        if (status && status.textContent === warning && label && label.textContent === labels[action]) { return; }
        link.setAttribute("data-cn-word-archive", action);
        link.setAttribute("title", warning);
        link.setAttribute("aria-label", labels[action] + ": " + warning);
        label = document.createElement("span");
        label.className = "cn-word-action-label";
        label.textContent = labels[action];
        status = document.createElement("span");
        status.className = "cn-word-link-status";
        status.textContent = warning;
        link.replaceChildren(label, status);
    }
    function qualifyAll() { document.querySelectorAll("a[href], a[data-cn-word-archive]").forEach(qualify); }
    qualifyAll();
    new MutationObserver(function () { qualifyAll(); }).observe(document.body, {childList: true, subtree: true, attributes: true, attributeFilter: ["href"]});
}());
