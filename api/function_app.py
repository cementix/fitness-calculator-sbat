import json
import logging

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

ACTIVITY_FACTORS = {
    'sedentary': 1.2,
    'light': 1.375,
    'moderate': 1.45,
    'active': 1.725,
    'very_active': 1.9,
}

GOAL_CALORIE_ADJUSTMENTS = {
    'lose': -500,
    'maintain': 0,
    'gain': 300,
}


def bmi_category(bmi):
    if bmi < 18.5:
        return 'Underweight'
    if bmi < 25:
        return 'Normal weight'
    if bmi < 30:
        return 'Overweight'
    return 'Obesity'


def round_to(value, step):
    return round(value / step) * step


def calculate_fitness(data):
    age = int(data['age'])
    gender = data['gender']
    height = float(data['height'])
    weight = float(data['weight'])
    activity_level = data['activityLevel']
    goal = data['goal']

    if gender == 'male':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    elif gender == 'female':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        raise ValueError('gender must be male or female')

    if activity_level not in ACTIVITY_FACTORS:
        raise ValueError('unknown activityLevel')
    if goal not in GOAL_CALORIE_ADJUSTMENTS:
        raise ValueError('unknown goal')

    bmi = weight / ((height / 100) ** 2)
    tdee = bmr * ACTIVITY_FACTORS[activity_level]
    target_calories = tdee + GOAL_CALORIE_ADJUSTMENTS[goal]

    return {
        'bmi': round(bmi, 1),
        'bmiCategory': bmi_category(bmi),
        'bmr': round_to(bmr, 100),
        'tdee': round_to(tdee, 100),
        'targetCalories': round_to(target_calories, 100),
        'protein': round_to(weight * 1.8, 10),
        'water': round(weight * 0.033, 1),
    }


@app.route(route="FitnessCalculator", methods=["POST"])
def FitnessCalculator(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        result = calculate_fitness(req.get_json())
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json",
        )
    except (KeyError, TypeError, ValueError) as exc:
        return func.HttpResponse(
            json.dumps({'error': str(exc)}),
            status_code=400,
            mimetype="application/json",
        )
