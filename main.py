from tabulate import tabulate
import random
from pysat.formula import CNF
from pysat.solvers import Solver
from itertools import product


def preference_logic_menu(attribute_file, hard_file):
    preferences = ['Penalty Logic', 'Qualitative Choice Logic', 'exit']
    while True:
        
        print("Choose the preference logic to use: ")
        for i in range(len(preferences)):
            print(f"{i+1}. {preferences[i]}")
        choice = int(input())
        if choice <1 or choice > 3:
            print("Invalid choice, try again.")
        else:
            break
    print(f"\nYour Choice: {choice}")
    print(f"\nYou picked {preferences[choice-1]}\n")

    if choice == 1:
        while True:
            try:
                preference_filename = input("Enter Preferences File Name: ")
                with open (f"../data/{preference_filename}", 'r') as file:
                    preference_file = file.read()
                if file:
                    break
            except:
                print("Wrong file name, try again.")           
        
        choose_reasoning_option1(attribute_file, hard_file, preference_file)
    
    if choice == 2:
        while True:
            try:
                qualitative_filename = input("Enter Preferences File Name: ")
                with open(f'../data/{qualitative_filename}', 'r') as file:
                    qualitative_file = file.readlines()
                if file:
                    break
            except:
                print("Wrong Qualitative file name, try again.")
        choose_reasoning_option2(attribute_file, hard_file, qualitative_file)



def display_reasoning_menu():
    reasoning_arr = ['Encoding', 'Feasibility Checking', 'Show the Table', 'Exemplification'
                    ,'Omni-optimization', 'Back to previous menu']
    while True:

        print("Choose the reasoning task to perform")
        for i in range(len(reasoning_arr)):
            print(f"{i+1}: {reasoning_arr[i]}")
        
        choice = int(input())
        print(f"\nYour Choice: {choice}\n")
        if choice <1 or choice > 6:
            print("Invalid choice, try again.")
        else:
            return choice

    

def check_feaibility(items_arr, constraints):
    feasible_items = items_arr 

    for constraint in constraints:
        arr = constraint.split("OR")
        
        if "NOT" in arr[0] and "NOT" in arr[1]:
            constraint1 = arr[0][4:].strip()
            constraint2 = arr[1][4:].strip()

            feasible_items = [line for line in feasible_items
                               if (constraint1 in line and constraint2 not in line) or
                               (constraint2 in line and constraint1 not in line) or
                               (constraint1 not in line and constraint2 not in line)]
        
        elif "NOT" in arr[0] and "NOT" not in arr[1]:
            constraint1 = arr[0][4:].strip()
            constraint2 = arr[1].strip()

            # Filter out the infeasible items based on the current constraint
            feasible_items = [line for line in feasible_items
                               if (constraint1 in line and constraint2 in line)]
    
    return feasible_items

    
def show_the_table_option1(preference_file, feasible_items):
    
    preference_items = preference_file.split('\n')
    omni_optimization = float("inf")

    headers = ['encoding']
    for preference in preference_items:
            headers.append(preference[:preference.find(',')])
    headers.append("total_penalty")

    table_data = []
    for item in feasible_items:
        total_penalty = 0
        data = [item.split(' - ')[0]]  
    
        for preference in preference_items:
            parts = preference.split()
            if len(parts) < 4:
                continue  

            condition1, operator, condition2, penalty = parts
            penalty = int(penalty)

            if operator == "AND":
                if condition1 in item and condition2 in item:
                    data.append(0)
                else:
                    data.append(penalty)
                    total_penalty += penalty

            elif operator == "OR":
                if condition1 in item or condition2 in item:
                    data.append(0)
                else:
                    data.append(penalty)
                    total_penalty += penalty
        if total_penalty <= omni_optimization:
            omni_optimization = total_penalty
        data.append(total_penalty)  # Append total penalty at the end
        table_data.append(data)
    
    # print(tabulate(table_data, headers=headers, tablefmt='grid'))
    return table_data, headers, omni_optimization


