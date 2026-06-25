import requests
from langchain_core.tools import tool
from database import get_vector_db_retriever
import config

@tool
def search_cookbook_recipes(query: str) -> str:
    """Search the local GSB cookbook database for specific recipes, cooking instructions, and ingredients list."""
    retriever = get_vector_db_retriever()
    search_term = query
    if len(query.split()) == 1:
        search_term = f"{query} with exact quantities measurements tablespoons cups preparation instructions"
    docs = retriever.invoke(search_term)
    return "\n\n".join([f"[Page {d.metadata.get('page')}]: {d.page_content}" for d in docs])

@tool
def get_calorie_details(food_item: str) -> str:
    """Get the specific calorie and nutritional details for raw ingredients using the free USDA database."""
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "api_key": config.USDA_API_KEY,
        "query": food_item,
        "pageSize": 1
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return f"[Tool Output]: Error contacting open database. HTTP Status: {response.status_code}."
            
        json_data = response.json()
        if "foods" not in json_data or len(json_data["foods"]) == 0:
            return f"[Tool Output]: Could not find ingredient '{food_item}' in the open data registry."
            
        food = json_data["foods"][0]
        description = food.get("description", "")
        nutrients = food.get("foodNutrients", [])
        
        macros = {"Energy": "Unknown", "Protein": "Unknown", "Total lipid": "Unknown", "Carbohydrate": "Unknown"}
        for n in nutrients:
            name = n.get("nutrientName", "")
            val = n.get("value", 0)
            if "Energy" in name: macros["Energy"] = f"{val} kcal"
            elif "Protein" in name: macros["Protein"] = f"{val}g"
            elif "Total lipid" in name: macros["Total lipid"] = f"{val}g"
            elif "Carbohydrate" in name: macros["Carbohydrate"] = f"{val}g"
            
        return (f"[Tool Output]: Based on the USDA database, 100g of '{description}' contains: "
                f"Calories: {macros['Energy']}, Protein: {macros['Protein']}, Fat: {macros['Total lipid']}, Carbs: {macros['Carbohydrate']}.")
    except Exception as e:
        return f"[Tool Output]: Connection error to USDA API: {str(e)}"

# Unified tools list Export
PROVIDABLE_TOOLS = [search_cookbook_recipes, get_calorie_details]
