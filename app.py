from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__, static_folder='static')
import numpy as np
import pandas as pd
import random

Personality_traits = [
    'Personality [Supportive]',
    'Personality [Inspiring]',
    'Personality [Patient]',
    'Personality [Approachable]',
    'Personality [Honest]',
    'Personality [Insightful]',
    'Personality [Empathetic]'
]

Skill_traits = [
    'Skills [Technical]',
    'Skills [Communication]',
    'Skills [Networking]',
    'Skills [Problem Solving]',
    'Skills [Time Management]',
    'Skills [Resourceful]'
]

Support_traits = [
    'Support [Goal Setting Support]',
    'Support [Sharing Industry Knowledge + Experience]',
    'Support [Skill Development Feedback]',
    'Support [Personal Growth Support]',
    'Support [Technical Expertise]',
    'Support [Work-Life Balance Advice]',
    'Support [Building Confidence]',
    'Support [Emotional Support]'
]

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Handle file upload
            mentee_file = request.files['mentee_file']
            mentor_file = request.files['mentor_file']
            
            # Read the uploaded files into DataFrames
            mentees_df = pd.read_csv(mentee_file)
            mentors_df = pd.read_csv(mentor_file)
            
            # Call the matching function
            mentee_matches, unmatched_mentees, unmatched_mentors = match_mentees_to_mentors(mentees_df, mentors_df)
            
            # Render the results page with the matches
            return render_template('results.html', mentee_matches=mentee_matches, unmatched_mentees=unmatched_mentees, unmatched_mentors=unmatched_mentors)
        except KeyError as e:
            return f"Missing file: {e}", 400
    
    return render_template('index.html')

