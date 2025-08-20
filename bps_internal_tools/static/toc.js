// static/toc.js
(function () {
  function debounce(fn, ms) {
    let t;
    return function (...args) {
      clearTimeout(t);
      t = setTimeout(() => fn.apply(this, args), ms);
    };
  }

  function wireAutocomplete({ input, results, endpoint, onSelect }) {
    if (!input || !results || !endpoint) return;

    let lastQ = "";
    const fetchResults = debounce(async () => {
      const q = (input.value || "").trim();
      if (!q || q === lastQ) {
        results.innerHTML = "";
        return;
      }
      lastQ = q;

      try {
        const url = new URL(endpoint, window.location.origin);
        url.searchParams.set("q", q);
        const res = await fetch(url, { headers: { "Accept": "application/json" } });
        if (!res.ok) throw new Error("bad response");
        const data = await res.json();
        if (!Array.isArray(data) || data.length === 0) {
          results.innerHTML = "";
          return;
        }
        results.innerHTML = data
          .map(
            (item) => `
              <button type="button" class="ac-item" data-id="${item.id}" data-name="${item.name}">
                ${item.name}
              </button>`
          )
          .join("");
      } catch (e) {
        console.error("autocomplete fetch failed:", e);
        results.innerHTML = "";
      }
    }, 180);

    input.addEventListener("input", fetchResults);
    input.addEventListener("focus", fetchResults);
    document.addEventListener("click", (e) => {
      if (!results.contains(e.target) && e.target !== input) {
        results.innerHTML = "";
      }
    });

    results.addEventListener("click", (e) => {
      const btn = e.target.closest(".ac-item");
      if (!btn) return;
      const id = btn.getAttribute("data-id");
      const name = btn.getAttribute("data-name");
      onSelect({ id, name });
      results.innerHTML = "";
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    const cfg = document.getElementById("toc-config");
    if (!cfg) {
      console.warn("toc-config element not found; endpoints missing");
      return;
    }

    const ENDPOINTS = {
      searchTeachers: cfg.dataset.searchTeachers,
      searchCourses:  cfg.dataset.searchCourses,
      goCourse:       cfg.dataset.goCourse
    };

    // Teacher autocomplete
    wireAutocomplete({
      input: document.getElementById("teacher-search"),
      results: document.getElementById("teacher-results"),
      endpoint: ENDPOINTS.searchTeachers,
      onSelect: ({ id, name }) => {
        // If you have a teacher->course selection page, change this accordingly:
        // e.g., window.location.href = cfg.dataset.selectCoursesForTeacher + "?teacher_id=" + encodeURIComponent(id) + ...
        // For now, just store selection in the field:
        document.getElementById("teacher-search").value = name;
        // TODO: navigate if desired
      },
    });

    // Course autocomplete
    wireAutocomplete({
      input: document.getElementById("course-search"),
      results: document.getElementById("course-results"),
      endpoint: ENDPOINTS.searchCourses,
      onSelect: ({ id, name }) => {
        const url = new URL(ENDPOINTS.goCourse, window.location.origin);
        url.searchParams.set("course_id", id);
        url.searchParams.set("course_name", name);
        window.location.href = url.toString();
      },
    });
  });
})();
