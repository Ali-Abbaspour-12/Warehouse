function getAllFieldsExcept(target) {
    const keys = ["company", "user", "category", "project_code", "property_code", "serial_number","personnel_code","current_location","system_identification_code", "model","serial_number","recipient_delivery","closed"];
    const params = {};
    keys.forEach(k => {
        if (k !== target) {
            let v = document.getElementById(k)?.value;
            if (v) params[k] = v;
        }
    });
    return params;
}

function loadSuggestions(field) {
    let value = document.getElementById(field).value;

    let params = new URLSearchParams();
    params.append("field", field);
    params.append("value", value);

    // اضافه کردن فیلتر سایر فیلدها
    let others = getAllFieldsExcept(field);
    for (let k in others) params.append(k, others[k]);

    fetch(`/search/suggest?${params.toString()}`)
        .then(res => res.json())
        .then(data => {
            let box = document.getElementById(field + "_box");
            box.innerHTML = "";
            box.style.display = data.suggestions.length ? "block" : "none";

            data.suggestions.forEach(s => {
                let div = document.createElement("div");
                div.className = "suggest-item";
                div.textContent = s;

                div.onclick = () => {
                    document.getElementById(field).value = s;
                    box.style.display = "none";
                };

                box.appendChild(div);
            });
        });
}

document.addEventListener("click", (e) => {
    document.querySelectorAll(".suggest-box").forEach(b => {
        if (!b.contains(e.target) && !b.previousElementSibling.contains(e.target)) {
            b.style.display = "none";
        }
    });
});