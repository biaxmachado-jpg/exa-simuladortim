"""Embute src/simulador-vagas.html no index.html (aba "Simulador de Vagas 2027").

Uso: python3 tools/embed_simulador_vagas.py
Idempotente: na primeira execução cria a aba; nas próximas só atualiza o conteúdo embutido.
A aba "Simulador" original não é alterada.
"""
import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
SRC = ROOT / "src" / "simulador-vagas.html"

html = INDEX.read_text(encoding="utf-8")
b64 = base64.b64encode(SRC.read_bytes()).decode("ascii")

if 'id="simvagas-b64"' in html:
    html, n = re.subn(
        r'(<script id="simvagas-b64" type="text/plain">)(.*?)(</script>)',
        lambda m: m.group(1) + b64 + m.group(3),
        html,
        flags=re.S,
    )
    assert n == 1
else:
    btn_old = """<button class="tab-btn" onclick="showTab('simulador')">Simulador</button>"""
    assert html.count(btn_old) == 1
    html = html.replace(
        btn_old,
        btn_old + """\n  <button class="tab-btn" onclick="showTab('simvagas')">Simulador de Vagas 2027</button>""",
    )

    panel = (
        '<div id="tab-simvagas" class="tab-panel">\n'
        '<div class="note" style="margin-top:0; margin-bottom:12px;">\n'
        '  Simulador de ofertas por vagas (Bronze, Prata, Ouro e Diamante) para o time comercial. Base: deck "AYA News 2027".\n'
        '</div>\n'
        '<iframe id="simvagas-iframe" style="width:100%; height:1400px; border:1px solid var(--border); border-radius:8px;" title="Simulador de Vagas 2027"></iframe>\n'
        '</div>\n\n'
        '<script id="simvagas-b64" type="text/plain">' + b64 + '</script>\n'
    )
    anchor = '<script id="simulador-b64" type="text/plain">'
    assert html.count(anchor) == 1
    html = html.replace(anchor, panel + anchor)

    loader = """
var simVagasLoaded = false;
function loadSimVagas() {
  if (simVagasLoaded) return;
  try {
    var b64 = document.getElementById('simvagas-b64').textContent;
    document.getElementById('simvagas-iframe').srcdoc = b64DecodeUnicode(b64);
    simVagasLoaded = true;
  } catch (e) {
    document.getElementById('tab-simvagas').insertAdjacentHTML('beforeend', '<div class="note">Erro ao carregar o simulador de vagas.</div>');
  }
}

// Ajusta a altura do iframe conforme o conteúdo (aceita mensagens apenas do próprio iframe).
window.addEventListener('message', function (ev) {
  var frame = document.getElementById('simvagas-iframe');
  if (!frame || ev.source !== frame.contentWindow) return;
  var h = ev.data && ev.data.ayaSimVagasHeight;
  if (typeof h === 'number' && h > 200 && h < 20000) frame.style.height = Math.ceil(h + 8) + 'px';
});

function showTab(name) {"""
    assert html.count("\nfunction showTab(name) {") == 1
    html = html.replace("\nfunction showTab(name) {", loader, 1)
    sim_line = "  if (name === 'simulador') { loadSimulador(); }"
    assert html.count(sim_line) == 1
    html = html.replace(sim_line, sim_line + "\n  if (name === 'simvagas') { loadSimVagas(); }")

INDEX.write_text(html, encoding="utf-8")
print("ok", len(b64), "bytes base64")
