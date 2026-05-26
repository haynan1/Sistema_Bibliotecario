const currentPath = window.location.pathname.replace(/\/$/, "") || "/";

document.querySelectorAll(".sidebar-link").forEach((link) => {
    const linkPath = new URL(link.href).pathname.replace(/\/$/, "") || "/";
    const isHome = linkPath === "/" && currentPath === "/";
    const isSection = linkPath !== "/" && currentPath.startsWith(linkPath);

    if (isHome || isSection) {
        link.classList.add("active");
    }
});

const toggleButton = document.querySelector(".sidebar-toggle");
const closeTargets = document.querySelectorAll("[data-sidebar-close], .sidebar-link");

if (toggleButton) {
    toggleButton.addEventListener("click", () => {
        document.body.classList.toggle("sidebar-open");
    });
}

closeTargets.forEach((target) => {
    target.addEventListener("click", () => {
        document.body.classList.remove("sidebar-open");
    });
});

document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
        const message = form.getAttribute("data-confirm");
        if (message && !window.confirm(message)) {
            event.preventDefault();
        }
    });
});
