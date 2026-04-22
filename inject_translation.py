import re

# 1. Update index.html
with open('index.html', 'r', encoding='utf-8') as f:
    idx_content = f.read()

# Add translation script and widget before </body>
script_html = """
<!-- Google Translate Script -->
<script type="text/javascript">
function googleTranslateElementInit() {
  new google.translate.TranslateElement({pageLanguage: 'es', includedLanguages: 'en,es', autoDisplay: false}, 'google_translate_element');
}
function changeLanguage(lang) {
  var select = document.querySelector('.goog-te-combo');
  if(select) {
    select.value = lang;
    select.dispatchEvent(new Event('change'));
  }
}
function toggleLang() {
    var btn = document.getElementById("lang-toggle-btn");
    var isEn = btn.getAttribute("data-lang") === "en";
    if(isEn) {
        changeLanguage('es');
        btn.setAttribute("data-lang", "es");
        btn.innerHTML = "🌐 ESP";
    } else {
        changeLanguage('en');
        btn.setAttribute("data-lang", "en");
        btn.innerHTML = "🌐 ENG";
    }
}
</script>
<script type="text/javascript" src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
<style>
  .goog-te-banner-frame.skiptranslate { display: none !important; }
  body { top: 0px !important; }
  #google_translate_element { display: none; }
  .lang-btn {
      background: var(--surface);
      color: var(--text);
      border: 1px solid var(--surface-border);
      padding: 8px 16px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      font-weight: 600;
      margin-left: 10px;
  }
</style>
<div id="google_translate_element"></div>
</body>
"""
idx_content = idx_content.replace('</body>', script_html)

# Add toggle button in nav
btn_html = ' <button id="lang-toggle-btn" class="lang-btn" data-lang="es" onclick="toggleLang()">🌐 ESP</button>\n            <button class="theme-toggle" id="themeToggle" aria-label="Toggle Theme">'
idx_content = idx_content.replace('<button class="theme-toggle" id="themeToggle" aria-label="Toggle Theme">', btn_html)

# Add notranslate to charts in index.html to keep them English
idx_content = idx_content.replace('class="chart-wrapper"', 'class="chart-wrapper notranslate"')
idx_content = idx_content.replace('id="sankey_diagram"', 'id="sankey_diagram" class="notranslate"')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(idx_content)

# 2. Update dashboard_powerbi.html
with open('dashboard_powerbi.html', 'r', encoding='utf-8') as f:
    pb_content = f.read()

script_html_pb = """
<!-- Google Translate Script -->
<script type="text/javascript">
function googleTranslateElementInit() {
  new google.translate.TranslateElement({pageLanguage: 'en', includedLanguages: 'en,es', autoDisplay: false}, 'google_translate_element');
}
function changeLanguage(lang) {
  var select = document.querySelector('.goog-te-combo');
  if(select) {
    select.value = lang;
    select.dispatchEvent(new Event('change'));
  }
}
function toggleLang() {
    var btn = document.getElementById("lang-toggle-btn");
    var isEs = btn.getAttribute("data-lang") === "es";
    if(isEs) {
        changeLanguage('en');
        btn.setAttribute("data-lang", "en");
        btn.innerHTML = "🌐 ENG";
    } else {
        changeLanguage('es');
        btn.setAttribute("data-lang", "es");
        btn.innerHTML = "🌐 ESP";
    }
}
</script>
<script type="text/javascript" src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
<style>
  .goog-te-banner-frame.skiptranslate { display: none !important; }
  body { top: 0px !important; }
  #google_translate_element { display: none; }
  .lang-btn {
      background: rgba(255, 255, 255, 0.1);
      color: white;
      border: 1px solid rgba(255, 255, 255, 0.2);
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      margin-left: 10px;
      line-height: inherit;
  }
  .lang-btn:hover {
      background: rgba(255, 255, 255, 0.2);
  }
</style>
<div id="google_translate_element"></div>
</body>
"""
pb_content = pb_content.replace('</body>', script_html_pb)

btn_html_pb = '<div class="control-group" style="align-items:center; justify-content:center;"><button id="lang-toggle-btn" class="lang-btn" data-lang="en" onclick="toggleLang()">🌐 ENG</button></div>\n        </div>'
pb_content = pb_content.replace('</div>\n    </header>', btn_html_pb + '\n    </header>')
if 'btn_html_pb' not in pb_content and '<div class="control-group">' in pb_content:
    # Alternative replace
    pb_content = pb_content.replace('</header>', btn_html_pb + '\n    </header>')

# Add notranslate to chart wrappers in dashboard_powerbi.html
pb_content = pb_content.replace('class="chart-body"', 'class="chart-body notranslate"')

with open('dashboard_powerbi.html', 'w', encoding='utf-8') as f:
    f.write(pb_content)

print("Injected translation scripts into both dashboards.")
