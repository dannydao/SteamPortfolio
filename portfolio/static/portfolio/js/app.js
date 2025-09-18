(function () {
    document.addEventListener("DOMContentLoaded", () => {
        console.log("[SteamPortfolio] app.js loaded");

        // ---------- Helpers -----------
        const $ = (sel, root = document) => root.querySelector(sel);
        const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

        const params = new URLSearchParams(location.search);
        const setParam = (k, v) => {
            if (v == null || v == "") params.delete(k);
            else params.set(k, v);
            const url = `${location.pathname}?${params.toString()}`;
            window.history.replaceState({}, "", url);
        };

        // ---------- Portfolio page widgets ----------
        const grid = $("[data-grid]");
        const cards = grid ? $$("[data-card]", grid) : [];
        const sortSelect = $("[data-sort]");
        const searchInput = $("[data-search]");

        // ----------- lazy-load covers ----------
        const lazyImgs = $$("img[loading='lazy'], img[data-lazy]");
        if ("IntersectionObserver" in window && lazyImgs.length) {
            const io = new IntersectionObserver((entries) => {
                entries.forEach((e) => {
                    if (e.isIntersecting) {
                        const img = e.target;
                        if (img.dataset.src) img.src = img.dataset.src;
                        img.removeAttribute("data-lazy");
                        io.unobserve(img)
                    }
                });
            }, { rootMargin: "200px 0px" });
            lazyImgs.forEach((img) => io.observe(img));
        }

        function sortCards(mode) {
            if (!grid || cards.length === 0) return;
            const list = Array.from(cards);
            list.sort((a, b) => {
                if (mode === "name") {
                    return (a.dataset.name || "").localeCompare(b.dataset.name || "", undefined, { sensitivity: "base"});
                }
                // default: most played (minutes desc)
                const am = +(a.dataset.minutes || 0)
                const bm = +(b.dataset.minutes || 0)
                return bm - am;
            });
            list.forEach((el) => grid.appendChild(el));
        }

        function filterCards(q) {
            if (!grid || cards.length === 0) return;
            const s = (q || "").trim().toLowerCase();
            cards.forEach((el) => {
                const name = (el.dataset.name || "").toLowerCase();
                el.style.display = s ? (name.includes(s) ? "" : "none") : "";
            });
        }

        // Debounce helper for search input
        function debounce(fn, ms = 200) {
            let t;
            return (...args) => {
                clearTimeout(t);
                t = setTimeout(() => fn(...args), ms);
            };
        }

        // Initialize from URL (?sort=minutes|name)
        if (sortSelect) {
            const initialSort = params.get("sort") || sortSelect.value || "minutes";
            sortSelect.value = initialSort;
            sortCards(initialSort)
            sortSelect.addEventListener("change", (e) => {
                const mode = e.target.value;
                setParam("sort", mode);
                sortCards(mode);
            });
        }

        if (searchInput) {
            const initialQuery = params.get("q") || "";
            if (initialQuery) {
                searchInput.value = initialQuery;
                filterCards(initialQuery);
            }
            searchInput.addEventListener("input", debounce((e) => {
                const q = e.target.value;
                setParam("q", q);
                filterCards(q);
            }, 150));
        }

        // ---------- Sync Now button UX ----------
        const syncBtn = $("[data-sync]");
        if (syncBtn) {
            syncBtn.addEventListener("click", (ev) => {
                syncBtn.classList.add("is-loading");
                syncBtn.setAttribute("aria-busy", "true");
                syncBtn.style.pointerEvents = "none";
            });
        }       
    });
})();
