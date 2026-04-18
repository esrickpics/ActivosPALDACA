/**
 * base.js — Layout global (sidebar, colapsar) y chat legacy.
 */

document.addEventListener("DOMContentLoaded", () => {
    const isGlass = document.body.classList.contains("glass-ui");

    initSidebar(isGlass);
    initGlobalSearch();
    initLegacyChat();
});

// ─── Sidebar: flechas de scroll, colapsar con flecha ───────────────────────
function initSidebar(isGlass) {
    const sidebar = document.getElementById("sidebar");
    const menu = document.getElementById("menu");
    const main = document.querySelector("main");
    const arrowUp = document.getElementById("sidebarArrowUp");
    const arrowDown = document.getElementById("sidebarArrowDown");
    const backdrop = document.getElementById("sidebarBackdrop");
    const collapseBtn = document.getElementById("sidebarCollapseBtn");

    if (!sidebar) return;

    /** Glass UI: drawer móvil con clase is-revealed */
    function setGlassMobileReveal(open) {
        sidebar.classList.toggle("is-revealed", open);
        document.body.classList.toggle("sidebar-revealed", open);
        if (menu) {
            menu.setAttribute("aria-expanded", open ? "true" : "false");
            menu.setAttribute("aria-label", open ? "Cerrar menú de navegación" : "Abrir menú de navegación");
        }
    }

    // --- Flechas de scroll (móvil cuando el menú está expandido) ---
    function updateArrowVisibility() {
        if (!arrowUp || !arrowDown) return;
        const isSmallScreen = window.innerWidth <= 500;
        const isExpanded = sidebar.classList.contains("menu-toggle") || sidebar.classList.contains("is-revealed");
        if (isSmallScreen && isExpanded) {
            const hasScroll = sidebar.scrollHeight > sidebar.clientHeight;
            const isAtTop = sidebar.scrollTop <= 5;
            const isAtBottom = sidebar.scrollTop + sidebar.clientHeight >= sidebar.scrollHeight - 5;
            if (hasScroll) {
                arrowUp.style.display = isAtTop ? "none" : "flex";
                arrowDown.style.display = isAtBottom ? "none" : "flex";
                arrowUp.classList.toggle("visible", !isAtTop);
                arrowDown.classList.toggle("visible", !isAtBottom);
            } else {
                arrowUp.style.display = arrowDown.style.display = "none";
                arrowUp.classList.remove("visible");
                arrowDown.classList.remove("visible");
            }
        } else {
            arrowUp.style.display = arrowDown.style.display = "none";
            arrowUp.classList.remove("visible");
            arrowDown.classList.remove("visible");
        }
    }

    if (arrowUp) {
        arrowUp.addEventListener("click", () => sidebar.scrollBy({ top: -100, behavior: "smooth" }));
    }
    if (arrowDown) {
        arrowDown.addEventListener("click", () => sidebar.scrollBy({ top: 100, behavior: "smooth" }));
    }
    sidebar.addEventListener("scroll", updateArrowVisibility);
    window.addEventListener("resize", updateArrowVisibility);
    setTimeout(updateArrowVisibility, 100);

    // --- Layout app (no glass): drawer móvil + colapsar escritorio ---
    const STORAGE_PALDACA_SIDEBAR = "paldaca-sidebar-desktop-collapsed";

    function layoutIsMobile() {
        return window.innerWidth < 992;
    }

    function readDesktopCollapsedPreference() {
        try {
            return localStorage.getItem(STORAGE_PALDACA_SIDEBAR) === "1";
        } catch (_) {
            return false;
        }
    }

    function persistDesktopCollapsed(collapsed) {
        try {
            if (collapsed) localStorage.setItem(STORAGE_PALDACA_SIDEBAR, "1");
            else localStorage.removeItem(STORAGE_PALDACA_SIDEBAR);
        } catch (_) {}
    }

    function applyStoredDesktopSidebar() {
        if (layoutIsMobile()) return;
        if (!readDesktopCollapsedPreference()) return;
        sidebar.classList.add("menu-toggle");
        if (main) main.classList.add("menu-toggle");
    }

    function setAppMobileDrawer(open) {
        if (open) {
            sidebar.classList.add("menu-toggle");
            if (menu) {
                menu.classList.add("menu-toggle");
                menu.setAttribute("aria-expanded", "true");
            }
            document.body.classList.add("sidebar-drawer-open");
        } else {
            sidebar.classList.remove("menu-toggle");
            if (menu) {
                menu.classList.remove("menu-toggle");
                menu.setAttribute("aria-expanded", "false");
            }
            document.body.classList.remove("sidebar-drawer-open");
        }
    }

    function toggleDesktopSidebarCollapsed() {
        sidebar.classList.toggle("menu-toggle");
        if (main) main.classList.toggle("menu-toggle");
        if (!layoutIsMobile()) {
            persistDesktopCollapsed(sidebar.classList.contains("menu-toggle"));
        }
    }

    if (menu && !isGlass) {
        menu.addEventListener("click", () => {
            if (!layoutIsMobile()) return;
            const open = !sidebar.classList.contains("menu-toggle");
            setAppMobileDrawer(open);
            setTimeout(updateArrowVisibility, 300);
        });
    }

    if (collapseBtn && !isGlass) {
        collapseBtn.addEventListener("click", (e) => {
            e.preventDefault();
            if (layoutIsMobile()) return;
            toggleDesktopSidebarCollapsed();
            setTimeout(updateArrowVisibility, 300);
        });
    }

    const sidebarNavApp = sidebar.querySelector(".sidebar-menu");
    if (sidebarNavApp && !isGlass) {
        sidebarNavApp.addEventListener("click", (e) => {
            const a = e.target.closest("a[href]");
            if (!a || !sidebar.contains(a)) return;
            if (layoutIsMobile() && sidebar.classList.contains("menu-toggle")) {
                setAppMobileDrawer(false);
                setTimeout(updateArrowVisibility, 150);
            }
        });
    }

    if (backdrop && !isGlass) {
        backdrop.addEventListener("click", () => {
            if (layoutIsMobile() && sidebar.classList.contains("menu-toggle")) {
                setAppMobileDrawer(false);
                setTimeout(updateArrowVisibility, 150);
            }
        });
    }

    if (!isGlass) {
        document.addEventListener("keydown", (e) => {
            if (e.key !== "Escape" || !layoutIsMobile()) return;
            if (!sidebar.classList.contains("menu-toggle")) return;
            setAppMobileDrawer(false);
            setTimeout(updateArrowVisibility, 150);
        });

        let lastBp = layoutIsMobile() ? "sm" : "lg";
        window.addEventListener("resize", () => {
            const now = layoutIsMobile() ? "sm" : "lg";
            if (now === lastBp) return;
            lastBp = now;
            document.body.classList.remove("sidebar-drawer-open");
            if (menu) {
                menu.classList.remove("menu-toggle");
                menu.setAttribute("aria-expanded", "false");
            }
            sidebar.classList.remove("menu-toggle");
            if (main) main.classList.remove("menu-toggle");
            if (!layoutIsMobile()) {
                applyStoredDesktopSidebar();
            }
            setTimeout(updateArrowVisibility, 150);
        });

        applyStoredDesktopSidebar();
        setTimeout(updateArrowVisibility, 50);
    }

    // --- Glass UI: sidebar inline (siempre visible en desktop) ---
    if (!isGlass) return;

    const STORAGE_KEY = "renata-sidebar-collapsed";
    const isMobile = () => window.innerWidth <= 768;

    // En móvil, el sidebar empieza oculto (off-canvas)
    // En desktop, siempre visible (inline)
    function syncMobileReveal() {
        if (!isMobile()) {
            setGlassMobileReveal(false);
        }
    }

    window.addEventListener("resize", syncMobileReveal);

    // Abrir/cerrar sidebar en móvil desde el botón hamburguesa (#menu en base_glass)
    if (menu) {
        menu.addEventListener("click", () => {
            if (isMobile()) {
                const willOpen = !sidebar.classList.contains("is-revealed");
                setGlassMobileReveal(willOpen);
            }
            setTimeout(updateArrowVisibility, 300);
        });
    }

    // Cerrar al hacer clic en el backdrop (móvil)
    if (backdrop) {
        backdrop.addEventListener("click", () => {
            setGlassMobileReveal(false);
        });
    }

    // Cerrar drawer al elegir un enlace del menú (móvil)
    const sidebarNav = sidebar.querySelector(".sidebar-menu");
    if (sidebarNav) {
        sidebarNav.addEventListener("click", (e) => {
            const a = e.target.closest("a[href]");
            if (!a || !sidebar.contains(a)) return;
            if (isMobile() && sidebar.classList.contains("is-revealed")) {
                setGlassMobileReveal(false);
            }
        });
    }

    document.addEventListener("keydown", (e) => {
        if (e.key !== "Escape" || !isMobile() || !sidebar.classList.contains("is-revealed")) return;
        setGlassMobileReveal(false);
    });

    // Colapsar / expandir (escritorio: reduce a solo iconos)
    function isCollapsed() {
        return sidebar.classList.contains("is-collapsed");
    }

    function setCollapsed(collapsed) {
        sidebar.classList.toggle("is-collapsed", collapsed);
        sidebar.setAttribute("aria-expanded", collapsed ? "false" : "true");
        try {
            if (collapsed) localStorage.setItem(STORAGE_KEY, "1");
            else localStorage.removeItem(STORAGE_KEY);
        } catch (_) {}
    }

    if (collapseBtn) {
        collapseBtn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            setCollapsed(!isCollapsed());
        });
    }

    try {
        if (localStorage.getItem(STORAGE_KEY) === "1") {
            sidebar.classList.add("is-collapsed");
            sidebar.setAttribute("aria-expanded", "false");
        }
    } catch (_) {}
}

