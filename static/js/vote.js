document.addEventListener("DOMContentLoaded", function () {
    var forms = document.querySelectorAll(".vote-form");

    forms.forEach(function (form) {
        form.addEventListener("submit", function (event) {
            var submitter = event.submitter;
            if (!submitter || submitter.name !== "option_id") {
                return;
            }
            event.preventDefault();

            var optionId = submitter.value;
            var csrfInput = form.querySelector("[name=csrfmiddlewaretoken]");
            var csrfToken = csrfInput ? csrfInput.value : "";

            fetch(form.action, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({ option_id: optionId }),
            })
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    if (data.ok) {
                        renderResults(form, data);
                    } else {
                        form.submit();
                    }
                })
                .catch(function () {
                    form.submit();
                });
        });
    });

    function renderResults(form, data) {
        var card = form.closest(".poll-card");
        if (!card) {
            return;
        }

        var buttonTexts = {};
        form.querySelectorAll(".poll-option-button").forEach(function (button) {
            buttonTexts[button.value] = button.textContent;
        });

        var resultsContainer = document.createElement("div");
        resultsContainer.className = "poll-results";

        data.results.forEach(function (result) {
            var isVoted = data.voted_option_id === result.option_id;

            var row = document.createElement("div");
            row.className = "poll-result-row" + (isVoted ? " poll-result-row-voted" : "");

            var label = document.createElement("div");
            label.className = "poll-result-label";

            var textSpan = document.createElement("span");
            textSpan.className = "poll-option-text";
            textSpan.textContent = buttonTexts[result.option_id] || "";

            if (isVoted) {
                textSpan.appendChild(document.createTextNode(" "));
                var badge = document.createElement("span");
                badge.className = "poll-voted-badge";
                badge.textContent = "✓ senin oyun";
                textSpan.appendChild(badge);
            }

            var percentSpan = document.createElement("span");
            percentSpan.className = "poll-option-percent";
            percentSpan.textContent = result.percent + "%";

            label.appendChild(textSpan);
            label.appendChild(percentSpan);

            var track = document.createElement("div");
            track.className = "poll-bar-track";

            var fill = document.createElement("div");
            fill.className = "poll-bar-fill";
            fill.style.width = "0%";
            track.appendChild(fill);

            row.appendChild(label);
            row.appendChild(track);
            resultsContainer.appendChild(row);
        });

        form.replaceWith(resultsContainer);

        var fills = resultsContainer.querySelectorAll(".poll-bar-fill");
        data.results.forEach(function (result, index) {
            var fill = fills[index];
            window.setTimeout(function () {
                fill.style.width = result.percent + "%";
            }, index * 40);
        });

        var totalEl = card.querySelector(".poll-total");
        if (totalEl) {
            totalEl.textContent = data.total + " oy";
        }
    }
});
