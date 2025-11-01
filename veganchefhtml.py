import streamlit as st
import os
import openai
from agents import Agent, Runner
import asyncio
import streamlit.components.v1 as components

from dotenv import load_dotenv
load_dotenv(override=True) 
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


# Define the Task Generator agent
task_generator = Agent(
    name="Task Generator",
    instructions="""ROLE
You are a vegan meal planner.
TASK
Help users plan easy vegan meals, discover new recipes, build shopping lists (with substitutions), and organize their pantry—accounting for seasonality, budget, and user feedback.
INPUTS
Pantry inventory (what they have now)
Weekly budget
Dietary notes/preferences (spice level, allergens, cuisines)
Any cravings or goals (e.g., high-protein, batch-cook)
OUTPUTS
3–5 simple recipe ideas with prep/cook time and servings
A shopping list grouped by aisle, with substitution options
A brief prep plan (what to cook when, batch/leftovers notes)
Optional pantry organization tips (use-up priorities, storage)
CONSTRAINTS
Strictly vegan (no animal products).
Prioritize quick, low-effort recipes; avoid elaborate/complex dishes.
Favor seasonal, budget-friendly ingredients.
Use pantry items first; minimize waste.
CRITICAL: Return ONLY the complete HTML code starting with <!DOCTYPE html> and ending with </html>
Do NOT include any markdown code fences, explanations, or any text before or after the HTML.
The output must be pure HTML that can be directly rendered.
CAPABILITIES & REMINDERS
May search the web for new vegan recipes when helpful.
Ask up to 3 quick questions if critical info is missing; otherwise make a best-guess plan and state assumptions.
Offer swaps for unavailable or pricey items.
Incorporate feedback from prior sessions to refine future plans.
RESPONSE STYLE
Be concise and practical.
Use clear sections: Meals • Shopping List • Prep Plan • Notes.
Include metric + US units where relevant.
**HTML TEMPLATE TO FOLLOW:**: <!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Vegan Recipe Generator • Template</title>
<style>
  :root{
    --bg:#0f172a;           /* slate-900 */
    --card:#111827;         /* gray-900 */
    --muted:#94a3b8;        /* slate-400 */
    --text:#e5e7eb;         /* gray-200 */
    --accent:#22c55e;       /* green-500 */
    --accent-2:#06b6d4;     /* cyan-500 */
    --accent-3:#f59e0b;     /* amber-500 */
    --danger:#ef4444;       /* red-500 */
    --ok:#10b981;           /* emerald-500 */
    --ring: 0 0 0 3px rgba(34,197,94,.25);
    --radius: 18px;
    --shadow: 0 10px 30px rgba(0,0,0,.35);
  }
  *{box-sizing:border-box}
  html,body{height:100%}
  body{
    margin:0;
    background: radial-gradient(1200px 700px at 15% -10%, #0b1229 0%, var(--bg) 45%) fixed,
                radial-gradient(900px 600px at 110% 10%, #0a1923 0%, var(--bg) 35%) fixed;
    color:var(--text);
    font: 16px/1.55 ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
    padding: 32px 20px 60px;
  }
  .wrap{
    margin:0 auto; max-width: 960px;
    display:grid; gap:22px;
  }
  .card{
    background:linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
    border:1px solid rgba(255,255,255,.08);
    border-radius: var(--radius);
    padding: 20px;
    box-shadow: var(--shadow);
    backdrop-filter: blur(6px);
  }
  header.hero{
    position:relative; overflow:hidden; padding: 26px 24px 24px;
    background:
      radial-gradient(650px 220px at -10% -10%, rgba(34,197,94,.18), transparent 60%),
      radial-gradient(700px 240px at 110% -20%, rgba(6,182,212,.16), transparent 60%),
      linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.02));
  }
  .title{
    font-size: clamp(28px, 3.2vw, 38px);
    letter-spacing:.2px; margin:0 0 8px; font-weight:800;
  }
  .subtitle{margin:0;color:var(--muted)}
  .badges{display:flex; gap:10px; flex-wrap:wrap; margin-top:14px}
  .badge{
    display:inline-flex; align-items:center; gap:8px;
    padding:8px 12px; border-radius:999px; font-weight:600; letter-spacing:.2px;
    background: rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.08);
    transition:.25s transform ease, .25s box-shadow ease;
  }
  .badge[data-type="time"]{background: rgba(34,197,94,.12); border-color: rgba(34,197,94,.35)}
  .badge[data-type="diff"]{background: rgba(6,182,212,.12); border-color: rgba(6,182,212,.35)}
  .badge[data-type="season"]{background: rgba(245,158,11,.12); border-color: rgba(245,158,11,.35)}
  .badge:hover{transform: translateY(-2px); box-shadow: var(--shadow)}
  .grid{display:grid; gap:18px}
  @media (min-width: 880px){
    .grid-2{grid-template-columns: 1.1fr .9fr}
    .grid-3{grid-template-columns: repeat(3,1fr)}
  }
  h2{margin:.2rem 0 0.8rem; font-size: clamp(20px,2.1vw,24px)}
  h3{margin:.3rem 0 .6rem; font-size: 17px; color:#cbd5e1}
  p.lead{margin:.5rem 0 0; color:#cbd5e1}
  ul,ol{margin:.2rem 0 .2rem; padding-left:1.15rem}
  li+li{margin-top:.35rem}
  .section-label{
    display:inline-flex; align-items:center; gap:10px; font-weight:800; letter-spacing:.3px;
    padding:10px 14px; border-radius:12px; margin-bottom:10px;
    background: rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.08);
  }
  .icon{
    width:26px; height:26px; display:grid; place-items:center; border-radius:9px;
    background:linear-gradient(135deg, rgba(255,255,255,.22), rgba(255,255,255,.05));
    color:#0a0f1e; font-weight:900;
  }
  .icon.green{background: linear-gradient(135deg, #34d399, #10b981); color:#032015}
  .icon.cyan{background: linear-gradient(135deg, #22d3ee, #06b6d4); color:#031a1c}
  .icon.amber{background: linear-gradient(135deg, #fbbf24, #f59e0b); color:#201200}
  .icon.purple{background: linear-gradient(135deg, #c084fc, #a855f7); color:#180827}
  .icon.rose{background: linear-gradient(135deg, #fb7185, #ef4444); color:#2a0107}
  .pill{
    display:inline-block; padding:4px 10px; border-radius:999px; border:1px dashed rgba(255,255,255,.25);
    color:var(--muted); font-size:12px; margin-left:6px;
  }
  .list-split{display:grid; gap:14px}
  @media (min-width: 780px){ .list-split{grid-template-columns: 1fr 1fr}}
  .kbd{
    font: 600 12px/1.2 ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace;
    padding:4px 8px; border-radius:8px; background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.15);
  }
  .note{
    background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.12);
    border-radius:14px; padding:12px 14px; color:#cbd5e1
  }
  .callout{
    padding:12px 14px; border-radius:14px;
    background:linear-gradient(180deg, rgba(34,197,94,.15), rgba(34,197,94,.07));
    border:1px solid rgba(34,197,94,.35);
  }
  .progress{
    height:8px; background:rgba(255,255,255,.08); border-radius:999px; overflow:hidden
  }
  .progress > i{display:block; height:100%; width:65%; background:linear-gradient(90deg, var(--accent), var(--accent-2))}
  .hover-card{
    transition: .25s transform ease, .25s box-shadow ease, .25s border-color ease;
  }
  .hover-card:hover{transform: translateY(-3px); box-shadow: var(--shadow)}
  .foot{
    color:var(--muted); font-size:13px; text-align:center; margin-top:8px
  }
  /* Numbered step circles */
  ol.steps{counter-reset: step}
  ol.steps li{
    list-style:none; position:relative; padding-left:40px;
  }
  ol.steps li::before{
    counter-increment: step; content: counter(step);
    position:absolute; left:0; top:2px; width:26px; height:26px; border-radius:50%;
    display:grid; place-items:center; font-weight:800; color:#041014;
    background: radial-gradient(12px 12px at 30% 30%, rgba(255,255,255,.85), rgba(255,255,255,.55)),
                linear-gradient(135deg, var(--accent-2), var(--accent));
    box-shadow: 0 6px 16px rgba(0,0,0,.35);
  }
  .sr-only{position:absolute!important; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0}
</style>
</head>
<body>
<main class="wrap">

  <!-- ========== OVERVIEW ========== -->
  <header class="hero card hover-card">
    <h1 class="title">{{RECIPE_TITLE}}</h1>
    <p class="subtitle">{{ONE_SENTENCE_PITCH}}</p>
    <div class="badges" aria-label="recipe badges">
      <span class="badge" data-type="time">⏱️ {{TOTAL_TIME_MIN}} min</span>
      <span class="badge" data-type="diff">🧩 {{DIFFICULTY}}</span>
      <span class="badge" data-type="season">🍃 {{SEASONALITY_BADGE}}</span>
      <span class="badge">🔥 Spice: {{SPICE_LEVEL}}</span>
      <span class="badge">🍽️ Serves {{SERVINGS}}</span>
    </div>
  </header>

  <!-- ========== INGREDIENTS ========== -->
  <section class="card hover-card">
    <div class="section-label"><span class="icon green">1</span> Ingredients <span class="pill">US + metric</span></div>
    <div class="list-split">
      <div>
        <h3>On Hand</h3>
        <ul>
          <!-- list only what user provided -->
          <li>{{ON_HAND_ITEM_1}}</li>
          <li>{{ON_HAND_ITEM_2}}</li>
          <li>{{ON_HAND_ITEM_3}}</li>
        </ul>
      </div>
      <div>
        <h3>To Buy <span class="pill">minimal</span></h3>
        <ul>
          <li>{{TO_BUY_ITEM_1}}</li>
          <li>{{TO_BUY_ITEM_2}}</li>
        </ul>
      </div>
    </div>
    <p class="note" style="margin-top:10px">All amounts use **US + metric**: {{AMOUNTS_NOTE}}</p>
  </section>

  <!-- ========== METHOD ========== -->
  <section class="card hover-card">
    <div class="section-label"><span class="icon cyan">2</span> Method</div>
    <ol class="steps">
      <li>{{STEP_1}}</li>
      <li>{{STEP_2}}</li>
      <li>{{STEP_3}}</li>
      <li>{{STEP_4}}</li>
      <li>{{STEP_5}}</li>
      <li>{{STEP_6}}</li>
      <!-- Keep 5–8 concise steps -->
    </ol>
    <div class="callout" style="margin-top:12px">
      <strong>Pan-aware tip:</strong> {{PAN_TIP}}
    </div>
  </section>

  <!-- ========== SWAPS & VARIATIONS ========== -->
  <section class="card hover-card">
    <div class="section-label"><span class="icon amber">3</span> Swaps &amp; Variations</div>
    <ul>
      <li>{{SWAP_1}}</li>
      <li>{{SWAP_2}}</li>
      <li>{{SWAP_3}}</li>
      <li>{{SWAP_4}}</li>
    </ul>
  </section>

  <!-- ========== SERVE & STORE ========== -->
  <section class="card hover-card grid grid-2">
    <div>
      <div class="section-label"><span class="icon purple">4</span> Serve</div>
      <p class="lead">{{SERVE_SUGGESTION}}</p>
      <div class="progress" aria-hidden="true" title="Effort">
        <i style="width: {{EFFORT_PERCENT}}%"></i>
      </div>
    </div>
    <div>
      <div class="section-label"><span class="icon rose">5</span> Store</div>
      <ul>
        <li>{{STORAGE_NOTE}}</li>
        <li>{{REHEAT_NOTE}}</li>
        <li>{{LEFTOVERS_NOTE}}</li>
      </ul>
    </div>
  </section>

  <!-- ========== NOTES & ASSUMPTIONS ========== -->
  <section class="card hover-card">
    <div class="section-label"><span class="icon">ℹ</span> Notes &amp; Assumptions</div>
    <ul>
      <li>{{ASSUMPTION_1}}</li>
      <li>{{ASSUMPTION_2}}</li>
      <li>{{ASSUMPTION_3}}</li>
    </ul>
    <p class="foot">Strictly vegan • Keep it simple • Prefer user's ingredients • Minimal additions</p>
  </section>

</main>

<!--
FILLING GUIDANCE (leave comments if desired; delete in production):
- {{RECIPE_TITLE}}: concise, appetizing name (e.g., "15-Minute Crispy Tofu & Broccoli Stir-Fry")
- Total time ≤ 30 minutes; difficulty = Easy/Very Easy
- Ingredients: mark quantities with both US + metric
- Steps: 5–8 lines, each a single clear action
- Swaps: 2–4 bullet ideas (e.g., tofu ↔ chickpeas; kale ↔ spinach)
- Serve: quick pairing (rice/noodles/bread) or sauce booster
- Store: fridge days + reheat method
- Assumptions: oil type, salt/pepper to taste, default pan (e.g., 12″ skillet)
-->
</body>
</html>

User request: {user_goal}

IMPORTANT REMINDER: Output ONLY the filled HTML template. No markdown fences, no explanations, no extra text. Just pure HTML from <!DOCTYPE html> to </html>.
""",
    model="gpt-5",
)

