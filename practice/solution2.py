#
# Authors: Pranav Marla and Nick Quinn
# Description: Program to solve Google's Hash Code 2022 'Pizza' practice problem: https://codingcompetitions.withgoogle.com/hashcode/round/00000000008f5ca9/00000000008f6f33#problem
#
# Strategy: Binary Search Tree
# 
# Synopsis: Solution uses a binary tree to generate permutations of each customer's likes and dislikes, then uses tree leaf nodes to calculate sum for each permutation.
#           Each leaf node represents a permutation with all of the ingredients considered, and contains a total count of the customer's that would be satisfied by this
#           permutation. The leaf node with the highest sum is returned which always contains the optimal solution. This strategy is better than brute force as we only
#           generate the combinations that would be possible for the list of customers and not every possible combination.
#

from math import trunc
from pathlib import Path
import sys

# Class represents the binary tree data structure used for the binary search tree algorithm
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

# Functions

def process_test_case_with_binary_tree(clients_preferences, ingredients):
    max_combo = []
    max_num_clients = 0
    total_clients = len(clients_preferences)
    # Initialize Tree
    root = Node(0)

    for c_num, client in enumerate(clients_preferences):
        current_node = root
        for i in ingredients:
            # If Client has no preference on ingredient
            if i not in client:
                # Assume this version of the client likes the ingredient, and create a duplicate client that dislikes this ingredient
                current_node = current_node.get_next_node(right=True)
                client[i] = 1
                new_client = client.copy()
                new_client[i] = 0
                clients_preferences.append(new_client)
                total_clients += 1
            else:
                # If Client Likes Ingredient
                if client[i] == 1:
                    current_node = current_node.get_next_node(right=True)

                # If Client Dislikes Ingredient
                if client[i] == 0:
                    current_node = current_node.get_next_node(left=True)

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
    
    output_folder = Path(f'outputs\\{strategy}')
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder/(input_file_path.name)
    with output_file.open('w+') as f:
        f.write(output_str)

if __name__ == "__main__":
    # Execution
    input_file = sys.argv[1]
    global input_file_path
    input_file_path = Path(input_file)

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