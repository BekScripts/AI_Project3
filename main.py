from tabulate import tabulate
import random

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

def check_feaibility(items_arr, constraints):
    feasible_num = 0
    feasible_items = []
    constraints = constraints.replace("NOT", "")

    if "OR" in constraints:
        constraints_arr = constraints.split('OR')
        constraints_arr = [item.strip(' ') for item in constraints_arr]
        for item in items_arr:
            if not constraints_arr[0] in item or not constraints_arr[1] in item:
                feasible_items.append(item)
                feasible_num +=1
        
        print(f"Yes, there are {feasible_num} objects")
            
    elif "AND" in constraints:
        constraints_arr = constraints.split("AND")
        constraints_arr = [item.strip(' ') for item in constraints_arr]
        for item in items_arr:
            if not constraints_arr[0] in item and not constraints_arr[1] in item:
                feasible_items.append(item)
                feasible_num +=1
        print(f"Yes, there are {feasible_num} objects")
    return feasible_items
    
def show_the_table(preference_file, feasible_items):
    preference_items = preference_file.split('\n')

    headers = ['encoding', preference_items[0].split(',')[0], preference_items[1].split(',')[0], 'total penalty']
    table_data = []
    penalty1 = preference_items[0].split(',')[0].split('AND')
    penalty2 = preference_items[1].split(',')[0].split('OR')
    for line in feasible_items:
        data = []
        total_pen = 0
        pen1 = 0
        pen2 = 0
        encode = line.split('-')
        data.append(encode[0])
        if not all(word.strip(' ') in line for word in penalty1):
            pen1 = 10
            data.append(pen1)
        else:
            pen1 = 0
            data.append(pen1)
        
        if not any(word.strip(' ') in line for word in penalty2):
            pen2 = 6
            data.append(pen2)
        else:
            pen2 = 0
            data.append(pen2)

        total_pen = pen2 + pen1
        data.append(total_pen)
        table_data.append(data)

    print(tabulate(table_data, headers, tablefmt='grid'))
    table_data = []

def exemplify(feasible_items, qualitative_file):
    while True:
        two_sample_items = random.sample(feasible_items, 2)
        if two_sample_items[0] != two_sample_items[1]:
            break
    
    sample_item1 = two_sample_items[0].split(' - ')[1].split(',')
    sample_item2 = two_sample_items[1].split(' - ')[1].split(',')
    sample_item1 = [i.strip(' ') for i in sample_item1]
    sample_item2 = [i.strip(' ') for i in sample_item2]
    preferred_option = ""
    unpreferred_option = ""
    if sample_item1[2] == 'beef' and sample_item2[2] == 'beef':  
    # Both have beef → Apply Beer > Wine rule  
        if sample_item1[1] == 'wine' and sample_item2[1] == 'wine':  
            # Both have wine → Compare Ice-cream vs Cake  
            if sample_item1[0] == 'ice-cream' and sample_item2[0] == 'cake':  
                preferred_option = two_sample_items[0]  
                unpreferred_option = two_sample_items[1]
            elif sample_item1[0] == 'cake' and sample_item2[0] == 'ice-cream':  
                preferred_option = two_sample_items[1]  
                unpreferred_option = two_sample_items[0]
            else:  
                preferred_option = two_sample_items[0]  # Default to first if tie  
                unpreferred_option = two_sample_items[1]
        elif sample_item1[1] == 'beer' and sample_item2[1] == 'wine':  
            preferred_option = two_sample_items[0]  # Beer > Wine (since beef exists)  
            unpreferred_option = two_sample_items[1]
        elif sample_item1[1] == 'wine' and sample_item2[1] == 'beer':  
            preferred_option = two_sample_items[1]    # Beer > Wine (since beef exists)  
            unpreferred_option = two_sample_items[0]
        else:  
            preferred_option = two_sample_items[0]  # Default if tie  
            unpreferred_option = two_sample_items[1]

    elif sample_item1[2] == 'fish' and sample_item2[2] == 'beef':  
        preferred_option = two_sample_items[0]  # Fish > Beef  
        unpreferred_option = two_sample_items[1]

    elif sample_item1[2] == 'beef' and sample_item2[2] == 'fish':  
        preferred_option = two_sample_items[1]    # Fish > Beef  
        unpreferred_option = two_sample_items[0]

    elif sample_item1[0] == 'ice-cream' and sample_item2[0] == 'cake':  
        preferred_option = two_sample_items[0]  # Ice-cream > Cake  
        unpreferred_option = two_sample_items[1]

    elif sample_item1[0] == 'cake' and sample_item2[0] == 'ice-cream':  
        preferred_option = two_sample_items[1]    # Ice-cream > Cake  
        unpreferred_option = two_sample_items[0]

    elif sample_item1[2] == 'fish' and sample_item2[2] == 'fish':  
        if sample_item1[1] == 'wine' and sample_item2[1] == 'beer':  
            preferred_option = two_sample_items[0]  # Wine > Beer (if fish exists)  
            unpreferred_option = two_sample_items[1]
        elif sample_item1[1] == 'beer' and sample_item2[1] == 'wine':  
            preferred_option = two_sample_items[1]    # Wine > Beer (if fish exists)  
            unpreferred_option = two_sample_items[0]
        else:  
            preferred_option = two_sample_items[0]  # Default if tie  
            unpreferred_option = two_sample_items[1]

    else:  
        preferred_option = two_sample_items[0]  # Default fallback  
        unpreferred_option = two_sample_items[1]
    
    print(f"The randomly selected feasible objects are {two_sample_items[0].split('-')[0]} and {two_sample_items[1].split('-')[0]}, \n and {preferred_option.split('-')[0]} is strictly preferred over {unpreferred_option.split('-')[0]}")


    