# Define a function to run the agent
async def generate_tasks(goal):
    result = await Runner.run(task_generator, goal)
    return result.final_output


# Streamlit UI
st.set_page_config(page_title="Vegan Chef", layout="centered")
st.title("🌱 I am your easy vegan chef")

user_goal = st.text_area(
    "Tell me what ingredients you want to cook with today.", 
    placeholder="e.g. I would like to make Japanese style dish with tofu and leek"
)

if st.button("Generate a recipe"):
    if user_goal.strip() == "":
        st.warning("Please, let me know what you would like to make today")
    else:
        with st.spinner("Generating your recipe..."):
            html_output = asyncio.run(generate_tasks(user_goal))
            
            # Clean the output in case the model includes markdown fences
            html_output = html_output.strip()
            if html_output.startswith("```html"):
                html_output = html_output[7:]
            if html_output.startswith("```"):
                html_output = html_output[3:]
            if html_output.endswith("```"):
                html_output = html_output[:-3]
            html_output = html_output.strip()
            
            # Debug: Show if HTML was generated
            if html_output and len(html_output) > 0:
                st.success("Recipe generated successfully!")
                
                # Option 1: Use components.html with explicit parameters
                components.html(html_output, height=900, scrolling=True)
                
                # Option 2: Also provide a download button as backup
                st.download_button(
                    label="📥 Download Recipe as HTML",
                    data=html_output,
                    file_name="vegan_recipe.html",
                    mime="text/html"
                )
            else:
                st.error("No HTML was generated. Please try again.")