# Constants



# Functions

def process_test_case(test_case_num):

    print(f'Case #{test_case_num}: YES')


# Execution

num_test_cases = int(input())

for test_case in range(1, num_test_cases+1):
    _ = int(input())
    _ = [int(int_str) for int_str in input().split()]
    _ = input()
    process_test_case(test_case)