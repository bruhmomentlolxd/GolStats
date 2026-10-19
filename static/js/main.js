document.addEventListener("DOMContentLoaded", function () {
  // En móvil, deja visible el filtro/ronda activo (las listas de chips se desplazan)
  document.querySelectorAll(".chip.active").forEach(function (chip) {
    chip.scrollIntoView({ inline: "center", block: "nearest" });
  });

  // Si hay partidos en vivo en pantalla, recarga cada 60 s para actualizar los resultados
  if (document.body.dataset.live === "1") {
    setTimeout(function () { location.reload(); }, 60000);
  }
});

// "VER MÁS" en las tarjetas de estadísticas
document.addEventListener("click", function (e) {
  var btn = e.target.closest("[data-more]");
  if (!btn) return;
  var card = btn.closest(".stat-card");
  card.classList.toggle("expanded");
  btn.textContent = card.classList.contains("expanded") ? "VER MENOS ⌃" : "VER MÁS ⌄";
});

// Al abrir el selector de fechas, deja visible la fecha seleccionada
document.addEventListener("toggle", function (e) {
  if (e.target.matches && e.target.matches(".round-picker") && e.target.open) {
    var a = e.target.querySelector(".round-item.active:not(.now)");
    if (a) a.scrollIntoView({ block: "center" });
  }
}, true);
