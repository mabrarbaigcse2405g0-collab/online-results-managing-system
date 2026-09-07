(function () {
    "use strict";

    function ready(fn) {
        if (document.readyState !== "loading") {
            fn();
        } else {
            document.addEventListener("DOMContentLoaded", fn);
        }
    }

    ready(function () {
        const totalField = document.getElementById("id_total_questions");
        const answerKeyField = document.getElementById("id_answer_key");
        if (!totalField || !answerKeyField) return;

        const form = totalField.closest("form");
        if (!form) return;

        const row = totalField.closest(".form-row");
        const container = document.createElement("div");
        container.id = "omr-answer-options";
        container.style.margin = "20px 0";
        if (row) row.after(container);

        function readSaved() {
            try {
                const value = answerKeyField.value || "{}";
                const parsed = JSON.parse(value);
                return parsed && typeof parsed === "object" ? parsed : {};
            } catch (e) {
                return {};
            }
        }

        function generate() {
            const count = parseInt(totalField.value, 10) || 0;
            const saved = readSaved();
            container.innerHTML = "";

            if (count < 1) return;

            const heading = document.createElement("h2");
            heading.textContent = "Correct option for each OMR question";
            heading.style.marginBottom = "15px";
            container.appendChild(heading);

            for (let q = 1; q <= count; q++) {
                const box = document.createElement("div");
                box.style.cssText = "border:1px solid #ddd;padding:12px 15px;margin:8px 0;background:#fff;border-radius:4px;";

                const title = document.createElement("strong");
                title.textContent = "Question " + q + ": ";
                box.appendChild(title);

                for (let option = 1; option <= 4; option++) {
                    const label = document.createElement("label");
                    label.style.cssText = "display:inline-flex;align-items:center;margin:0 22px 0 0;cursor:pointer;font-weight:normal;";

                    const radio = document.createElement("input");
                    radio.type = "radio";
                    radio.name = "omr_answer_" + q;
                    radio.value = String(option);
                    radio.required = true;
                    radio.style.marginRight = "5px";

                    if (String(saved[String(q)]) === String(option)) {
                        radio.checked = true;
                    }

                    label.appendChild(radio);
                    label.appendChild(document.createTextNode(String(option)));
                    box.appendChild(label);
                }

                container.appendChild(box);
            }
        }

        form.addEventListener("submit", function (event) {
            const count = parseInt(totalField.value, 10) || 0;
            const key = {};

            for (let q = 1; q <= count; q++) {
                const selected = form.querySelector('input[name="omr_answer_' + q + '"]:checked');
                if (!selected) {
                    event.preventDefault();
                    alert("Please select the correct option for Question " + q + ".");
                    selected?.focus();
                    return;
                }
                key[String(q)] = selected.value;
            }

            answerKeyField.value = JSON.stringify(key);
        });

        totalField.addEventListener("input", generate);
        totalField.addEventListener("change", generate);
        generate();
    });
})();