def show_the_table_option2(choice_logic_rules, feasible_items):
   
    # headers = ['encoding'] + [rule.split(" BT ")[0] for rule in choice_logic_rules]  
    headers = ['encoding']
    for rule in choice_logic_rules:
        curr_rule = rule.split()
        if len(curr_rule) == 5:
            item1 = curr_rule[0]
            item2 = curr_rule[2]
            condition = curr_rule[4]

            headers.append(f'{item1} > {item2} <- {condition}')
        else:
            item1 = curr_rule[0]
            item2 = curr_rule[2]
            headers.append(f'{item1} > {item2} <-')


    table_data = []

    for item in feasible_items:
        encoding, attributes_str = item.split(' - ')  
        attributes = list(map(str.strip, attributes_str.split(',')))  
        data = [encoding]  

        for i in range(1, len(headers), 1):
            curr_header = list(map(str.strip, headers[i].split()))
            preferred = curr_header[0]
            unpreferred = curr_header[2]
            condition = curr_header[4] if len(curr_header)==5 else ""


            if condition and condition not in attributes:
                data.append(float("inf"))  

            elif condition and condition in attributes:
                if preferred in attributes:
                    data.append(1)  
                else:
                    data.append(2)  

            elif not condition:
                if preferred in attributes:
                    data.append(1)  
                elif unpreferred in attributes:
                    data.append(2)  
                else:
                    data.append(2)
            
        table_data.append(data)
    
    return table_data, headers


def create_attributes_table (attribute_file, constraints) -> list:
     # encode the attributes file with PySat with their respective CNFs
    attribute_file_items =[]
    for i in range(len(attribute_file)):
        attribute_file_items.append(attribute_file[i].split(':')[1].split(','))

    cnf = []
    cnf_dict= {}
    constraints_dict = {}
    constraints_arr = []

    for i in range(len(attribute_file)):
        cnf.append([i+1, -1*(i+1)])
        item1 = attribute_file_items[i][0].strip(" ").strip("\n")
        item2 = attribute_file_items[i][1].strip(" ").strip("\n")
        cnf_dict[i+1] = item1
        cnf_dict[-1*(i+1)] = item2

        for constraint in  constraints:
            constraints_arr = constraint.split(" ")
            if item1 in constraints_arr:
                constraints_dict[item1] = i+1
            elif item2 in constraints_arr:
                constraints_dict[item2] = -1*(i+1)

    
    encoding_arr = []
    with Solver(bootstrap_with=cnf) as solver:
        for m in solver.enum_models():
            encoding_arr.append(m)
    encode_string_arr = []
    combinations = list(product([0, 1], repeat=len(encoding_arr[0])))
    encoding_arr = [[(i + 1) if bit == 1 else -1 * (i + 1) for i, bit in enumerate(comb)] for comb in combinations]
    for i in range(len(encoding_arr)):
        encode_string= ""
        encoding= encoding_arr[i]
        for k in range(len(encoding)-1):
            encode_string += f"{cnf_dict[encoding[k]]}, "
        encode_string += f"{cnf_dict[encoding[len(encoding)-1]]}"
        encode_string_arr.append(f"o{i} - {encode_string}")
    
    return encode_string_arr

    
def choose_reasoning_option1(attribute_file, constraints, preference_file):
    choice = display_reasoning_menu()
    while choice >0 and choice < 6:
        encode_string_arr  = create_attributes_table(attribute_file, constraints)
        feasible_items = check_feaibility(encode_string_arr, constraints)
        data_table, headers, omni_optimization = show_the_table_option1(preference_file, feasible_items)
        if choice == 1:
            for item in encode_string_arr:
                print(item)
        
        if choice == 2:
            print(f"Yes, there are {len(feasible_items)} feasible items.")

        if choice == 3:
            print(tabulate(data_table, headers, tablefmt='grid'))
        
        if choice == 4:
            two_rand_samples = random.sample(data_table, 2)
            sample1 = two_rand_samples[0]
            sample2 = two_rand_samples[1]
            preferred = sample1[0] if int(sample1[3]) < int(sample2[3]) else sample2[0]
            unpreferred = sample1[0] if int(sample1[3]) > int(sample2[3]) else sample2[0]

            print(f"Two randomly selected feasible objects are {sample1[0]} and {sample2[0]},\n and {preferred} is strictly preferred over {unpreferred}")

        
        if choice == 5:
            a = [i[0] for i in data_table if int(i[3])== omni_optimization]
            print(f"All optimal objects: {a}")
            # exemplify(feasible_items)
        
        choice = display_reasoning_menu()
    if choice == 6:
        preference_logic_menu(attribute_file, constraints)


