#
# Authors: Pranav Marla and Nick Quinn
# Description: Program to solve Google's Hash Code 2022 'Pizza' practice problem: https://codingcompetitions.withgoogle.com/hashcode/round/00000000008f5ca9/00000000008f6f33#problem
#
# Currently, this brute force solution (containing some minor optimizations) is too slow to evaluate the last two test cases ('d' and 'e')

from itertools import combinations
from math import factorial, trunc
from pathlib import Path
from pprint import pprint
import sys


# Constants

# Strategies:
# Check if likes are larger than current combo
# Check dislikes first, since if one dislike is there, than we can return immediately
# For each iteration, check if it's possible to get a new best solution, otherwise return to save processing time

# Functions

def evaluate_combo(combo, clients_preferences, total_num_clients, max_num_clients):

    num_clients = 0
    error_margin = total_num_clients - max_num_clients
    num_failures = 0

    for potential_client in clients_preferences:

        if num_failures >= error_margin:
            #print(f'Num failures ({num_failures}) >= error margin ({error_margin}) -- aborting ...')
            return num_clients

        found_conflict = False

        # Num combo ingredients should be >= num likes
        if len(potential_client['likes']) > len(combo):
            #print('Num combo ingredients should be >= num likes')
            found_conflict = True
            num_failures += 1
            continue

        # No dislikes present
        for dislike in potential_client['dislikes']:
            if dislike in combo:
                found_conflict = True
                num_failures += 1
                #print('No dislikes should be present')
                break

        if found_conflict:
            continue
        
        # All likes present
        for like in potential_client['likes']:
            if like not in combo:
                found_conflict = True
                num_failures += 1
                #print('All likes should be present')
                break

        if not found_conflict:
            #print('No conflicts')
            num_clients += 1

    return num_clients


def process_test_case(total_num_clients, clients_preferences, ingredients, total_num_combos):

    # Evaluate every combo
    max_num_clients = 0
    max_combo = []
    
    total_num_ingredients = len(ingredients)

    # Generate and evaluate every combo
    combo_counter = 0
    for num_choose in range(1, total_num_ingredients+1):
        combos = list(combinations(ingredients, num_choose))
        # Eg. combo = ('pineapple', 'basil', 'cheese', 'peppers')
        for combo in combos:
            #print(f'{combo=}')

            # Counter to help us keep track of how fast we're progressing
            combo_counter += 1
            if (combo_counter % 1000) == 1:
                print(f'Evaluating combo #{combo_counter}/{total_num_combos} ({trunc((combo_counter/total_num_combos)*100)}%)')
            
            num_clients = evaluate_combo(combo, clients_preferences, total_num_clients, max_num_clients)
            #print(f'Num clients for this combo: {num_clients}\n')
            if num_clients > max_num_clients:
                max_num_clients = num_clients
                max_combo = combo
                #print(f'Max num clients increased to {max_num_clients}\n')
                #print(f'New max combo: {max_combo}')
                
                if max_num_clients == total_num_clients:
                    #print(f'Found the optimal combo -- stop looking\n')
                    return max_combo, max_num_clients

    return max_combo, max_num_clients

# Execution

input_file = sys.argv[1]
input_file_path = Path(input_file)

# client_preferences = \
# [
#     {
#         'likes': [],
#         'dislikes': []
#     },
#     {
#         'likes': [],
#         'dislikes': []
#     },
# ]
clients_preferences = []
ingredients = set()

with open(input_file, encoding='utf8') as f:
    line = f.readline()
    total_num_clients = int(line)
    
    for i in range(total_num_clients):
        new_client = {'likes': [], 'dislikes': []}
        new_client['likes'] = f.readline().split()[1:]
        new_client['dislikes'] = f.readline().split()[1:]
        clients_preferences.append(new_client)

        ingredients.update(set(new_client['likes']), new_client['dislikes'])

#pprint(f'{clients_preferences=}')
print(f'{ingredients=}\n')

# Number of combinations (choosing r items out of n items): n!/((n-r)!r!)
total_num_combos = 0
total_num_ingredients = len(ingredients)
for i in range(1, total_num_ingredients + 1):
    total_num_combos += factorial(total_num_ingredients) / (factorial(total_num_ingredients - i) * factorial(i))
print(f'{total_num_combos=}')

max_combo, max_num_clients = process_test_case(total_num_clients, clients_preferences, ingredients, total_num_combos)
max_combo = sorted(max_combo)

# Write more intuitive output for our debugging
print(f'{max_num_clients=}')
print(f'{max_combo=}')

# Write official, unintuitive output format to file
output_elements = []
output_elements.append(str(len(max_combo)))
output_elements.extend(list(max_combo))
output_str = ' '.join(output_elements)
# print(output_str)
output_folder = Path('submissions')
output_folder.mkdir(parents=True, exist_ok=True)
output_file = output_folder/input_file_path.name
with output_file.open('w+') as f:
    f.write(output_str)