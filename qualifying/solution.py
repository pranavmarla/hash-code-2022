#
# Authors: Pranav Marla and Nick Quinn
# Description: Program to solve Google's 2022 HashCode Problem
#
# Strategies
#   - 
# 
#  Synopsis:
#  Timeline: Start 12:45 AM, Ends 4:30 PM
#  Steps:
#   1. Given a project, find contributors that will fill all the roles
#      Data Structures
#      skill[tool_name] = min-heap of people with skill
#      people[name] = person_class
#   2. Sort project based on value (score/duration) Note: If score is tied, pick project smaller duration or earlier due date
#

'''
Psuedo Code
Step 1: 

for skill in project
    pull min person off of tool min heap
    check if person is qualified
        yes? assign to skill in project
        no? pull next person off and add to list of people needed to add back for next project
            (*before adding people back, wait till next project to add back onto min-heap*)

'''

import heapq
from pathlib import Path
import sys

# Global Variables
global all_assigned_workers
all_assigned_workers = []
global day
day = 0

class Person:
    def __init__(self, name, skills):
        self.name = name
        # Eg. {'C++': 3, 'Python': 4}
        self.skills = skills

    def get_skill_level(self, skill_name):
        # Return skill level or assume skill is zero if missing
        return self.skills.get(skill_name, 0)

    # When two people in heap have same skill level (first element of each tuple), heap will move on to second element of each tuple , which is the Person object itself. Thus, heap needs a way to do the "<" operation for two Person objects to decide which is "lesser" -- currently, we just pick the first one.
    def __lt__(self, other):
        return True

class Project:
    def __init__(self, name, duration, score, best_before, num_of_roles, skills):
        self.name = name
        self.duration = duration
        self.score = score
        self.best_before = best_before
        self.num_of_roles = num_of_roles
        # [('C++', required_level), ...]
        self.skills = skills
        self.assigned_workers = []
    
    def calculate_value(self):
        # We define value of a project as its 'score' divided by its duration. However, we want the heap to give us the project with the max value, but Python's implementation is a min heap -- thus, make the value negative to force it to effectively behave like a max heap.
        return -1 * (self.score / self.duration)
    
    # When two projects in heap have same value, deadline, etc., currently we just pick the first poject and tell heap that is the "lesser" one
    def __lt__(self, other):
        return True

# Iterative function to find min person
def find_min_person(available_people, required_skill_level, people_not_in_heap, skill_name):

    if skill_name not in people_not_in_heap:
        people_not_in_heap[skill_name] = []

    while len(available_people) != 0:
        # Pop lowest skilled worker, and check if their skill meets requirements.
        min_person = heapq.heappop(available_people)[1]
        people_not_in_heap[skill_name].append(min_person)

        if (min_person.get_skill_level(skill_name) >= required_skill_level) and not next((p for p, d in all_assigned_workers if p == min_person), False):
            return min_person, people_not_in_heap, available_people
    
    return None, people_not_in_heap, available_people

# Check if mentor is available for this skill
def check_for_mentor(assigned_workers, skill_name, required_skill_level):
    for w in assigned_workers:
        if w.get_skill_level(skill_name) >= required_skill_level:
            return True
    return False

# Reinsert People back into heap
def reinsert_people_back_in_heap(project, skill_heap_tree, people_not_in_heap):
    for skill_name, required_skill_level in project.skills:
        if skill_name in people_not_in_heap:
            for person in people_not_in_heap[skill_name]:
                heapq.heappush(skill_heap_tree[skill_name], (person.get_skill_level(skill_name), person))

    return skill_heap_tree, people_not_in_heap

def assign_to_project(project, skill_heap_tree):

    # Eg. people_not_in_heap = {'C++': [Person1, Person2]}
    people_not_in_heap = {}
    assigned_workers = []
    project_fully_scheduled = True
    global all_assigned_workers
    global day

    for skill_name, required_skill_level in project.skills:
        # Get heap tree for skill
        available_people = skill_heap_tree[skill_name]
        
        # If mentor available, then lower skill level by one
        if check_for_mentor(assigned_workers, skill_name, required_skill_level):
            min_person, people_not_in_heap, available_people = find_min_person(available_people, required_skill_level - 1, people_not_in_heap, skill_name)
        else:
            min_person, people_not_in_heap, available_people = find_min_person(available_people, required_skill_level, people_not_in_heap, skill_name)

        if min_person is None:
            project_fully_scheduled = False
            skill_heap_tree, people_not_in_heap = reinsert_people_back_in_heap(project, skill_heap_tree, people_not_in_heap)
            return [], project_fully_scheduled
        
        assigned_workers.append(min_person)
    
    skill_heap_tree, people_not_in_heap = reinsert_people_back_in_heap(project, skill_heap_tree, people_not_in_heap)
    for w in assigned_workers:
        all_assigned_workers.append((w, project.duration + day))
    
    return assigned_workers, project_fully_scheduled


