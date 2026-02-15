/*
    Fichier écrit et structuré manuellement :
    - Python (Flask+SymPy) calcule tout
    - JS ne fait que transmettre les entrées et afficher les sorties
*/

async function run() {

    const type_input  = document.getElementById("type_input").value;
    const user_input1 = document.getElementById("user_input1").value;
    const user_input2 = document.getElementById("user_input2").value;

    const outDiv = document.getElementById("out");
    outDiv.innerHTML = "<p>Calcul en cours…</p>";

    try {
        const response = await fetch("/compute", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                type_input: type_input,
                user_input1: user_input1,
                user_input2: user_input2
            })
        });

        const data = await response.json();
        outDiv.innerHTML = "";

        data.messages.forEach(msg => {

            if (msg.type === "latex") {
                const div = document.createElement("div");
                div.className = "msg latex";
                try {
                    katex.render(msg.content, div, { throwOnError: false, displayMode: true });
                } catch (e) {
                    div.textContent = msg.content;
                }
                outDiv.appendChild(div);
            }

            else if (msg.type === "info") {
                const div = document.createElement("div");
                div.className = "msg info";
                div.textContent = "ℹ️ " + msg.content;
                outDiv.appendChild(div);
            }

            else if (msg.type === "error") {
                const div = document.createElement("div");
                div.className = "msg error";
                div.textContent = "❌ " + msg.content;
                outDiv.appendChild(div);
            }

            else if (msg.type === "plot") {
                const img = document.createElement("img");
                img.src = "data:image/png;base64," + msg.content;
                img.className = "plot";
                outDiv.appendChild(img);
            }

        });

    } catch (err) {
        outDiv.innerHTML = "";
        const div = document.createElement("div");
        div.className = "msg error";
        div.textContent = "Erreur de communication avec le serveur : " + err;
        outDiv.appendChild(div);
    }
}

/* Entrée clavier = lancer (comportement type Streamlit) */
document.addEventListener("DOMContentLoaded", function () {
    ["user_input1", "user_input2"].forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        el.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                run();
            }
        });
    });
});