import streamlit as st
import pandas as pd
import random
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# Sidebar Styling
st.sidebar.markdown(
    """
    <style>
    [data-testid="stSidebar"]::before {
        content: "NutriUsher 🥗"; 
        font-size: 24px; 
        font-weight: bold; 
        padding: 120px 90px 0px 30px;
        display: block;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# Firebase initialization
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate('firebase-adminsdk.json')
        firebase_admin.initialize_app(cred)
        st.write("Firebase initialized successfully.")
    except Exception as e:
        st.error(f"Firebase initialization failed: {e}")

# Initialize Firestore
db = firestore.client()

# Function to check login
def check_login():
    if 'user' not in st.session_state:
        st.error("You must be logged in to view your diet plans.")
        return False
    return True

# Load data
def load_data():
    food_data = pd.read_csv('food.csv')
    user_data = pd.read_csv('user_nutritional_data.csv')
    return food_data, user_data

# Generate meal plan
def generate_meal_plan(user_requirements, food_data):
    breakfast_items = food_data[food_data['Breakfast'] == 1]
    lunch_items = food_data[food_data['Lunch'] == 1]
    dinner_items = food_data[food_data['Dinner'] == 1]

    daily_plan = {
        'Breakfast': [],
        'Lunch': [],
        'Dinner': []
    }

    # Target values from user requirements
    target_calories = user_requirements['Calories']
    target_proteins = user_requirements['Proteins']
    target_carbs = user_requirements['Carbs']
    target_fats = user_requirements['Fats']

    # Select items for each meal
    for meal, items in daily_plan.items():
        if meal == 'Breakfast':
            meal_items = breakfast_items
        elif meal == 'Lunch':
            meal_items = lunch_items
        else:
            meal_items = dinner_items

        # Select 2-3 items per meal
        num_items = random.randint(2, 3)
        selected_items = meal_items.sample(n=min(num_items, len(meal_items)))
        daily_plan[meal] = selected_items

    return daily_plan

def generate_four_week_plan(user_input, food_data):
    weeks = 4
    days_per_week = 7
    meals = ['Breakfast', 'Lunch', 'Dinner']
    full_plan = {}
    
    # Track used meals to ensure variety
    used_meals = {meal: set() for meal in meals}
    
    for week in range(1, weeks + 1):
        for day in range(1, days_per_week + 1):
            day_menu = {}
            day_id = f"Week {week} Day {day}"
            
            for meal in meals:
                meal_recommendations = recommend_food(user_input, food_data, meal)
                
                if not meal_recommendations.empty:
                    # Filter out recently used meals
                    available_meals = meal_recommendations[
                        ~meal_recommendations['Food_items'].isin(used_meals[meal])
                    ]
                    
                    # If too few options, reset the used meals tracking
                    if len(available_meals) < 3:
                        used_meals[meal].clear()
                        available_meals = meal_recommendations
                    
                    # Select meals
                    selected_meals = available_meals.sample(
                        n=min(3, len(available_meals)),
                        random_state=week*100 + day
                    )
                    
                    # Track used meals
                    used_meals[meal].update(selected_meals['Food_items'].tolist())
                    
                    # Keep only last 7 days of used meals
                    if len(used_meals[meal]) > 21:  # 7 days * 3 meals
                        used_meals[meal] = set(list(used_meals[meal])[-21:])
                    
                    day_menu[meal] = [
                        {
                            'Food': meal_item['Food_items'],
                            'Calories': meal_item['Calories'],
                            'Proteins': meal_item['Proteins'],
                            'Carbs': meal_item['Carbohydrates'],
                            'Fats': meal_item['Fats'],
                            'Sugars': meal_item['Sugars'],
                            'Sodium': meal_item['Sodium']
                        }
                        for _, meal_item in selected_meals.iterrows()
                    ]
                else:
                    day_menu[meal] = 'No suitable meal found'
            
            full_plan[day_id] = day_menu
    
    return full_plan

def create_plan_dataframe(meal_plan):
    rows = []
    for day, meals in meal_plan.items():
        for meal_type, items in meals.items():
            if isinstance(items, list):
                for item in items:
                    rows.append({
                        'Day': day,
                        'Meal': meal_type,
                        'Food': item['Food'],
                        'Calories': item['Calories'],
                        'Proteins': item['Proteins'],
                        'Carbs': item['Carbs'],
                        'Fats': item['Fats'],
                        'Sugars': item['Sugars'],
                        'Sodium': item['Sodium']
                    })
    return pd.DataFrame(rows)

def display_four_week_plan(four_week_plan):
    # Create tabs for each week
    week_tabs = st.tabs([f"Week {i}" for i in range(1, 5)])
    
    for week_num, week_tab in enumerate(week_tabs, 1):
        with week_tab:
            week_data = four_week_plan[f'Week {week_num}']
            
            # Style for the table
            st.markdown("""
                <style>
                .meal-table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 10px 0;
                }
                .meal-table th, .meal-table td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                .meal-table th {
                    background-color: #0066cc;
                    color: white;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Create columns for days
            cols = st.columns(7)
            
            # Display days as headers
            for col, day in zip(cols, week_data.keys()):
                with col:
                    st.markdown(f"**{day}**")
                    
                    # Display meals in expandable sections
                    for meal_type, items in week_data[day].items():
                        with st.expander(meal_type):
                            total_calories = 0
                            total_proteins = 0
                            total_carbs = 0
                            total_fats = 0
                            
                            for _, item in items.iterrows():
                                st.write(f"• {item['Food_items']}")
                                total_calories += item['Calories']
                                total_proteins += item['Proteins']
                                total_carbs += item['Carbohydrates']
                                total_fats += item['Fats']
                            
                            st.markdown(f"""
                                **Totals:**
                                - Cal: {total_calories:.0f}
                                - Pro: {total_proteins:.1f}g
                                - Carb: {total_carbs:.1f}g
                                - Fat: {total_fats:.1f}g
                            """)

            # Display daily totals
            st.markdown("### Daily Totals")
            daily_totals = {}
            
            for day, meals in week_data.items():
                day_total = {'Calories': 0, 'Proteins': 0, 'Carbs': 0, 'Fats': 0}
                for meal_type, items in meals.items():
                    for _, item in items.iterrows():
                        day_total['Calories'] += item['Calories']
                        day_total['Proteins'] += item['Proteins']
                        day_total['Carbs'] += item['Carbohydrates']
                        day_total['Fats'] += item['Fats']
                daily_totals[day] = day_total
            
            # Create totals dataframe
            totals_df = pd.DataFrame(daily_totals).T
            st.dataframe(totals_df.round(1), use_container_width=True)

def calculate_nutrition(meal_plan):
    total_nutrition = {
        'Calories': 0,
        'Proteins': 0,
        'Carbs': 0,
        'Fats': 0
    }
    
    for meal, items in meal_plan.items():
        for _, item in items.iterrows():
            total_nutrition['Calories'] += item['Calories']
            total_nutrition['Proteins'] += item['Proteins']
            total_nutrition['Carbs'] += item['Carbohydrates']
            total_nutrition['Fats'] += item['Fats']
    
    return total_nutrition

def calculate_bmr(weight, height, age, gender):
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
    if gender == 'Male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return bmr

def calculate_calories(bmr, activity_level):
    """Calculate daily calorie needs based on activity level"""
    activity_multipliers = {
        'Sedentary': 1.2,
        'Light Exercise': 1.375,
        'Moderate Exercise': 1.55,
        'Heavy Exercise': 1.725
    }
    return bmr * activity_multipliers.get(activity_level, 1.2)

def recommend_food(user_input, food_data, meal):
    # Calculate meal-specific calorie targets
    daily_calories = user_input['Calories']
    meal_calories = {
        'Breakfast': daily_calories * 0.3,
        'Lunch': daily_calories * 0.4,
        'Dinner': daily_calories * 0.3
    }

    # Filter by meal timing (using meal column from food data)
    filtered_foods = food_data[food_data[meal] == 1]

    # Apply dietary preference filter
    if user_input['Diet'] != 'All':
        filtered_foods = filtered_foods[filtered_foods['Diet'] == (1 if user_input['Diet'] == 'Non-Veg' else 0)]

    # Apply health condition filters
    if user_input['Condition']:
        for condition in user_input['Condition']:
            if condition == 'Diabetes':
                filtered_foods = filtered_foods[filtered_foods['Sugars'] < 5]
            elif condition == 'Heart Disease':
                filtered_foods = filtered_foods[filtered_foods['Fats'] < 10]
            elif condition == 'Hypertension':
                filtered_foods = filtered_foods[filtered_foods['Sodium'] < 500]

    # Filter by meal calories
    filtered_foods = filtered_foods[filtered_foods['Calories'] <= meal_calories[meal]]

    return filtered_foods

def recommend_weekly_meals(user_input, food_data):
    meals = {'Breakfast': [], 'Lunch': [], 'Dinner': []}
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_plan = {}

    for day in days:
        daily_meals = {}
        for meal in meals:
            recommendations = recommend_food(user_input, food_data, meal)
            if not recommendations.empty:
                # Select 2-3 items per meal
                meal_items = recommendations.sample(n=min(3, len(recommendations)))
                daily_meals[meal] = [{
                    'Food': item['Food_items'],
                    'Calories': item['Calories'],
                    'Proteins': item['Proteins'],
                    'Carbs': item['Carbohydrates'],
                    'Fats': item['Fats'],
                    'Sugars': item['Sugars'],
                    'Sodium': item['Sodium']
                } for _, item in meal_items.iterrows()]
            else:
                daily_meals[meal] = "No suitable options found"
        weekly_plan[day] = daily_meals

    return weekly_plan

def create_meal_plan_table(four_week_plan):
    # Create lists to store data
    records = []
    
    for day_id, day_meals in four_week_plan.items():
        week_num = day_id.split()[1]
        day_num = day_id.split()[3]
        
        for meal_type, items in day_meals.items():
            if isinstance(items, list):
                # Join multiple food items with newlines
                foods = "\n".join([f"• {item['Food']}" for item in items])
                # Calculate meal totals
                total_calories = sum(item['Calories'] for item in items)
                total_proteins = sum(item['Proteins'] for item in items)
                total_carbs = sum(item['Carbs'] for item in items)
                total_fats = sum(item['Fats'] for item in items)
                
                records.append({
                    'Week': f"Week {week_num}",
                    'Day': f"Day {day_num}",
                    'Meal': meal_type,
                    'Foods': foods,
                    'Calories': f"{total_calories:.0f}",
                    'Proteins (g)': f"{total_proteins:.1f}",
                    'Carbs (g)': f"{total_carbs:.1f}",
                    'Fats (g)': f"{total_fats:.1f}"
                })
    
    return pd.DataFrame(records)

def display_meal_plan(four_week_plan):
    df = create_meal_plan_table(four_week_plan)
    
    # Create tabs for each week
    week_tabs = st.tabs(["Week 1", "Week 2", "Week 3", "Week 4"])
    
    # Display data in each tab
    for week_num, tab in enumerate(week_tabs, 1):
        with tab:
            week_data = df[df['Week'] == f"Week {week_num}"]
            
            try:
                # Reset index and format table
                display_df = week_data.reset_index(drop=True)
                
                # Display table
                st.dataframe(
                    display_df,
                    column_config={
                        "Foods": st.column_config.TextColumn(
                            "Foods",
                            width="large",
                            help="Daily meal items"
                        ),
                        "Calories": st.column_config.NumberColumn(
                            "Calories",
                            format="%d"
                        ),
                        "Proteins (g)": st.column_config.NumberColumn(
                            "Proteins (g)",
                            format="%.1f"
                        ),
                        "Carbs (g)": st.column_config.NumberColumn(
                            "Carbs (g)",
                            format="%.1f"
                        ),
                        "Fats (g)": st.column_config.NumberColumn(
                            "Fats (g)",
                            format="%.1f"
                        )
                    },
                    hide_index=True,
                    height=400
                )
                
                # Weekly totals
                weekly_totals = display_df.agg({
                    'Calories': lambda x: f"{x.astype(float).sum():.0f}",
                    'Proteins (g)': lambda x: f"{x.astype(float).sum():.1f}",
                    'Carbs (g)': lambda x: f"{x.astype(float).sum():.1f}",
                    'Fats (g)': lambda x: f"{x.astype(float).sum():.1f}"
                })
                
                st.markdown(f"""
                **Weekly Totals:**
                - Calories: {weekly_totals['Calories']}
                - Proteins: {weekly_totals['Proteins (g)']}g
                - Carbs: {weekly_totals['Carbs (g)']}g
                - Fats: {weekly_totals['Fats (g)']}g
                """)
                
            except Exception as e:
                st.error(f"Error displaying table for Week {week_num}: {str(e)}")

# Main function
def main():
    st.title("Diet Plan Generator")
    
    # User inputs
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1, step=1)
    gender = st.selectbox("Gender", ["Male", "Female"])
    weight = st.number_input("Weight (kg)", min_value=1.0, step=0.1)
    height = st.number_input("Height (cm)", min_value=1.0, step=0.1)
    activity_level = st.selectbox("Activity Level", 
        ['Sedentary', 'Light Exercise', 'Moderate Exercise', 'Heavy Exercise'])

    food_data, user_data = load_data()

    if food_data is not None:
        # Use 'Diet' column instead of 'Dietary Preference'
        dietary_pref = st.selectbox("Dietary Preference", ['All'] + list(food_data['Diet'].unique()))
        health_conditions = st.multiselect("Health Conditions", 
            ['None', 'Diabetes', 'Hypertension', 'Heart Disease'])
    else:
        dietary_pref, health_conditions = None, []

    if st.button("Generate 4-Week Plan"):
        if name and age and weight and height:
            bmr = calculate_bmr(weight, height, age, gender)
            daily_calories = calculate_calories(bmr, activity_level)
            
            user_requirements = {
                'Calories': daily_calories,
                'BMR': bmr,
                'Proteins': int(daily_calories * 0.15 / 4),
                'Carbs': int(daily_calories * 0.55 / 4),
                'Fats': int(daily_calories * 0.30 / 9),
                'Diet': dietary_pref,
                'Condition': health_conditions
            }
            
            four_week_plan = generate_four_week_plan(user_requirements, food_data)
            display_meal_plan(four_week_plan)
            
            # # Create downloadable CSV
            # plan_df = create_meal_plan_table(four_week_plan)
            # csv = plan_df.to_csv(index=False)
            # st.download_button(
            #     label="Download 4-Week Plan",
            #     data=csv,
            #     file_name="four_week_diet_plan.csv",
            #     mime="text/csv"
            # )
        else:
            st.error("Please fill all the required fields.")
    else:
        return

if __name__ == "__main__":
    main()