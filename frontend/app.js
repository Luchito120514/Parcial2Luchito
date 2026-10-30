const API_URL = "http://34.224.168.92:8000";

const form = document.getElementById("form");
const urlInput = document.getElementById("url");
const errorEl = document.getElementById("error");
const copiedEl = document.getElementById("copied");
const resultEl = document.getElementById("result");
const shortInput = document.getElementById("short");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorEl.textContent = "";
  copiedEl.textContent = "";
  resultEl.hidden = true;

  // Validar la URL antes de enviarla
  try {
    const parsed = new URL(urlInput.value);
    if (!["http:", "https:"].includes(parsed.protocol)) throw new Error();
  } catch {
    errorEl.textContent = "La URL ingresada no es válida.";
    return;
  }

  try {
    const res = await fetch(`${API_URL}/shorten`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ original_url: urlInput.value }),
    });
    if (res.status === 422) {
      errorEl.textContent = "El backend rechazó la URL por no ser válida.";
      return;
    }
    if (!res.ok) throw new Error("Error del servidor");
    const data = await res.json();
    shortInput.value = data.short_url;
    resultEl.hidden = false;
  } catch {
    errorEl.textContent = "No se pudo conectar con el backend.";
  }
});

document.getElementById("copy").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(shortInput.value);
    copiedEl.textContent = "¡Enlace copiado!";
  } catch {
    shortInput.select();
    document.execCommand("copy");
    copiedEl.textContent = "¡Enlace copiado!";
  }
});