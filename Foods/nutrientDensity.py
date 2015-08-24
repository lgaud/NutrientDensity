import numpy as np
import pandas

def rdiByCalories(nutrient, rdi, calories, caloriesRDI = 2000):
    return (nutrient/rdi) / (calories/caloriesRDI)

foods = pandas.read_csv("USDA_ABBREV.csv")
nutrientRecommendations = pandas.read_csv("NutrientRDA.csv")

transposedNutrients = nutrientRecommendations.T

nutrient_cap = 10 # Avoid one nutrient dominating averages too much

foods = foods.fillna(0) # Replace missing values with 0
foods = foods[foods["Energ_Kcal"] > 0] # Exclude calorie free items
foods["MicroNutrientScore"] = 0

learningColumns = ["MicroNutrientScore"]
goodNutrientColumns = []
nutrientCount = 0
for i in transposedNutrients:
    name = transposedNutrients[i][0]
    columnName = transposedNutrients[i][3] + "_Density"  # Remove Unit information
    foods[columnName] = rdiByCalories(foods[name], transposedNutrients[i][1], foods["Energ_Kcal"]).clip_lower(0)
    learningColumns.append(columnName)
    if transposedNutrients[i][2] == 0:        
        foods["MicroNutrientScore"] = foods["MicroNutrientScore"] + foods[columnName].clip_upper(nutrient_cap)
        goodNutrientColumns.append(columnName)
        nutrientCount = nutrientCount + 1

foods["MicroNutrientScore"] = foods["MicroNutrientScore"] / nutrientCount

sortedByScore = foods.sort(["MicroNutrientScore"], ascending=False)
sortedByScore.to_csv("food_out.csv")