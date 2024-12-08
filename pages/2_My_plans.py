import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pandas as pd

# Must be the first Streamlit command
st.set_page_config(
    page_title="Meal Plan Tracker",
    page_icon="🍽️",
    layout="wide"
)

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate('firebase-adminsdk.json')
    firebase_admin.initialize_app(cred)
db = firestore.client()

class MealPlanTracker:
    def __init__(self):
        """Initialize Firebase and Streamlit configuration"""
        self._add_custom_css()

    def _add_custom_css(self):
        """Add custom CSS styling"""
        st.markdown("""
            <style>
            .plan-container { padding: 20px; border-radius: 5px; margin: 10px 0; }
            .meal-header { color: #0066cc; font-weight: bold; }
            .nutrition-info { color: #666; font-size: 14px; }
            </style>
        """, unsafe_allow_html=True)

    def check_authentication(self):
        """Validate user authentication"""
        if 'user' not in st.session_state:
            st.warning("Please log in to access Meal Plan Tracker")
            return False
        return True

    def delete_plan(self, plan_id):
        """
        Delete a specific meal plan
        
        Args:
            plan_id (str): Firestore document ID of the plan
        
        Returns:
            bool: Success status of deletion
        """
        try:
            db.collection('meal_plans').document(plan_id).delete()
            st.success("Meal plan deleted successfully!")
            return True
        except Exception as e:
            st.error(f"Failed to delete meal plan: {e}")
            return False

def save_generated_plan(plan_data, user_metrics):
    if 'user' not in st.session_state:
        st.warning("Please log in to save your plan")
        return False
    
    try:
        plan_ref = db.collection('meal_plans').document()
        plan_ref.set({
            'user_id': st.session_state.user['uid'],
            'created_at': firestore.SERVER_TIMESTAMP,
            'plan_data': plan_data,
            'user_metrics': user_metrics
        })
        return True
    except Exception as e:
        st.error(f"Failed to save plan: {e}")
        return False

def get_user_plans():
    try:
        plans = db.collection('meal_plans')\
            .where('user_id', '==', st.session_state.user['uid'])\
            .get()
        return [{'id': plan.id, **plan.to_dict()} for plan in plans]
    except Exception as e:
        st.error(f"Error fetching plans: {e}")
        return []

def display_saved_plans():
    plans = get_user_plans()
    if not plans:
        st.info("No saved meal plans found")
        return
        
    for plan in plans:
        with st.expander(f"Plan from {plan.get('created_at', datetime.now()).strftime('%Y-%m-%d')}"):
            st.write("### Plan Details")
            if 'user_metrics' in plan:
                metrics = plan['user_metrics']
                st.write(f"- Weight: {metrics.get('weight')} kg")
                st.write(f"- Height: {metrics.get('height')} cm")
                st.write(f"- Daily Calories: {metrics.get('Calories', 0):.0f}")
            
            st.write("### Meal Plan")
            for week, meals in plan.get('plan_data', {}).items():
                st.write(f"#### {week}")
                for day, day_meals in meals.items():
                    for meal_type, items in day_meals.items():
                        if isinstance(items, list):
                            st.write(f"*{meal_type}*")
                            for item in items:
                                st.write(f"• {item['Food']}")

def main():
    st.title("My Saved Meal Plans")
    
    if 'user' not in st.session_state:
        st.warning("Please log in to view your plans")
        return
        
    display_saved_plans()

if st.button("Generate 4-Week Meal Plan"):
    if name and age and weight and height:
        bmr = calculate_bmr(weight, height, age, gender)
        daily_calories = calculate_calories(bmr, activity_level)
        
        user_metrics = {
            'weight': weight,
            'height': height,
            'age': age,
            'gender': gender,
            'activity_level': activity_level,
            'Calories': daily_calories,
            'Diet': dietary_pref,
            'Conditions': health_conditions
        }
        
        four_week_plan = generate_four_week_plan(user_requirements, food_data)
        display_four_week_plan(four_week_plan)
        
        # Add save button after plan generation
        if st.button("💾 Save Plan"):
            save_generated_plan(four_week_plan, user_metrics)

if __name__ == "__main__":
    main()