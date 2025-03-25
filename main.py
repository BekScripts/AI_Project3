from tabulate import tabulate
import random
from pysat.formula import CNF
from pysat.solvers import Solver


def preference_logic_menu():
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
    return choice, preferences[choice-1]

def check_feaibility(items_arr, constraints_dict, constraints):
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

    
def show_the_table(preference_file, feasible_items):
    preference_items = preference_file.split('\n')
    min_penalty = float('inf') # this is used for the exemplificatio. 

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
        if total_penalty < min_penalty:
            min_penalty = total_penalty
            min_encode= item
        data.append(total_penalty)  # Append total penalty at the end
        table_data.append(data)
    
    # print(tabulate(table_data, headers=headers, tablefmt='grid'))
    return table_data, headers, min_encode

def exemplify(feasible_items, qualitative_file):
    pass
    
def choose_reasoning(attribute_file, constraints, preference_file):
    
    reasoning_arr = ['Encoding', 'Feasibility Checking', 'Show the Table', 'Exemplification'
                    ,'Omni-optimization', 'Back to previous menu']
    
    while True:

        print("Choose the reasoning task to perform")
        for i in range(len(reasoning_arr)):
            print(f"{i+1}: {reasoning_arr[i]}")
        
        choice = int(input())
        print(f"\nYour Choice: {choice}\n")
        if choice == 6:
            preference_logic_menu()
        if choice <1 or choice > 6:
            print("Invalid choice, try again.")

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
        for i in range(len(encoding_arr)):
            encode_string= ""
            encoding= encoding_arr[i]
            for k in range(len(encoding)-1):
                encode_string += f"{cnf_dict[encoding[k]]}, "
            encode_string += f"{cnf_dict[encoding[len(encoding)-1]]}"
            encode_string_arr.append(f"o{i} - {encode_string}")

        feasible_items = check_feaibility(encode_string_arr, constraints_dict, constraints)
        data_table, headers, min_encode = show_the_table(preference_file, feasible_items)
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
            print(f"All optimal objects: {min_encode.split(' - ')[0]}")
            # exemplify(feasible_items)
                        


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
  
    preference_logic_choice_num, preference_str = preference_logic_menu()

    if preference_logic_choice_num == 1:
        while True:
            try:
                preference_filename = input("Enter Preferences File Name: ")
                with open (f"../data/{preference_filename}", 'r') as file:
                    preference_file = file.read()
                if file:
                    break
            except:
                print("Wrong file name, try again.")           
        
        choose_reasoning(attribute_file, hard_file, preference_file)


if __name__ == "__main__":
    main()