# Sort Projects Based on value
def sort_projects(projects):
    sorted_projects = []
    for project in projects:
        heapq.heappush(sorted_projects, (project.calculate_value(), project.best_before, project))
    return sorted_projects


def make_skill_heap_tree_dict(people):
    # Eg. {'C++': <heap tree of people, where person with min skill_level is at top>}
    skill_heap_tree_dict = {}
    
    for person in people:
        for skill_name in person.skills:
            heap = skill_heap_tree_dict.get(skill_name, [])
            heapq.heappush(heap, (person.get_skill_level(skill_name), person))
            if skill_name not in skill_heap_tree_dict:
                skill_heap_tree_dict[skill_name] = heap
                
    return skill_heap_tree_dict


def output(input_file, num_of_fully_scheduled_projects, fully_scheduled_projects):
    input_file_path_obj = Path(input_file)
    output_folder = Path('qualifying/outputs')
    output_folder.mkdir(parents=True, exist_ok=True)
    # Eg. outputs\a_an_example.in.txt
    output_file = output_folder/(input_file_path_obj.name)
    with output_file.open('w+') as f:
        f.write(f'{str(num_of_fully_scheduled_projects)}\n')
        for project in fully_scheduled_projects:
            f.write(f'{project.name}\n')
            worker_names = [worker.name for worker in project.assigned_workers]
            worker_names_str = ' '.join(worker_names)
            f.write(f'{worker_names_str}\n')


# Main Driver function
# TODO Increment Skill if mentored
def main(num_people, num_projects, people, projects, skill_heap_tree_dict, input_file):
    global day
    global all_assigned_workers
    # Projects => [(Project Value, Project Duration, Project Class Object)]
    projects = sort_projects(projects)
    fully_scheduled_projects = []
    
    while (len(fully_scheduled_projects) < num_projects) and day < 100:
        not_fully_scheduled_projects = []
        for project in projects:
            project = project[2]
            assigned_workers, project_fully_scheduled = assign_to_project(project, skill_heap_tree_dict)
            project.assigned_workers = assigned_workers
            if project_fully_scheduled:
                fully_scheduled_projects.append(project)
            else:
                not_fully_scheduled_projects.append(project)

        projects = sort_projects(not_fully_scheduled_projects)
        day += 1
        print(f'{day=}')

        for w in all_assigned_workers:
            if w[1] == day:
                all_assigned_workers.remove(w)
                
    output(input_file, len(fully_scheduled_projects), fully_scheduled_projects)

if __name__ == "__main__":
    # Read input data
    input_file = sys.argv[1]
    # input_file = Path('qualifying/input_data/a_an_example.in.txt')
    with open(input_file, encoding='utf8') as f:
        
        num_people, num_projects = [int(int_str) for int_str in f.readline().split()]
        
        people = []
        for i in range(num_people):
            name, num_skills_str = f.readline().split()
            num_skills = int(num_skills_str)
            skills_dict = {}
            for i in range(num_skills):
                skill_name, skill_level_str = f.readline().split()
                skill_level = int(skill_level_str)
                skills_dict[skill_name] = skill_level
            people.append(Person(name, skills_dict))

        projects = []
        for i in range(num_projects):
            name, duration_str, score_str, best_before_str, num_roles_str = f.readline().split()
            duration, score, best_before, num_roles = int(duration_str), int(score_str), int(best_before_str), int(num_roles_str)
            skills_list = []
            for i in range(num_roles):
                skill_name, required_skill_level_str = f.readline().split()
                required_skill_level = int(required_skill_level_str)
                # E.g. [('skill_name', required_level), ...]
                skills_list.append((skill_name, required_skill_level))
                
            projects.append(Project(name, duration, score, best_before, num_roles, skills_list))

        skill_heap_tree_dict = make_skill_heap_tree_dict(people)

        main(num_people, num_projects, people, projects, skill_heap_tree_dict, input_file)