def match_mentees_to_mentors(mentees_df, mentors_df):
    # Store mentee and mentor preferences based on matching score order (dictionary for name and associated score)
    mentees_preferences = {}
    mentors_preferences = {}
    unmatched_mentees = []
    unmatched_mentors = []
    total_mentee_scores = {}  # for handling cases
    total_mentor_scores = {}

    # Iterate through each mentee data 
    for mentee_index, mentee_row in mentees_df.iterrows():
        mentee_discipline = mentee_row['What is your discipline?']

        # Create a new set of mentors that match current mentee's discipline
        matching_mentors_df = mentors_df[mentors_df['What is your discipline?'] == mentee_discipline]

        # Store mentor scores 
        mentor_scores = []
        total_score = 0

        # If no mentor with the same discipline as mentee
        if matching_mentors_df.empty:
            unmatched_mentees.append(mentee_row['Full Name'])

        # If matching disciplines found (not empty), proceed with comparing rankings
        if not matching_mentors_df.empty:
            # Iterate through each mentor's ranking for personality, skills, and support traits, and calculate score  
            for mentor_index, mentor_row in matching_mentors_df.iterrows():
                total_difference = 0

                # Calculate the difference for personality traits
                for traits in Personality_traits:
                    mentee_personality_rank = mentee_row[traits]
                    mentor_personality_rank = mentor_row[traits]
                    personality_difference = abs(mentee_personality_rank - mentor_personality_rank)
                    total_difference += personality_difference

                # Calculate the difference for skill traits
                for traits in Skill_traits:
                    mentee_skills_rank = mentee_row[traits]
                    mentor_skills_rank = mentor_row[traits]
                    skills_difference = abs(mentee_skills_rank - mentor_skills_rank)
                    total_difference += skills_difference

                # Calculate the difference for support traits
                for traits in Support_traits:
                    mentee_support_rank = mentee_row[traits]
                    mentor_support_rank = mentor_row[traits]
                    support_difference = abs(mentee_support_rank - mentor_support_rank)
                    total_difference += support_difference

                    # Tie-breaker 
                    total_difference += random.uniform(0, 0.01)
                    total_score += total_difference

                total_mentee_scores[mentee_row['Full Name']] = total_score  # keep track of total scores, in case of unmatched number of people, highest scores are removed in no one's first choice 

                # Organize mentees list with names and scores 
                mentor_scores.append({
                    'Mentor Name': mentor_row['Full Name'],  # Ensure the column name matches your data
                    'Mentor Difference Score': total_difference
                })

        # Sort the list in terms of each of the mentees' preferred mentors  
        sorted_mentors = sorted(mentor_scores, key=lambda x: x['Mentor Difference Score'])
        mentee_preference_order = [mentor['Mentor Name'] for mentor in sorted_mentors]
        mentees_preferences[mentee_row['Full Name']] = mentee_preference_order

    # Mentors perspective pairings 
    for mentor_index, mentor_row in mentors_df.iterrows():
        mentor_discipline = mentor_row['What is your discipline?']

        # Create a new set of mentees that match current mentor's discipline
        matching_mentees_df = mentees_df[mentees_df['What is your discipline?'] == mentor_discipline]

        # Store mentee scores 
        mentee_scores = []
        total_score = 0 

        # If no mentee with the same discipline as mentor
        if matching_mentees_df.empty:
            unmatched_mentors.append(mentor_row['Full Name'])

        # If matching disciplines found (not empty), proceed with comparing rankings
        if not matching_mentees_df.empty:
            # Iterate through each mentee's ranking for personality, skills, and support traits, and calculate score  
            for mentee_index, mentee_row in matching_mentees_df.iterrows():
                total_difference = 0

                # Calculate the difference for personality traits
                for traits in Personality_traits:
                    mentor_personality_rank = mentor_row[traits]
                    mentee_personality_rank = mentee_row[traits]
                    personality_difference = abs(mentor_personality_rank - mentee_personality_rank)
                    total_difference += personality_difference

                # Calculate the difference for skill traits
                for traits in Skill_traits:
                    mentor_skills_rank = mentor_row[traits]
                    mentee_skills_rank = mentee_row[traits]
                    skills_difference = abs(mentor_skills_rank - mentee_skills_rank)
                    total_difference += skills_difference

                # Calculate the difference for support traits
                for traits in Support_traits:
                    mentor_support_rank = mentor_row[traits]
                    mentee_support_rank = mentee_row[traits]
                    support_difference = abs(mentor_support_rank - mentee_support_rank)
                    total_difference += support_difference

                    # Tie-breaker 
                    total_difference += random.uniform(0, 0.01)
                    total_score += total_difference  # total score holds the value of all the pairs' scores added up to see overall compatibility

                total_mentor_scores[mentor_row['Full Name']] = total_score 

                # Organize mentees list with names and scores 
                mentee_scores.append({
                    'Mentee Name': mentee_row['Full Name'],  
                    'Mentee Difference Score': total_difference
                })

        # Sort the list in terms of each of the mentors' preferred mentees 
        sorted_mentee = sorted(mentee_scores, key=lambda x: x['Mentee Difference Score'])
        mentor_preference_order = [mentee['Mentee Name'] for mentee in sorted_mentee]
        mentors_preferences[mentor_row['Full Name']] = mentor_preference_order

    # Handling Case of Unequal Mentors and Mentees
    
    # Run the applicant imbalance checker 
    mentees_df, mentors_df = handle_applicant_imbalance(
        mentees_df, mentors_df, mentees_preferences, mentors_preferences, unmatched_mentees, unmatched_mentors, total_mentee_scores, total_mentor_scores
    )

    # Run the Gale-Shapley algorithm
    mentee_matches, mentor_matches = gale_shapley(mentees_preferences, mentors_preferences, unmatched_mentees)

    return mentee_matches, unmatched_mentees, unmatched_mentors

