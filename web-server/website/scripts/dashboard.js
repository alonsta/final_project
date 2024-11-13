function switchTab(tabName) {
    const sections = document.querySelectorAll(".content-section");
    sections.forEach(section => section.classList.add("hidden"));

    const activeSection = document.getElementById(tabName);
    if (activeSection) {
        activeSection.classList.remove("hidden");
    }
}