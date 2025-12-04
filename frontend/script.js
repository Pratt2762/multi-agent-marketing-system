document.getElementById("run").addEventListener("click", () => {
    fetch("http://localhost:8000/run-agent")
        .then(res => res.json())
        .then(data => {
            document.getElementById("results").innerHTML =
                `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        });
});