def handle_applicant_imbalance(mentees_df, mentors_df, mentees_preferences, mentors_preferences, unmatched_mentees, unmatched_mentors, total_mentee_scores, total_mentor_scores):
    # Keep track of all unique disciplines to count
    disciplines = mentees_df['What is your discipline?'].unique()

    for discipline in disciplines:
        # Create an array of all mentee and mentor disciplines
        mentees_in_discipline = mentees_df[mentees_df['What is your discipline?'] == discipline]['Full Name'].tolist()
        mentors_in_discipline = mentors_df[mentors_df['What is your discipline?'] == discipline]['Full Name'].tolist()

        # If more mentees in particular discipline than mentors
        while len(mentees_in_discipline) > len(mentors_in_discipline):
            least_compatible_mentee = unmatch_least_compatible(
                total_mentee_scores, mentors_preferences, mentees_in_discipline, "mentee")

            if least_compatible_mentee is None:
                break

            # Remove from preferences and DataFrame
            mentees_preferences.pop(least_compatible_mentee, None)
            mentees_df = mentees_df[mentees_df['Full Name'] != least_compatible_mentee]
            mentees_in_discipline.remove(least_compatible_mentee)

            unmatched_mentees.append(least_compatible_mentee)

        # If more mentors in particular discipline than mentees
        while len(mentors_in_discipline) > len(mentees_in_discipline):
            least_compatible_mentor = unmatch_least_compatible(
                total_mentor_scores, mentees_preferences, mentors_in_discipline, "mentor")

            if least_compatible_mentor is None:
                break

            # Remove from preferences and DataFrame
            mentors_preferences.pop(least_compatible_mentor, None)
            mentors_df = mentors_df[mentors_df['Full Name'] != least_compatible_mentor]
            mentors_in_discipline.remove(least_compatible_mentor)

            unmatched_mentors.append(least_compatible_mentor)

    return mentees_df, mentors_df  # Return updated DataFrames

def unmatch_least_compatible(total_score, preferences, in_discipline, discipline_type):
    reverse_sorted_scores = sorted(total_score.items(), key=lambda x: x[1], reverse=True)

    for applicant, score in reverse_sorted_scores:  # Obtain highest scoring mentor/mentee
        if applicant in in_discipline:  # Check if the applicant is in the current discipline
            is_first_choice = False 

            for other_applicant, pref in preferences.items():
                if len(pref) > 0 and pref[0] == applicant:  # Check if pref is not empty
                    is_first_choice = True 
                    break

            if not is_first_choice:  # If not first choice in anyone's pref
                return applicant

    return None  # If all are first choices

def gale_shapley(mentees_preferences, mentors_preferences, unmatched_mentees):
    free_mentees = list(mentees_preferences.keys())  # Keys are mentee names
    mentee_matching = {}  # This will store the final matchings for mentees
    mentor_matching = {}  # This will store the final matchings for mentors

    # Initialize each mentor's current mentee to None (free)
    for mentor in mentors_preferences:
        mentor_matching[mentor] = None

    # While there are free mentees
    while free_mentees:
        mentee = free_mentees.pop(0)  # Get the next free mentee
        if mentee in unmatched_mentees:  # Skip unmatched mentees
            continue

        mentee_pref = mentees_preferences[mentee]  # Get their preference list

        for mentor in mentee_pref:
            # If the mentor is free, match them with the mentee
            if mentor_matching[mentor] is None:
                mentee_matching[mentee] = mentor
                mentor_matching[mentor] = mentee
                break  # Mentee is now matched, go to the next mentee

            # If the mentor is already matched, check their preference
            current_mentee = mentor_matching[mentor]
            mentor_pref = mentors_preferences[mentor]

            # Check if the mentor prefers this new mentee over their current match
            if mentor_pref.index(mentee) < mentor_pref.index(current_mentee):
                # Mentor prefers the new mentee, so reject the current mentee
                mentee_matching[mentee] = mentor
                mentor_matching[mentor] = mentee
                free_mentees.append(current_mentee)  # The rejected mentee becomes free again
                break  # Mentee is now matched, go to the next mentee

        # Check if the mentee could not be matched, add to unmatched list
        if mentee not in mentee_matching and mentee not in unmatched_mentees:
            unmatched_mentees.append(mentee)

    return mentee_matching, mentor_matching

if __name__ == '__main__':
    app.run(debug=True)
