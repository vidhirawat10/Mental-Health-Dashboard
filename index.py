# index.py

from dash import dcc, html, Input, Output, State
from app import app, server 
from pages import stress_analyzer, survey_results 

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pandas.api.types import CategoricalDtype 


try:
    df = pd.read_csv('data/cleaned_mental_health_survey.csv')
    print("Cleaned data loaded successfully in index.py for callbacks.")
except FileNotFoundError:
    print("Error: 'cleaned_mental_health_survey.csv' not found. Make sure it's in the 'data/' directory.")
    
    df = pd.DataFrame(columns=['Age_Group', 'Gender', 'Country', 'treatment', 'no_employees', 'self_employed', 'family_history', 'remote_work', 'tech_company', 'benefits', 'care_options', 'wellness_program', 'seek_help', 'anonymity', 'leave', 'mental_health_consequence', 'phys_health_consequence', 'coworkers', 'supervisor', 'mental_health_interview', 'phys_health_interview', 'mental_vs_physical', 'obs_consequence', 'work_interfere'])



def calculate_stress_index(sleep_hours, work_hours, screen_time, activity, caffeine,
                           q_stressed, q_interfere, q_sleep_well, q_policies, q_talk_to_someone):
    score = 0

    if sleep_hours is None: sleep_hours = 7
    if work_hours is None: work_hours = 8
    if screen_time is None: screen_time = 6
    if activity is None: activity = 30
    if caffeine is None: caffeine = 2
    if q_stressed is None: q_stressed = 'Sometimes'
    if q_interfere is None: q_interfere = 'No'
    if q_sleep_well is None: q_sleep_well = 'Yes'
    if q_policies is None: q_policies = 'No'
    if q_talk_to_someone is None: q_talk_to_someone = 'Yes'

    if sleep_hours < 5 or sleep_hours > 9:
        score += 20
    elif (5 <= sleep_hours < 6) or (8 < sleep_hours <= 9):
        score += 10
    if work_hours > 10:
        score += 15
    elif 9 <= work_hours <= 10:
        score += 10
    if screen_time > 10:
        score += 15
    elif 6 < screen_time <= 10:
        score += 10
    if activity < 10:
        score += 15
    elif 10 <= activity < 30:
        score += 10
    if caffeine > 5:
        score += 10
    elif 3 <= caffeine <= 5:
        score += 5

    risky_answers = 0
    if q_stressed in ['Often', 'Always']: risky_answers += 1
    if q_interfere in ['Yes', 'Sometimes']: risky_answers += 1
    if q_sleep_well == 'No': risky_answers += 1
    if q_policies == 'No': risky_answers += 1
    if q_talk_to_someone == 'No': risky_answers += 1
    score += risky_answers * 5

    return min(score, 100)

def stress_category(score):
    if score <= 40:
        return "🟢 Low Stress"
    elif 40 < score <= 70:
        return "🟡 Moderate Stress"
    else:
        return "🔴 High Stress"

