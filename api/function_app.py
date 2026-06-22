import azure.functions as func
import logging
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="CalculateFitnessIndicators", methods=["POST"])
def CalculateFitnessIndicators(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("CalculateFitnessIndicators function processed a request.")

    try:
        data = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON body"}),
            status_code=400,
            mimetype="application/json"
        )

    try:
        age = int(data.get("age"))
        gender = data.get("gender")
        height = float(data.get("height"))
        weight = float(data.get("weight"))
        activity_level = data.get("activityLevel")
        goal = data.get("goal")
    except (TypeError, ValueError):
        return func.HttpResponse(
            json.dumps({"error": "Missing or invalid input data"}),
            status_code=400,
            mimetype="application/json"
        )

    if age <= 0 or height <= 0 or weight <= 0:
        return func.HttpResponse(
            json.dumps({"error": "Age, height and weight must be positive numbers"}),
            status_code=400,
            mimetype="application/json"
        )

    if gender not in ["male", "female"]:
        return func.HttpResponse(
            json.dumps({"error": "Gender must be male or female"}),
            status_code=400,
            mimetype="application/json"
        )

    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }

    if activity_level not in activity_multipliers:
        return func.HttpResponse(
            json.dumps({"error": "Invalid activity level"}),
            status_code=400,
            mimetype="application/json"
        )

    bmi = weight / ((height / 100) ** 2)

    if bmi < 18.5:
        bmi_category = "Underweight"
    elif bmi < 25:
        bmi_category = "Normal weight"
    elif bmi < 30:
        bmi_category = "Overweight"
    else:
        bmi_category = "Obesity"

    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    tdee = bmr * activity_multipliers[activity_level]

    if goal == "lose":
        target_calories = tdee - 500
    elif goal == "maintain":
        target_calories = tdee
    elif goal == "gain":
        target_calories = tdee + 300
    else:
        return func.HttpResponse(
            json.dumps({"error": "Invalid goal"}),
            status_code=400,
            mimetype="application/json"
        )

    protein = weight * 1.8
    water = weight * 0.035

    result = {
        "bmi": round(bmi, 1),
        "bmiCategory": bmi_category,
        "bmr": round(bmr),
        "tdee": round(tdee),
        "targetCalories": round(target_calories),
        "protein": round(protein),
        "water": round(water, 1)
    }

    return func.HttpResponse(
        json.dumps(result),
        status_code=200,
        mimetype="application/json"
    )