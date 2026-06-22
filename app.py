from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder='.')

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


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/api/FitnessCalculator', methods=['POST'])
@app.route('/FitnessCalculator', methods=['POST'])
def fitness_calculator():
    try:
        data = request.get_json(force=True)
        return jsonify(calculate_fitness(data))
    except (KeyError, TypeError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400


if __name__ == '__main__':
    app.run()