def get_risk_factors_and_recommendations(sleep_hours, work_hours, screen_time, activity, caffeine,
                                           q_stressed, q_interfere, q_sleep_well, q_policies, q_talk_to_someone):
    risk_factors = []
    recommendations = []

    if sleep_hours is None: sleep_hours = 7
    if work_hours is None: work_hours = 8
    if screen_time is None: screen_time = 6
    if activity is None: activity = 30
    if caffeine is None: caffeine = 2
    if q_stressed is None: q_stressed = 'Sometimes'
    if q_interfere is None: q_interfere = 'No'
    if q_sleep_well is None: q_sleep_well = 'Yes'
    if q_policies is None: q_policies = 'No'
    if q_talk_to_someone is None: q_talk_to_someone = 'Yes'

    if sleep_hours < 5:
        risk_factors.append("Low sleep duration")
        recommendations.append("Increase sleep to at least 7 hours per day.")
    elif sleep_hours > 9:
        risk_factors.append("Excessive sleep duration (could indicate an underlying issue)")
        recommendations.append("Consult a health professional if excessive sleep persists.")
    if work_hours > 10:
        risk_factors.append("Very high work hours")
        recommendations.append("Consider reducing work hours or improving work-life balance.")
    elif 9 <= work_hours <= 10:
        risk_factors.append("High work hours")
        recommendations.append("Ensure you're taking regular breaks and managing your workload effectively.")
    if screen_time > 10:
        risk_factors.append("Very high screen time")
        recommendations.append("Aim to reduce screen time, especially before bed. Try digital detox periods.")
    elif 6 < screen_time <= 10:
        risk_factors.append("High screen time")
        recommendations.append("Take regular breaks from screens (e.g., 20-20-20 rule).")
    if activity < 10:
        risk_factors.append("Very low physical activity")
        recommendations.append("Incorporate at least 30 minutes of moderate exercise most days.")
    elif 10 <= activity < 30:
        risk_factors.append("Low physical activity")
        recommendations.append("Increase physical activity to recommended levels (e.g., 30 mins daily).")
    if caffeine > 5:
        risk_factors.append("Very high caffeine intake")
        recommendations.append("Consider reducing caffeine intake, especially in the afternoon.")
    elif 3 <= caffeine <= 5:
        risk_factors.append("High caffeine intake")
        recommendations.append("Be mindful of your caffeine consumption and its impact on sleep.")
    if q_stressed in ['Often', 'Always']:
        risk_factors.append("Frequent feelings of stress")
        recommendations.append("Explore stress management techniques like mindfulness or meditation.")
    if q_interfere in ['Yes', 'Sometimes']:
        risk_factors.append("Mental state interferes with work/study")
        recommendations.append("Consider speaking to a mental health professional or your HR department.")
    if q_sleep_well == 'No':
        risk_factors.append("Trouble sleeping or concentrating")
        recommendations.append("Improve sleep hygiene and consult a doctor if sleep issues persist.")
    if q_policies == 'No':
        risk_factors.append("Lack of awareness of company mental health policies")
        recommendations.append("Familiarize yourself with your company's mental health resources and policies.")
    if q_talk_to_someone == 'No':
        risk_factors.append("Unwillingness to discuss mental health with colleagues/supervisors")
        recommendations.append("Remember that seeking support is a strength. Confidential resources might be available.")

    return list(set(risk_factors)), list(set(recommendations))


app.layout = html.Div(
    style={'backgroundColor': '#222222', 'color': 'white', 'minHeight': '100vh'}, # Global dark background for the entire app
    children=[
        dcc.Location(id='url', refresh=False),
        html.Div([
            html.H1(children='Mental Health Dashboard', style={'textAlign': 'center', 'color': '#66CCFF', 'marginBottom': '10px'}), # Heading for dark mode
            html.Div(children='''
                Insights and personalized analysis on mental health in the tech industry.
            ''', style={'textAlign': 'center', 'color': '#BBBBBB', 'marginBottom': '20px'}), # Subtitle for dark mode

            # Navigation Links
            html.Div([
                dcc.Link('Personal Stress Analyzer', href='/', className='nav-button', style={'marginRight': '15px', 'textDecoration': 'none', 'padding': '10px 20px', 'backgroundColor': '#007BFF', 'color': 'white', 'borderRadius': '5px'}), # Adjusted button colors for dark mode
                dcc.Link('Survey Results & Trends', href='/survey-results', className='nav-button', style={'textDecoration': 'none', 'padding': '10px 20px', 'backgroundColor': '#20C997', 'color': 'white', 'borderRadius': '5px'}), # Adjusted button colors
            ], style={'textAlign': 'center', 'marginBottom': '30px'}),
        ], style={'padding': '20px', 'borderBottom': '1px solid #555', 'backgroundColor': '#212529'}), # Dark header background

        html.Div(id='page-content') # Content of selected page will be rendered here
    ]
)

# --- Callback to update page content based on URL ---
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/survey-results':
        return survey_results.layout
    else: # Default to stress analyzer page
        return stress_analyzer.layout