// ─── Chat legacy (modal Bootstrap, /ia/chat/api/) ─────────────────────────
function initLegacyChat() {
    const openChat = document.getElementById("openChat");
    const sendBtn = document.getElementById("sendChat");
    const chatInput = document.getElementById("chatInput");
    const chatBody = document.getElementById("chatBody");
    const chatModal = document.getElementById("chatModal");

    if (!chatBody) return;

    function appendMessage(role, text) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `mb-3 ${role === "user" ? "text-end" : "text-start"}`;
        const badgeClass = role === "user" ? "bg-primary" : "bg-light text-dark";
        let maxWidth = "80%";
        if (text.length > 200) maxWidth = "90%";
        else if (text.length < 50) maxWidth = "60%";
        const textStyle = text.length > 100 ? "word-wrap: break-word; white-space: pre-wrap; text-align: left;" : "";
        messageDiv.innerHTML = `<span class="badge ${badgeClass} p-2" style="font-size: 0.9rem; max-width: ${maxWidth}; display: inline-block; ${textStyle}">${text}</span>`;
        chatBody.appendChild(messageDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function loadHistory() {
        try {
            const hist = localStorage.getItem("renataChatHistory");
            if (!hist) return [];
            const msgs = JSON.parse(hist);
            chatBody.innerHTML = "";
            msgs.forEach((m) => appendMessage(m.role, m.text));
            return msgs;
        } catch {
            return [];
        }
    }

    function saveMessage(role, text) {
        let msgs = [];
        try {
            const hist = localStorage.getItem("renataChatHistory");
            if (hist) msgs = JSON.parse(hist) || [];
        } catch {}
        msgs.push({ role, text });
        localStorage.setItem("renataChatHistory", JSON.stringify(msgs));
        return msgs;
    }

    if (loadHistory().length === 0) {
        appendMessage("assistant", "¡Hola! Soy Renata, tu asistente IA. ¿En qué puedo ayudarte hoy?");
    }

    if (openChat && chatModal) {
        openChat.addEventListener("click", () => {
            const modal = new bootstrap.Modal(chatModal);
            modal.show();
            loadHistory();
        });
        chatModal.addEventListener("shown.bs.modal", loadHistory);
    }

    function sendMessage() {
        const msg = chatInput?.value?.trim();
        if (!msg) return;

        appendMessage("user", msg);
        const history = saveMessage("user", msg);
        chatInput.value = "";

        const typingDiv = document.createElement("div");
        typingDiv.className = "mb-3 text-start";
        typingDiv.innerHTML = '<span class="badge bg-light text-dark p-2">Renata está escribiendo...</span>';
        chatBody.appendChild(typingDiv);
        chatBody.scrollTop = chatBody.scrollHeight;

        fetch("/ia/chat/api/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ message: msg, history }),
        })
            .then((res) => res.json())
            .then((data) => {
                chatBody.removeChild(typingDiv);
                appendMessage("assistant", data.response || "");
                saveMessage("assistant", data.response || "");
                if (data.fillForm) {
                    localStorage.setItem("renataFormData", JSON.stringify(data.fillForm));
                    fillFormWithData(data.fillForm);
                }
                if (data.errors) showFormErrors(data.errors);
            })
            .catch((err) => {
                if (typingDiv.parentNode) chatBody.removeChild(typingDiv);
                console.error("Chat error:", err);
                appendMessage("assistant", "Lo siento, hubo un problema técnico. ¿Puedes intentar de nuevo?");
                saveMessage("assistant", "Lo siento, hubo un problema técnico. ¿Puedes intentar de nuevo?");
            });
    }

    function fillFormWithData(formData) {
        for (const [name, value] of Object.entries(formData)) {
            const field = document.querySelector(`[name="${name}"]`);
            if (field) {
                field.value = value;
                field.dispatchEvent(new Event("input", { bubbles: true }));
                field.dispatchEvent(new Event("change", { bubbles: true }));
            }
        }
        appendMessage("assistant", "¡Formulario completado! Revisa los datos y haz clic en guardar cuando estés listo.");
        saveMessage("assistant", "¡Formulario completado! Revisa los datos y haz clic en guardar cuando estés listo.");
    }

    function showFormErrors(errors) {
        let text = "Hay algunos errores en el formulario:\n";
        for (const [field, fieldErrors] of Object.entries(errors)) {
            text += `• ${field}: ${fieldErrors.join(", ")}\n`;
        }
        appendMessage("assistant", text);
        saveMessage("assistant", text);
    }

    if (sendBtn) sendBtn.addEventListener("click", sendMessage);
    if (chatInput) {
        chatInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    try {
        const savedData = localStorage.getItem("renataFormData");
        if (savedData) fillFormWithData(JSON.parse(savedData));
    } catch (_) {}

    window.addEventListener("beforeunload", () => {
        try {
            if (performance.getEntriesByType("navigation")[0]?.type === "reload") return;
            localStorage.removeItem("renataChatHistory");
            localStorage.removeItem("renataFormData");
        } catch (_) {}
    });
}

// ─── Buscador global (autocomplete, sin modal) ───────────────────────────
function initGlobalSearch() {
    const input = document.getElementById("globalSearchInput");
    const resultsBox = document.getElementById("globalSearchResults");
    const wrap = document.getElementById("globalSearchWrap");
    if (!input || !resultsBox || !wrap) return;

    let items = [];
    let groups = [];
    let activeIndex = -1;
    let lastQuery = "";
    let debounceTimer = null;
    let abortCtrl = null;

    function closeResults() {
        resultsBox.style.display = "none";
        resultsBox.innerHTML = "";
        items = [];
        groups = [];
        activeIndex = -1;
    }

    function setActive(idx) {
        activeIndex = idx;
        resultsBox.querySelectorAll(".global-search-item").forEach((el, i) => {
            el.classList.toggle("active", i === activeIndex);
        });
    }

    function renderResults(results, grouped) {
        items = results || [];
        groups = grouped || [];
        activeIndex = -1;
        if (!items.length) {
            resultsBox.innerHTML = `<div class="global-search-empty">Sin resultados para tu búsqueda.</div>`;
            resultsBox.style.display = "block";
            return;
        }

        let globalIndex = 0;
        const html = groups.length
            ? groups
                  .map((g) => {
                      const title = (g.group || "").replace(/</g, "&lt;");
                      const rows = (g.items || [])
                          .map((r) => {
                              const idx = globalIndex++;
                              const type = (r.type || "").replace(/</g, "&lt;");
                              const label = (r.label || "").replace(/</g, "&lt;");
                              const sub = (r.sublabel || "").replace(/</g, "&lt;");
                              return `
                                <div class="global-search-item" data-idx="${idx}">
                                  <div class="global-search-top">
                                    <span class="global-search-type">${type}</span>
                                  </div>
                                  <div class="global-search-label">${label}</div>
                                  ${sub ? `<div class="global-search-sublabel">${sub}</div>` : ``}
                                </div>
                              `;
                          })
                          .join("");
                      return `
                        <div class="global-search-group">
                          <div class="global-search-group-title">${title}</div>
                          ${rows}
                        </div>
                      `;
                  })
                  .join("")
            : items
                  .map((r, i) => {
                      const type = (r.type || "").replace(/</g, "&lt;");
                      const label = (r.label || "").replace(/</g, "&lt;");
                      const sub = (r.sublabel || "").replace(/</g, "&lt;");
                      return `
                        <div class="global-search-item" data-idx="${i}">
                          <div class="global-search-top">
                            <span class="global-search-type">${type}</span>
                          </div>
                          <div class="global-search-label">${label}</div>
                          ${sub ? `<div class="global-search-sublabel">${sub}</div>` : ``}
                        </div>
                      `;
                  })
                  .join("");

        resultsBox.innerHTML = html;

        resultsBox.style.display = "block";
    }

    function fetchResults(q) {
        if (abortCtrl) abortCtrl.abort();
        abortCtrl = new AbortController();

        return fetch(`/buscar/?q=${encodeURIComponent(q)}`, {
            headers: { "X-Requested-With": "XMLHttpRequest" },
            signal: abortCtrl.signal,
        })
            .then((res) => res.json())
            .then((data) => ({ results: data.results || [], groups: data.groups || [] }));
    }

    function onInput() {
        const q = (input.value || "").trim();
        lastQuery = q;
        if (q.length < 2) {
            closeResults();
            return;
        }
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            resultsBox.innerHTML = `<div class="global-search-loading">Buscando...</div>`;
            resultsBox.style.display = "block";
            fetchResults(q)
                .then((res) => {
                    if (lastQuery !== q) return; // desfasado
                    renderResults(res.results, res.groups);
                })
                .catch(() => {});
        }, 220);
    }

    input.addEventListener("input", onInput);

    resultsBox.addEventListener("click", (e) => {
        const row = e.target.closest(".global-search-item");
        if (!row) return;
        const idx = Number(row.getAttribute("data-idx"));
        const item = items[idx];
        if (item && item.url) window.location.href = item.url;
    });

    input.addEventListener("keydown", (e) => {
        if (resultsBox.style.display !== "block") return;
        const max = items.length - 1;
        if (e.key === "ArrowDown") {
            e.preventDefault();
            setActive(activeIndex < max ? activeIndex + 1 : 0);
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            setActive(activeIndex > 0 ? activeIndex - 1 : max);
        } else if (e.key === "Enter") {
            const idx = activeIndex >= 0 ? activeIndex : 0;
            if (items[idx] && items[idx].url) window.location.href = items[idx].url;
        } else if (e.key === "Escape") {
            closeResults();
        }
    });

    // Click fuera cierra
    document.addEventListener("click", (e) => {
        if (!wrap.contains(e.target)) closeResults();
    });

    // Focus vuelve a abrir si hay query y resultados
    input.addEventListener("focus", () => {
        const q = (input.value || "").trim();
        if (q.length >= 2 && resultsBox.innerHTML.trim()) {
            resultsBox.style.display = "block";
        }
    });
}

function getCookie(name) {
    let value = null;
    if (document.cookie && document.cookie !== "") {
        for (const part of document.cookie.split(";")) {
            const trimmed = part.trim();
            if (trimmed.startsWith(name + "=")) {
                value = decodeURIComponent(trimmed.slice(name.length + 1));
                break;
            }
        }
    }
    return value;
}
