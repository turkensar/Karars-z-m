document.addEventListener("DOMContentLoaded", function () {
    var MIN_OPTIONS = 2;
    var MAX_OPTIONS = 5;
    var optionList = document.getElementById("option-list");
    var addButton = document.getElementById("add-option");

    if (!optionList || !addButton) {
        return;
    }

    function optionRows() {
        return optionList.querySelectorAll(".option-row");
    }

    function updateButtonStates() {
        var count = optionRows().length;
        addButton.disabled = count >= MAX_OPTIONS;
        optionRows().forEach(function (row) {
            row.querySelector(".remove-option").disabled = count <= MIN_OPTIONS;
        });
    }

    function bindRemove(row) {
        row.querySelector(".remove-option").addEventListener("click", function () {
            row.remove();
            updateButtonStates();
        });
    }

    function createOptionRow() {
        var row = document.createElement("div");
        row.className = "option-row";

        var input = document.createElement("input");
        input.type = "text";
        input.name = "options";
        input.maxLength = 60;
        input.placeholder = "Seçenek";
        row.appendChild(input);

        var removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.className = "remove-option";
        removeButton.textContent = "Kaldır";
        row.appendChild(removeButton);

        bindRemove(row);
        return row;
    }

    optionRows().forEach(bindRemove);

    addButton.addEventListener("click", function () {
        if (optionRows().length >= MAX_OPTIONS) {
            return;
        }
        optionList.appendChild(createOptionRow());
        updateButtonStates();
    });

    updateButtonStates();
});
