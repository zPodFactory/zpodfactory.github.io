/* Official asciinema embed + trim the cross-origin "Recorded with asciinema" footer.
   https://docs.asciinema.org/manual/server/embedding/ */
(function () {
  /* .powered footer only: 8px margin-top + ~13px text (see asciinema iframe CSS). */
  var FOOTER_HEIGHT = 28;

  function trimFooter(iframe, fullHeight) {
    var h = Math.max(0, fullHeight - FOOTER_HEIGHT);
    iframe.style.height = h + "px";
    var wrap = iframe.closest(".asciicast");
    if (wrap) {
      wrap.style.height = h + "px";
      wrap.style.overflow = "hidden";
    }
  }

  window.addEventListener("message", function (e) {
    if (!e.data || e.data.type !== "bodySize" || !e.data.payload) {
      return;
    }
    document.querySelectorAll(".asciinema-embed .asciicast iframe").forEach(function (iframe) {
      if (e.source !== iframe.contentWindow) {
        return;
      }
      var full = e.data.payload.height;
      /* Run after asciinema's embed handler sets the full document height. */
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          trimFooter(iframe, full);
        });
      });
    });
  });

  document.querySelectorAll("[data-asciinema-id]").forEach(function (container) {
    if (container.dataset.asciinemaLoaded) {
      return;
    }
    var id = container.dataset.asciinemaId;
    if (!id) {
      return;
    }
    var script = document.createElement("script");
    script.src = "https://asciinema.org/a/" + id + ".js";
    script.id = "asciicast-" + id;
    script.async = true;
    container.appendChild(script);
    container.dataset.asciinemaLoaded = "1";
  });
})();
