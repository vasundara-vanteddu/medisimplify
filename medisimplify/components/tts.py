"""Read-aloud button using the browser's Web Speech API (free)."""
import json

import streamlit.components.v1 as components


def read_aloud(text: str, lang_code: str = "en-IN", label: str = "🔊 Read aloud"):
    safe_text = json.dumps(text).replace("</", "<\\/")
    html = f"""
    <div style="font-family:sans-serif">
      <button id="play" style="padding:6px 14px;border-radius:8px;border:1px solid #888;cursor:pointer">{label}</button>
      <button id="stop" style="padding:6px 14px;border-radius:8px;border:1px solid #888;cursor:pointer">⏹ Stop</button>
      <span id="msg" style="color:#b45309;font-size:13px;margin-left:8px"></span>
    </div>
    <script>
      const text = {safe_text};
      const lang = "{lang_code}";
      const msg = document.getElementById("msg");
      function pickVoice() {{
        const voices = window.speechSynthesis.getVoices();
        return voices.find(v => v.lang.replace("_","-") === lang)
            || voices.find(v => v.lang.toLowerCase().startsWith(lang.split("-")[0]));
      }}
      document.getElementById("play").onclick = () => {{
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(text);
        u.lang = lang;
        const v = pickVoice();
        if (v) {{ u.voice = v; msg.textContent = ""; }}
        else if (!lang.startsWith("en")) {{ msg.textContent = "No voice for this language on your device (try Chrome)."; }}
        window.speechSynthesis.speak(u);
      }};
      document.getElementById("stop").onclick = () => window.speechSynthesis.cancel();
    </script>
    """
    components.html(html, height=50)
