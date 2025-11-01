import streamlit as st
import os
import openai
from agents import Agent, Runner
import asyncio #running functions at the same time to reduce run time 


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
Return only the html code (do not start or end with "```html") but with <!DOCTYPE html>
CAPABILITIES & REMINDERS
May search the web for new vegan recipes when helpful.
Ask up to 3 quick questions if critical info is missing; otherwise make a best-guess plan and state assumptions.
Offer swaps for unavailable or pricey items.
Incorporate feedback from prior sessions to refine future plans.
RESPONSE STYLE
Be concise and practical.
Use clear sections: Meals • Shopping List • Prep Plan • Notes.
Include metric + US units where relevant.
 """,
    model="gpt-5",
)

# Define a function to run the agent
async def generate_tasks(goal):
    result = await Runner.run(task_generator, goal)
    return result.final_output


# Streamlit UI
st.set_page_config(page_title="Vegan Chef", page_icon="🥦")
st.title("🥦 Vegan Chef — simple, tasty, vegan")
#st.write("Tell me what ingredients you want to cook with today.")

user_goal = st.text_area("Tell me what ingredients you want to cook with today.", placeholder="e.g. I would like to make Japanese style dish with tofu and leek")

if st.button("Generate a recipe"):
    if user_goal.strip() == "":
        st.warning("Please, let me know what you would like to make today")
    else:
        with st.spinner("Generating your recipe..."):
            tasks = asyncio.run(generate_tasks(user_goal))
            st.success("Here is your recipe:")
            st.markdown(f"```text\n{tasks}\n```")