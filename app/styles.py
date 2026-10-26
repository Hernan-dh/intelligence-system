CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Manrope:wght@400;500;600;700&display=swap');
:root { --bg:#111412; --surface:#181c19; --raised:#202522; --line:#343a35; --text:#e9e9e3; --muted:#909690; --acid:#c7ff37; --orange:#ff6947; --mono:'DM Mono',monospace; --sans:'Manrope',sans-serif; }
footer,.built-with,.show-api,.api-docs { display:none!important; }
html,body,gradio-app { background:var(--bg)!important; color:var(--text)!important; }
body { background-image:linear-gradient(rgb(255 255 255 / 2.5%) 1px,transparent 1px),linear-gradient(90deg,rgb(255 255 255 / 2.5%) 1px,transparent 1px)!important; background-size:42px 42px!important; }
.gradio-container { max-width:1180px!important; padding:34px 24px 56px!important; background:transparent!important; color:var(--text)!important; font-family:var(--sans)!important; }
.gradio-container * { border-radius:0!important; }
.block,.form { background:transparent!important; box-shadow:none!important; }
#is-header { display:grid!important; grid-template-columns:auto 1fr auto; gap:18px; align-items:center; margin-bottom:28px; padding-bottom:22px; border-bottom:3px solid var(--text); }
.is-mark { width:42px; height:42px; display:grid; grid-template-columns:repeat(2,1fr); gap:4px; }.is-mark span{background:var(--acid)}.is-mark span:last-child{background:var(--orange)}
.is-eyebrow { margin:0; color:var(--muted); font:400 10px var(--mono); letter-spacing:.13em; text-transform:uppercase; }.is-title { margin:5px 0 0; font:700 clamp(2rem,5vw,3.4rem)/.9 var(--sans); letter-spacing:-.065em; }.is-title span{color:var(--acid);font-weight:400}.is-status { color:var(--acid); font:400 10px var(--mono); letter-spacing:.08em; text-transform:uppercase; }
#is-chat,#is-inspect { min-height:420px; padding:20px!important; border:1px solid var(--line)!important; background:var(--surface)!important; }#is-chat{box-shadow:14px 14px 0 rgb(0 0 0 / 26%)}
#is-inspect h3 { margin:0 0 14px!important; padding-bottom:10px; border-bottom:2px solid var(--acid); color:var(--text)!important; font:500 10px var(--mono)!important; letter-spacing:.13em; text-transform:uppercase; }
textarea,input { border:1px solid var(--line)!important; background:var(--surface)!important; color:var(--text)!important; font:400 15px/1.5 var(--sans)!important; }textarea:focus,input:focus{box-shadow:inset 3px 0 0 var(--acid)!important;}
button { border:1px solid var(--line)!important; background:var(--raised)!important; color:var(--text)!important; font:500 10px var(--mono)!important; letter-spacing:.07em; text-transform:uppercase; }button.primary { background:var(--acid)!important; color:#111412!important; border-color:var(--acid)!important; }
.message-row .message,.message-row .bubble { background:var(--raised)!important; color:var(--text)!important; }.message-row.user-row .message,.message-row[data-role='user'] .message { background:var(--acid)!important; color:#111412!important; }.message-row.bot-row .message,.message-row[data-role='assistant'] .message { border-left:2px solid var(--orange)!important; }
table,th,td { border-color:var(--line)!important; color:var(--text)!important; background:var(--surface)!important; font-family:var(--mono)!important; font-size:11px!important; }
#is-ingest { margin-top:24px; padding:20px!important; border:1px solid var(--line)!important; background:var(--surface)!important; }#is-ingest h3 { margin:0 0 12px!important; color:var(--text)!important; font:500 11px var(--mono)!important; letter-spacing:.13em; text-transform:uppercase; }
@media(max-width:700px){.gradio-container{padding:24px 14px 38px!important}#is-header{grid-template-columns:auto 1fr}.is-status{display:none}}
"""
