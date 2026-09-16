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

        var resultsHtml = "";
        data.results.forEach(function (result) {
            var isVoted = data.voted_option_id === result.option_id;
            var votedClass = isVoted ? " poll-result-row-voted" : "";
            var votedMark = isVoted ? " ✓ senin oyun" : "";
            var text = buttonTexts[result.option_id] || "";
            resultsHtml +=
                '<div class="poll-result-row' + votedClass + '">' +
                '<div class="poll-bar" style="width:' + result.percent + '%;"></div>' +
                '<span class="poll-option-text">' + text + votedMark + "</span>" +
                '<span class="poll-option-percent">' + result.percent + "%</span>" +
                "</div>";
        });

        var resultsContainer = document.createElement("div");
        resultsContainer.className = "poll-results";
        resultsContainer.innerHTML = resultsHtml;
        form.replaceWith(resultsContainer);

        var totalEl = card.querySelector(".poll-total");
        if (totalEl) {
            totalEl.textContent = data.total + " oy";
        }
    }
});
