import numpy as np
import pandas

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

foods = pandas.read_csv("USDA_ABBREV.csv")
nutrientRecommendations = pandas.read_csv("NutrientRDA.csv")

transposedNutrients = nutrientRecommendations.T
def rdiByCalories(nutrient, rdi, calories, caloriesRDI = 2000):
    return (nutrient/rdi) / (calories/caloriesRDI)

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
    #else:
        #foods["NutrientScore"] = foods["NutrientScore"] - foods[columnName].clip_upper(nutrient_cap)


foods["MicroNutrientScore"] = foods["MicroNutrientScore"] / nutrientCount

#print(foods[foods["Calcium_(mg)_Density"] > 2]["NutrientsGt2"] + 1)

# Look at distribution of nutrients - find the number of nutrients whose denisty is greater than given thresholds
microNutrientScores = foods[goodNutrientColumns]
values = [0.5, 0.75, 1, 2]
for v in values:
    foods["NutrientsGt{0}".format(v)] = microNutrientScores[microNutrientScores > v].count(axis = 1)

numGoodNutrients = len(goodNutrientColumns)
def grade(row):
    if row["MicroNutrientScore"] > 3 and row["NutrientsGt1"] >= 5 and row["NutrientsGt0.5"] >= numGoodNutrients - 2: # Overall fantastic and has a wide range of nutrients
        return 5
    elif row["MicroNutrientScore"] > 2 and row["NutrientsGt1"] >= 3: # Overall great, and a great source of multiple nutrients
        return 4
    elif row["MicroNutrientScore"] > 1 and row["NutrientsGt0.75"] >= 3: # overall good, and a good source of multiple nutrients
        return 3
    elif row["MicroNutrientScore"] > 1 or row["NutrientsGt1"] >= 3: # Overall good, but could be dominated by one or two nutrients, or a good source of a few nutrients
        return 2
    elif row["NutrientsGt1"] > 0 or row["NutrientsGt0.75"] > 1 or row["NutrientsGt0.5"] > 2:  # A good source of at least one nutrient, or a source of at least 2
        return 1
    else:
        return 0

foods["Grade"] = foods.apply(grade,axis=1)
learningColumns.append("Grade")

#countGt2 = lambda row: [row[learningColumns] > 2].sum()

#foods["NutrientsGt2"] = foods.apply(countGt2,axis=1)
#for c in learningColumns:    
    #foods.loc[:,(foods[c] > 2, "NutrientsGt2")] = foods[foods[c] > 2]["NutrientsGt2"] + 1
    #foods[foods[c] > 1]["NutrientsGt1"] = foods[foods[c] > 1]["NutrientsGt1"] + 1
    #foods[foods[c] > 0.5]["NutrientsGt0.5"] = foods[foods[c] > 0.5]["NutrientsGt0.5"] + 1
#print foods[(foods["Fiber_TD_(g)_Density"] > 5)].head()


#Calories from fat (9Kcal/g)
foods["Fat_Cal_%"] =  (foods["Lipid_Tot_(g)"] * 9) / foods["Energ_Kcal"]
foods["Prot_Cal_%"] = (foods["Protein_(g)"] * 4) / foods["Energ_Kcal"]
foods["Carb_Cal_%"] = ((foods["Carbohydrt_(g)"] - foods["Fiber_TD_(g)"]) * 4) / foods["Energ_Kcal"]
foods["Total_Cal_%"] = foods["Fat_Cal_%"] + foods["Prot_Cal_%"] + foods["Carb_Cal_%"]
foods["Sugar_Cal_%"] = (foods["Sugar_Tot_(g)"] * 4) / foods["Energ_Kcal"]


#print foods[foods["NutrientScore"] > 7]
#Calories from protein (4Kcal/g)
#Calories from carbs (4Kcal/g)
print foods[learningColumns].describe()

def cluster():
    normalizedFoods = foods[learningColumns] / foods[learningColumns].max()
    km = KMeans()
    km.fit_predict(normalizedFoods)

    #print(km.labels_)

    foods["Cluster"] = km.labels_
    #print km.cluster_centers_
    clusterGroups = foods.groupby("Cluster")
    print(clusterGroups[learningColumns].mean())

sortedByScore = foods.sort(["MicroNutrientScore"], ascending=False)
sortedByScore.to_csv("food_out.csv")


columnsWithName = learningColumns
columnsWithName.append("Shrt_Desc")

#gradeGroups = foods.groupby("Grade")
#print gradeGroups[learningColumns].mean()


#Find the best food for each nutrient, by density
#print foods[goodNutrientColumns].idxmax()

bestOfEachNutrient = foods[foods.index.isin(foods[goodNutrientColumns].idxmax())]


#print bestOfEachNutrient[goodNutrientColumns].describe()
with plt.xkcd():
    print bestOfEachNutrient
    #print bestOfEachNutrient[goodNutrientColumns.append("Shrt_Desc")].pivot(index="Shrt_Desc")

def scatterplot(x, y, colors):
    with plt.xkcd():
        fig = plt.figure()
        plt.xlabel(x)
        plt.ylabel(y)
        plt.scatter(foods[x], foods[y], c=foods[colors])
        plt.legend(foods[colors].unique())
        plt.show()
        
def bar(data):
    with plt.xkcd():
        data.plot(kind="bar")

#lines(foods[columnsWithName][0:10])

scatterplot("MicroNutrientScore", "Fiber_Density", "Grade")
#plot(foods["NutrientScore"], foods["Potassium_(mg)_Density"], foods["Cluster"])
#scatterplot("NutrientScore", "Sugar_Tot_(g)_Density", "Cluster")
#scatterplot("Fiber_TD_(g)_Density", "Sugar_Tot_(g)_Density", "Cluster")
#plot(foods["NutrientScore"], foods["Calcium_(mg)_Density"], foods["Cluster"])
#plot(foods["NutrientScore"], foods["Sodium_(mg)_Density"], foods["Cluster"])
#plot(foods["NutrientScore"], foods["Folate_Tot_(æg)_Density"], foods["Cluster"])
#plot(foods["NutrientScore"], foods["Vit_E_(mg)_Density"], foods["Cluster"])




# Treat Points = Calories/75 - 0.25*(Protein+Fibre) 
#foods["treat_points1"] = foods["Energ_Kcal"] / 75 - 0.25 * (foods["Protein_(g)"] + foods["Fiber_TD_(g)"])
#foods["treat_points2"] = foods["Sugar_Tot_(g)"] * 4 + foods["Lipid_Tot_(g)"] * 9
#sorted = foods.sort(["treat_points2"], ascending=False)

#print(sorted[["Shrt_Desc", "treat_points2", "Energ_Kcal", "Protein_(g)", "Fiber_TD_(g)"]][:30])
#sorted.to_csv("food_out2.csv")
