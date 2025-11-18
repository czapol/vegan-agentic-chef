import streamlit as st
import os
import openai
from agents import Agent, Runner
import asyncio
import streamlit.components.v1 as components
import base64
from io import BytesIO

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
    --bg:#ffffff;           /* white */
    --card:#f8fafc;         /* slate-50 */
    --muted:#64748b;        /* slate-500 */
    --text:#0f172a;         /* slate-900 */
    --accent:#22c55e;       /* green-500 */
    --accent-2:#06b6d4;     /* cyan-500 */
    --accent-3:#f59e0b;     /* amber-500 */
    --danger:#ef4444;       /* red-500 */
    --ok:#10b981;           /* emerald-500 */
    --ring: 0 0 0 3px rgba(34,197,94,.25);
    --radius: 18px;
    --shadow: 0 4px 20px rgba(0,0,0,.08);
  }
  *{box-sizing:border-box}
  html,body{height:100%}
  body{
    margin:0;
    background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 50%, #ecfeff 100%);
    color:var(--text);
    font: 16px/1.55 ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
    padding: 32px 20px 60px;
  }
  .wrap{
    margin:0 auto; max-width: 960px;
    display:grid; gap:22px;
  }
  .card{
    background:#ffffff;
    border:1px solid #e2e8f0;
    border-radius: var(--radius);
    padding: 20px;
    box-shadow: var(--shadow);
  }
  header.hero{
    position:relative; overflow:hidden; padding: 26px 24px 24px;
    background:
      radial-gradient(650px 220px at -10% -10%, rgba(34,197,94,.08), transparent 60%),
      radial-gradient(700px 240px at 110% -20%, rgba(6,182,212,.06), transparent 60%),
      #ffffff;
  }
  .title{
    font-size: clamp(28px, 3.2vw, 38px);
    letter-spacing:.2px; margin:0 0 8px; font-weight:800;
    color: var(--text);
  }
  .subtitle{margin:0;color:var(--muted)}
  .badges{display:flex; gap:10px; flex-wrap:wrap; margin-top:14px}
  .badge{
    display:inline-flex; align-items:center; gap:8px;
    padding:8px 12px; border-radius:999px; font-weight:600; letter-spacing:.2px;
    background: #f1f5f9; border:1px solid #e2e8f0;
    color: var(--text);
    transition:.25s transform ease, .25s box-shadow ease;
  }
  .badge[data-type="time"]{background: #f0fdf4; border-color: #bbf7d0; color: #166534}
  .badge[data-type="diff"]{background: #ecfeff; border-color: #a5f3fc; color: #155e75}
  .badge[data-type="season"]{background: #fef3c7; border-color: #fde68a; color: #92400e}
  .badge:hover{transform: translateY(-2px); box-shadow: var(--shadow)}
  .grid{display:grid; gap:18px}
  @media (min-width: 880px){
    .grid-2{grid-template-columns: 1.1fr .9fr}
    .grid-3{grid-template-columns: repeat(3,1fr)}
  }
  h2{margin:.2rem 0 0.8rem; font-size: clamp(20px,2.1vw,24px); color: var(--text)}
  h3{margin:.3rem 0 .6rem; font-size: 17px; color:#475569}
  p.lead{margin:.5rem 0 0; color:#475569}
  ul,ol{margin:.2rem 0 .2rem; padding-left:1.15rem}
  li+li{margin-top:.35rem}
  .section-label{
    display:inline-flex; align-items:center; gap:10px; font-weight:800; letter-spacing:.3px;
    padding:10px 14px; border-radius:12px; margin-bottom:10px;
    background: #f8fafc; border:1px solid #e2e8f0;
    color: var(--text);
  }
  .icon{
    width:26px; height:26px; display:grid; place-items:center; border-radius:9px;
    color:#ffffff; font-weight:900;
  }
  .icon.green{background: linear-gradient(135deg, #34d399, #10b981)}
  .icon.cyan{background: linear-gradient(135deg, #22d3ee, #06b6d4)}
  .icon.amber{background: linear-gradient(135deg, #fbbf24, #f59e0b)}
  .icon.purple{background: linear-gradient(135deg, #c084fc, #a855f7)}
  .icon.rose{background: linear-gradient(135deg, #fb7185, #ef4444)}
  .pill{
    display:inline-block; padding:4px 10px; border-radius:999px; border:1px dashed #cbd5e1;
    color:var(--muted); font-size:12px; margin-left:6px;
  }
  .list-split{display:grid; gap:14px}
  @media (min-width: 780px){ .list-split{grid-template-columns: 1fr 1fr}}
  .kbd{
    font: 600 12px/1.2 ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace;
    padding:4px 8px; border-radius:8px; background:#f1f5f9; border:1px solid #cbd5e1;
  }
  .note{
    background:#f8fafc; border:1px solid #e2e8f0;
    border-radius:14px; padding:12px 14px; color:#475569
  }
  .callout{
    padding:12px 14px; border-radius:14px;
    background:#f0fdf4;
    border:1px solid #bbf7d0;
    color: #166534;
  }
  .progress{
    height:8px; background:#f1f5f9; border-radius:999px; overflow:hidden
  }
  .progress > i{display:block; height:100%; width:65%; background:linear-gradient(90deg, var(--accent), var(--accent-2))}
  .hover-card{
    transition: .25s transform ease, .25s box-shadow ease, .25s border-color ease;
  }
  .hover-card:hover{transform: translateY(-3px); box-shadow: 0 8px 30px rgba(0,0,0,.12); border-color: #cbd5e1}
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
    display:grid; place-items:center; font-weight:800; color:#ffffff;
    background: linear-gradient(135deg, var(--accent-2), var(--accent));
    box-shadow: 0 4px 12px rgba(6,182,212,.3);
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

# Function to extract text content from HTML
def html_to_text(html_content):
    """Convert HTML recipe to plain text format"""
    # Simple extraction - you might want to use BeautifulSoup for better parsing
    import re
    
    # Remove HTML tags
    text = re.sub('<[^<]+?>', '', html_content)
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()


# Streamlit UI
st.set_page_config(page_title="Vegan Chef", layout="centered")
st.title("🌱 I am your easy vegan chef")

user_goal = st.text_area(
    "Tell me what ingredients you want to cook with today.", 
    placeholder="e.g. I would like to make Japanese style dish with tofu and leek"
)

# Initialize session state to store the recipe
if 'html_output' not in st.session_state:
    st.session_state.html_output = None

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
            
            # Store in session state
            if html_output and len(html_output) > 0:
                st.session_state.html_output = html_output
            else:
                st.error("No HTML was generated. Please try again.")

# Display the recipe if it exists in session state
if st.session_state.html_output:
    st.success("Recipe generated successfully!")
    
    # Render the HTML
    components.html(st.session_state.html_output, height=900, scrolling=True)
    
    # Download options
    st.markdown("---")
    st.subheader("📥 Download Your Recipe")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download as HTML
        st.download_button(
            label="📄 Download as HTML",
            data=st.session_state.html_output,
            file_name="vegan_recipe.html",
            mime="text/html",
            help="Download the recipe as a styled HTML file you can open in any browser",
            key="download_html"
        )
    
    with col2:
        # Download as Text
        text_output = html_to_text(st.session_state.html_output)
        st.download_button(
            label="📝 Download as Text",
            data=text_output,
            file_name="vegan_recipe.txt",
            mime="text/plain",
            help="Download the recipe as plain text without formatting",
            key="download_text"
        )
    
    with col3:
        # Info about screenshot
        st.info("💡 **Tip:** To save as image, use your browser's screenshot tool or print to PDF!")