def choose_reasoning_option2(attribute_file, constraints, qualitative_file):
    choice = display_reasoning_menu()
    while choice >0 and choice < 6:
        encode_string_arr  = create_attributes_table(attribute_file, constraints)
        feasible_items = check_feaibility(encode_string_arr, constraints)
        data_table, headers = show_the_table_option2(qualitative_file, feasible_items)
        if choice == 1:
            for item in encode_string_arr:
                print(item)
        
        if choice == 2:
            print(f"Yes, there are {len(feasible_items)} feasible items.")
        
        if choice == 3:
            print(tabulate(data_table, headers=headers, tablefmt="grid"))
        
        if choice == 4:
            two_random_objects = random.sample(data_table, 2)
            a =  False
            b = False
            a1 = two_random_objects[0]
            a2 = two_random_objects[1]
            cnt = 0
            for i in range(1, len(two_random_objects[0]), 1):
                if a1[i] <= a2[i]:
                    cnt +=1
            if cnt == len(a1)-1:
                a = True


            for i in range(1, len(two_random_objects[0]), 1):
                if a2[i] <= a1[i]:
                    cnt +=1
            if cnt == len(a1)-1:
                b = True

            if a and not b:
                prefeffered = a1
                unpreferred = a2
                print(f"Two randomly selected feasible objects are {a1[0]} and {a2[0]}, and {prefeffered[0]} is strictly preferred over {unpreferred[0]}.")
            if b and not a:
                prefeffered = a2
                unpreferred = a1
                print(f"Two randomly selected feasible objects are {a1[0]} and {a2[0]}, and {unpreferred[0]} is strictly preferred over {prefeffered[0]}.")

            else:
                print(f"Two randomly selected feasible objects are {a1[0]} and {a2[0]}, and {a1[0]} and {a2[0]} are incomparable.")
        
        if choice == 5:
            
            optimal_objects = []

            for curr_item in data_table:
                is_optimal = True  

                for other_item in data_table:
                    if curr_item == other_item:
                        continue  
                    
                    strictly_better = False
                    strictly_worse = False
                    
                    for j in range(1, len(curr_item)):  
                        if isinstance(curr_item[j], (int, float)) and isinstance(other_item[j], (int, float)):  
                            if curr_item[j] > other_item[j]:  
                                strictly_worse = True  
                            elif curr_item[j] < other_item[j]:  
                                strictly_better = True 

                    if strictly_worse and not strictly_better:
                        is_optimal = False  
                        break  

                if is_optimal:
                    optimal_objects.append(curr_item[0])

            print("All optimal objects:", ", ".join(optimal_objects))
                    
        choice = display_reasoning_menu()

    if choice == 6:
        preference_logic_menu(attribute_file, constraints)


def main():
    print("Welcome to PrefAgent !")
    cnf = []
    while True:
        attribute_filename = input("Enter Attributes File Name: ")
        try:
            with open(f"../data/{attribute_filename}", 'r') as file:
                attribute_file = file.readlines()
            if file:
                break
            for i in range(len(attribute_file)):
                cnf.append([i+1, -1*(i+1)])
        except:
            print("Wrong file name, try again.")
        
    while True:
        try:
            hard_constraint_filename = input("Enter Hard Constraints File Name: ")
            with open (f"../data/{hard_constraint_filename}", 'r') as file:
                hard_file = file.readlines()
            if file:
                break
        except:
            print("Wrong file name, try again.")   
  
    preference_logic_menu(attribute_file, hard_file)


if __name__ == "__main__":
    main()
