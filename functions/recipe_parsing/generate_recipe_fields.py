from functions.llms.llm import LLM
import json

def generate(recipe, model_name="llama-3.3-70b-versatile"):
    """
    Generate a recipe using the specified LLM model.
    """
    llm = LLM(model_name)
    try:
        result = llm.ask(f"""
        Given the recipe name '{recipe}', return a JSON with:
        - description: a short description (2-3 sentences)
        - difficulty: one of [Easy, Medium, Hard]

        Respond with raw JSON only. No markdown, no backticks, no extra text.
        """)

        #print(f"Generated recipe for '{recipe}' using model '{model_name}': {result}")
        return json.loads(result)
    except Exception as e:
        print(f"Error: {e}")
        raise

#generate("Pizza Margherita")