# --- Callbacks for Personalized Stress Analyzer ---
@app.callback(
    Output('stress-score-output', 'children'),
    Output('risk-category-output', 'children'),
    Output('risk-factors-output', 'children'),
    Output('recommendations-output', 'children'),
    Output('comparison-graph-output', 'children'),
    Input('analyze-button', 'n_clicks'),
    State('input-sleep', 'value'),
    State('input-work-hours', 'value'),
    State('input-screen-time', 'value'),
    State('input-activity', 'value'),
    State('input-caffeine', 'value'),
    State('q-stressed', 'value'),
    State('q-interfere', 'value'),
    State('q-sleep-well', 'value'),
    State('q-policies', 'value'),
    State('q-talk-to-someone', 'value'),
    State('input-age', 'value'),
    State('input-gender', 'value')
)
def update_stress_results(n_clicks, sleep, work_hours, screen_time, activity, caffeine,
                          q_stressed, q_interfere, q_sleep_well, q_policies, q_talk_to_someone,
                          age, gender):
    if n_clicks > 0:
        score = calculate_stress_index(sleep, work_hours, screen_time, activity, caffeine,
                                       q_stressed, q_interfere, q_sleep_well, q_policies, q_talk_to_someone)
        category_text = stress_category(score)
        risk_factors, recommendations = get_risk_factors_and_recommendations(
            sleep, work_hours, screen_time, activity, caffeine,
            q_stressed, q_interfere, q_sleep_well, q_policies, q_talk_to_someone
        )

        # --- Gauge Chart for Stress Score ---
        gauge_fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Your Stress Level", 'font': {'color': 'white'}}, # White title for dark mode
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"}, # White ticks
                'bar': {'color': "#66CCFF"}, # A nice blue for the bar
                'bgcolor': "#2C3E50", # Dark background for gauge
                'borderwidth': 2,
                'bordercolor': "#777",
                'steps': [
                    {'range': [0, 40], 'color': '#2ECC71'}, # Green
                    {'range': [41, 70], 'color': '#F1C40F'}, # Yellow
                    {'range': [71, 100], 'color': '#E74C3C'}], # Red
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': score}}
        ))
        gauge_fig.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10),
                                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)') 

        score_graph = dcc.Graph(figure=gauge_fig, config={'displayModeBar': False})

        risk_list_items = [html.Li(factor) for factor in risk_factors] if risk_factors else [html.Li("No significant risk factors identified based on inputs.")]
        reco_list_items = [html.Li(reco) for reco in recommendations] if recommendations else [html.Li("Continue your healthy habits!")]

        
        age_group_user = None
        bins = [0, 25, 35, 45, 55, 65, np.inf]
        labels = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
        if age is not None:
            for i in range(len(bins) - 1):
                if bins[i] <= age < bins[i+1]:
                    age_group_user = labels[i]
                    break
            if age >= 65:
                 age_group_user = '65+'

        if 'Age_Group' in df.columns and 'treatment' in df.columns:
            avg_treatment_by_age_group = df.groupby('Age_Group')['treatment'].apply(lambda x: (x == 'Yes').sum() / len(x) * 100).reset_index()
            avg_treatment_by_age_group.columns = ['Age_Group', 'Treatment_Percentage']

            valid_labels = [label for label in labels if label in avg_treatment_by_age_group['Age_Group'].unique()]
            avg_treatment_by_age_group['Age_Group'] = pd.Categorical(avg_treatment_by_age_group['Age_Group'], categories=valid_labels, ordered=True)
            avg_treatment_by_age_group = avg_treatment_by_age_group.sort_values('Age_Group')

            comparison_fig = px.bar(avg_treatment_by_age_group, x='Age_Group', y='Treatment_Percentage',
                                    title='Survey Data: % Seeking Treatment by Age Group',
                                    labels={'Treatment_Percentage': '% Seeking Treatment'},
                                    text='Treatment_Percentage',
                                    color='Age_Group',
                                    color_discrete_sequence=px.colors.qualitative.Plotly,
                                    template='plotly_dark' # Apply dark template here too
                                    )
            comparison_fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            comparison_fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',
                                          xaxis_title='Age Group', yaxis_title='% Seeking Treatment')

            if age_group_user and age_group_user in avg_treatment_by_age_group['Age_Group'].values:
                user_age_group_data = avg_treatment_by_age_group[avg_treatment_by_age_group['Age_Group'] == age_group_user]
                if not user_age_group_data.empty:
                    y_value_for_annotation = user_age_group_data['Treatment_Percentage'].iloc[0]
                    comparison_fig.add_annotation(
                        x=age_group_user,
                        y=y_value_for_annotation,
                        text=f"Your Age Group",
                        showarrow=True, arrowhead=2, ax=0, ay=-40,
                        font=dict(color="#FFD700", size=14, weight='bold'), 
                        bgcolor="rgba(0,0,0,0.8)", bordercolor="#FFD700", borderwidth=1, borderpad=4
                    )
            comparison_graph = dcc.Graph(figure=comparison_fig, config={'displayModeBar': False})
        else:
            comparison_graph = html.Div("Data for comparison graph is not available. Please ensure 'cleaned_mental_health_survey.csv' is correctly loaded.", style={'color': 'red'})

        return score_graph, category_text, html.Ul(risk_list_items), html.Ul(reco_list_items), comparison_graph
    return html.Div(), "", html.Ul(), html.Ul(), html.Div()

if __name__ == '__main__':
    app.run(debug=True)