def choose_reasoning(attribute_file, constraints, preference_file, qualitative_file):
    
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

        attributes_arr= attribute_file.split('\n')
        dessert_arr = attributes_arr[0].split(':')[1:][0].strip("'").split(',')
        dessert_arr.reverse()
        drink_arr = attributes_arr[1].split(':')[1:][0].strip("'").split(',')
        drink_arr.reverse()
        main_arr = attributes_arr[2].split(":")[1:][0].strip("'").split(',')
        main_arr.reverse()

        counter= 0
        items_arr = []
        for des_i in range(len(dessert_arr)):
            for drk_i in range(len(drink_arr)):
                for main_i in range(len(main_arr)):
                    str = (f"o{counter} - {dessert_arr[des_i]}, {drink_arr[drk_i]}, {main_arr[main_i]}")
                    counter+=1
                    items_arr.append(str)
        counter = 0
            
        if choice == 1:
           for item in items_arr:
               print(item)
            
        if choice == 2:
           feasible_items = check_feaibility(items_arr, constraints)

        if choice == 3:
            show_the_table(preference_file, feasible_items)
        
        if choice == 4:
            exemplify(feasible_items, qualitative_file)
        
        if choice == 5:
            exemplify(feasible_items, qualitative_file)
                        


def main():
    print("Welcome to PrefAgent !")
    while True:
        attribute_filename = input("Enter Attributes File Name: ")
        try:
            with open(f"../data/{attribute_filename}", 'r') as file:
                attribute_file = file.read()
            if file:
                break
        except:
            print("Wrong file name, try again.")
        
    while True:
        try:
            hard_constraint_filename = input("Enter Hard Constraints File Name: ")
            with open (f"../data/{hard_constraint_filename}", 'r') as file:
                hard_file = file.read()
            if file:
                break
        except:
            print("Wrong file name, try again.")   
  
    try:
        qualittivechoicelogic_filename = "../data/qualitativechoicelogic.txt"
        with open(qualittivechoicelogic_filename, 'r') as file:
            qualitative_file = file.read()
    except:
        print("qualitative file is not found, please make sure to have it in the correct path.")


    preference_logic_choice_num, preference_str = preference_logic_menu()

    if preference_logic_choice_num == 1:
        while True:
            try:
                preference_filename = input("Enter Hard Constraints File Name: ")
                with open (f"../data/{preference_filename}", 'r') as file:
                    preference_file = file.read()
                if file:
                    break
            except:
                print("Wrong file name, try again.")           
        
        choose_reasoning(attribute_file, hard_file, preference_file, qualitative_file)


if __name__ == "__main__":
    main()
