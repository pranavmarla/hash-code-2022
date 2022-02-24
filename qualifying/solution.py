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
        # {'C++': required_level}
        self.skills = skills
        self.assigned_workers = []
    
    def calculate_value(self):
        # We define value of a project as its 'score' divided by its duration. However, we want the heap to give us the project with the max value, but Python's implementation is a min heap -- thus, make the value negative to force it to effectively behave like a max heap.
        return -1 * (self.score / self.duration)
    
    # When two projects in heap have same value, deadline, etc., currently we just pick the first poject and tell heap that is the "lesser" one
    def __lt__(self, other):
        return True

def assign_to_project(project, skill_heap_tree):

    people_not_in_heap = {}

    # Eg. people_not_in_heap = {'C++': [Person1, Person2]}

    assigned_workers = []
    project_fully_scheduled = True
    global all_assigned_workers
    global day

    for skill_name in project.skills:
        # Get heap tree for skill
        available_people = skill_heap_tree[skill_name]
        required_skill_level = project.skills[skill_name]
        
        # Recursive function to find min person
        def find_min_person(available_people, required_skill_level, people_not_in_heap, skill_name):
            # Return None if no person exists to satisfy role
            if len(available_people) == 0:
                return None, people_not_in_heap, available_people
            
            # Pop lowest skilled worker, and check if their skill meets requirements. If yes, then return
            # min person, otherwise, make a recursive call to find next min person
            min_person = heapq.heappop(available_people)[1]
            if skill_name not in people_not_in_heap:
                    people_not_in_heap[skill_name] = []
            people_not_in_heap[skill_name].append(min_person)

            if (min_person.get_skill_level(skill_name) >= required_skill_level):
                # TODO: Had to check for tuple instead
                for w in all_assigned_workers:
                    if min_person == w[0]:
                        return find_min_person(available_people, required_skill_level, people_not_in_heap, skill_name)
                return min_person, people_not_in_heap, available_people
            else:
                return find_min_person(available_people, required_skill_level, people_not_in_heap, skill_name)

        # Check if mentor is available for this skill
        def check_for_mentor(assigned_workers, skill_name, required_skill_level):
            for w in assigned_workers:
                if w.get_skill_level(skill_name) >= required_skill_level:
                    return True
            return False

        # If mentor available, then lower skill level by one
        if check_for_mentor(assigned_workers, skill_name, required_skill_level):
            min_person, people_not_in_heap, available_people = find_min_person(available_people, required_skill_level - 1, people_not_in_heap, skill_name)
        else:
            min_person, people_not_in_heap, available_people = find_min_person(available_people, required_skill_level, people_not_in_heap, skill_name)

        if min_person is None:
            # print(f"WARNING: Unable to find worker for project {project.name} and skill {skill_name}!")
            project_fully_scheduled = False

            # Reinsert the people not in heap
            for skill_name in project.skills:
                if skill_name in people_not_in_heap:
                    for person in people_not_in_heap[skill_name]:
                        heapq.heappush(skill_heap_tree[skill_name], (person.get_skill_level(skill_name), person))
            return [], project_fully_scheduled
        
        assigned_workers.append(min_person)
    
    # Reinsert the people not in heap
    for skill_name in project.skills:
        for person in people_not_in_heap[skill_name]:
            heapq.heappush(skill_heap_tree[skill_name], (person.get_skill_level(skill_name), person))

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
    projects = sort_projects(projects)
    num_of_fully_scheduled_projects = 0
    global day
    global all_assigned_workers
    fully_scheduled_projects = []
    
    while (num_of_fully_scheduled_projects < num_projects) and day < 100:
        not_fully_scheduled_projects = []
        for project in projects:
            project = project[2]
            assigned_workers, project_fully_scheduled = assign_to_project(project, skill_heap_tree_dict)
            project.assigned_workers = assigned_workers
            if project_fully_scheduled:
                num_of_fully_scheduled_projects += 1
                fully_scheduled_projects.append(project)
            else:
                not_fully_scheduled_projects.append(project)

        projects = sort_projects(not_fully_scheduled_projects)
        day += 1

        for w in all_assigned_workers:
            if w[1] == day:
                all_assigned_workers.remove(w)
                
    output(input_file, num_of_fully_scheduled_projects, fully_scheduled_projects)

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
            skills_dict = {}
            for i in range(num_roles):
                skill_name, required_skill_level_str = f.readline().split()
                required_skill_level = int(required_skill_level_str)
                skills_dict[skill_name] = required_skill_level
            projects.append(Project(name, duration, score, best_before, num_roles, skills_dict))

        skill_heap_tree_dict = make_skill_heap_tree_dict(people)

        main(num_people, num_projects, people, projects, skill_heap_tree_dict, input_file)
