#
# Authors: Pranav Marla and Nick Quinn
# Description: Program to solve Google's Hash Code 2022 'Pizza' practice problem: https://codingcompetitions.withgoogle.com/hashcode/round/00000000008f5ca9/00000000008f6f33#problem
#
# Strategies
#   - Brute Force (from solution1.py)
#   - Binary Search Tree
# 
#  Synopsis: Currently, this brute force solution (containing some minor optimizations) is too slow to evaluate the last two test cases ('d' and 'e')

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

# Represents the binary tree data structure used for the binary search tree algorithm
class Node:
    def __init__(self, data):
        self.left = None
        self.right = None
        self.data = data

    def get_next_node(self, right=False, left=False):
        if right is True:
            if self.right is None:
                self.right = Node(0)
            return self.right
        elif left is True:
            if self.left is None:
                self.left = Node(0)
            return self.left
        else:
            print("Left or Right Node was not specified in function call.")
            raise

def process_test_case_with_binary_tree(clients_preferences, ingredients):
    max_combo = []
    max_num_clients = 0
    total_clients = len(clients_preferences)
    # Initialize Tree
    root = Node(0)

    for c_num, client in enumerate(clients_preferences):
        #print(f'\n client start')
        #print(client)

        current_node = root
        for i in ingredients:
            #print(f"{i=}")
            # If Client has no preference on ingredient
            if i not in client:
                # Assume this version of the client likes the ingredient, and create a duplicate
                # client that dislikes this ingredient
                current_node = current_node.get_next_node(right=True)
                client[i] = 1
                new_client = client.copy()
                new_client[i] = 0
                clients_preferences.append(new_client)
                total_clients += 1
                #print("Ingredient Does Not Exist, Creating New Client:")
                #print(new_client)
            else:
                # If Client Likes Ingredient
                if client[i] == 1:
                    current_node = current_node.get_next_node(right=True)
                    #print("Client Likes Ingredient")

                # If Client Dislikes Ingredient
                if client[i] == 0:
                    current_node = current_node.get_next_node(left=True)
                    #print("Client Disklikes Ingredient")

        # Current node is currently leaf node. Now get value after incrementing for current customer and see if current combo is best
        current_node.data += 1
        if current_node.data > max_num_clients:
            max_num_clients = current_node.data
            max_combo = client

        # Print Progress
        if c_num % 100 == 1:
            print(f'Evaluating clients #{c_num}/{total_clients} ({trunc((c_num/total_clients)*100)}%)')
    
    # Since max_combo is dictionary, we need to convert to list
    combo = []
    for key in max_combo:
        # Only add ingredient if they like it
        if max_combo[key] == 1:
            combo.append(key)
    max_combo = combo
        
    return max_combo, max_num_clients

# Execution
input_file = sys.argv[1]
global input_file_path 
input_file_path = Path(input_file)

# Number of combinations (choosing r items out of n items): n!/((n-r)!r!)
def find_total_num_combos(ingredients):
    total_num_combos = 0
    total_num_ingredients = len(ingredients)
    for i in range(1, total_num_ingredients + 1):
        total_num_combos += factorial(total_num_ingredients) / (factorial(total_num_ingredients - i) * factorial(i))
    print(f'{total_num_combos=}')
    return total_num_combos

# Print final results and write result to file
def print_results(max_combo, max_num_clients, strategy):
    max_combo = sorted(max_combo)
    global input_file_path

    # Write more intuitive output for our debugging
    print(f'{strategy=}')
    print(f'{max_num_clients=}')
    print(f'{sorted(max_combo)=}\n')

    # Write official, unintuitive output format to file
    output_elements = []
    output_elements.append(str(len(max_combo)))
    output_elements.extend(list(max_combo))
    output_str = ' '.join(output_elements)
    # print(output_str)
    output_folder = Path(f'submissions\\{strategy}')
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder/(input_file_path.name)
    with output_file.open('w+') as f:
        f.write(output_str)

# Strategy Flags
brute_force_stratey = True
binary_tree_strategy = True

if brute_force_stratey:
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

    #pprint(f'{clients_preferences=}')
    with open(input_file, encoding='utf8') as f:
        line = f.readline()
        total_num_clients = int(line)
        
        for i in range(total_num_clients):
            new_client = {'likes': [], 'dislikes': []}
            new_client['likes'] = f.readline().split()[1:]
            new_client['dislikes'] = f.readline().split()[1:]
            clients_preferences.append(new_client)

            ingredients.update(set(new_client['likes']), new_client['dislikes'])

    total_num_combos= find_total_num_combos(ingredients)
    max_combo, max_num_clients = process_test_case(total_num_clients, clients_preferences, ingredients, total_num_combos)
    print_results(max_combo, max_num_clients, "brute_force")

if binary_tree_strategy:
    clients_preferences = []
    ingredients = set()

    with open(input_file, encoding='utf8') as f:
        line = f.readline()
        total_num_clients = int(line)
        
        for i in range(total_num_clients):
            new_client = {}

            # Go through each liked and disliked ingredient, and add to customer preference.
            # Like = 1, Dislike = 0
            liked_ingredients = f.readline().split()[1:]
            for like in liked_ingredients:
                new_client[like] = 1
            disliked_ingredients = f.readline().split()[1:]
            for dislike in disliked_ingredients:
                new_client[dislike] = 0
            
            clients_preferences.append(new_client)
            ingredients.update(set(liked_ingredients), disliked_ingredients)

    # Sort Ingredients Lexographically
    ingredients = sorted(ingredients)

    # Find best combination with clients and ingredients
    max_combo, max_num_clients = process_test_case_with_binary_tree(clients_preferences, ingredients)
    print_results(max_combo, max_num_clients, "binary_tree")