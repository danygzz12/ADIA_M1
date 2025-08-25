def compare_returns(expected_output, real_output):
    if real_output is None: 
        return False
    
    # Handle complex numbers separately
    if isinstance(expected_output, complex) or isinstance(real_output, complex):
        return abs(expected_output - real_output) <= 1e-6
    if isinstance(expected_output, float) or isinstance(real_output, float):
        ### compare numbers with a tolerance level
        from math import isclose
        return isclose(expected_output, real_output, rel_tol=1e-6, abs_tol=1e-6)
    if isinstance(expected_output, int) or isinstance(real_output, int):
        return expected_output == real_output
    if isinstance(expected_output, str):
        return expected_output == real_output
    if isinstance(expected_output, dict):
        ### compare the keys: 
        for key in expected_output:
            if key not in real_output:
                return False
        for key in real_output:
            if key not in expected_output:
                return False 
        for key in expected_output:
            if expected_output[key] != real_output[key]:
                return False
        return True
    if isinstance(expected_output, tuple): 
        return expected_output == real_output
    if isinstance(expected_output, list):
        return expected_output == real_output
    return expected_output == real_output



def failed_case_message(expected_output, real_output, func_name, arg, arg_name=True):
    if arg_name:
        arg_text = [str(key)+"="+str(value) for key, value in arg.items()]
    else:
        arg_text = [str(value) for value in arg.values()]
    arg_text = ", ".join(arg_text)
    return f"\nCalling {func_name}({arg_text}) returned: \n{real_output} \nExpected: \n{expected_output} \n"

def count_comparisons(func):
    import ast
    import inspect
    tree = ast.parse(inspect.getsource(func))
    boolean_count = sum([1 for node in ast.walk(tree) if isinstance(node, ast.Compare)])
    return boolean_count

# def check_comparisons(func_name, ):
#     func = global_vars[func_name]
#     max_comparisons = 2
#     comparisons = count_comparisons(func)
#     assert comparisons <= max_comparisons, "Tu función usa más de 2 comparaciones."

def grade_code_and_func(func):
    import pickle 
    import pickle 
    try: 
        with open("ADIA_M1/tests_" + func.__name__, "rb") as file:
            tests = pickle.load(file)
    except FileNotFoundError:
        return "The function name is not valid. Grading failed. "
    input_args = tests[1]
    max_score = tests[2]
    max_comparisons = tests[3]

    ### check if the function uses too many comparisons: 
    if count_comparisons(func) > max_comparisons: 
        return f"Score: 0 \nYour function has too many comparison statements. If you actually use a dictionary, \n your function should have no more than {max_comparisons} comparison statements"

    try: 
        with open("ADIA_M1/" + func.__name__, "rb") as file:
            expected_results = pickle.load(file)
    except FileNotFoundError:
        return "Function name not valid. Grading failed. "
    
    passed_tests = 0
    total_tests = 0
    failed_messages = ""

    for arg, expected_output in zip(input_args, expected_results): 
        total_tests += 1
        real_output = func(**arg)

        passed = compare_returns(expected_output, real_output)

        if passed:
            passed_tests +=1 
            continue 

        failed_messages += failed_case_message(expected_output, real_output, func.__name__, arg)

    score = passed_tests/total_tests*max_score
    feedback = f"Passed {passed_tests}/{total_tests}.\nScore: {score}"+failed_messages
    return feedback


def grade_code(func):
    import pickle 
    try: 
        with open("ADIA_M1/tests_" + func.__name__, "rb") as file:
            tests = pickle.load(file)
    except FileNotFoundError:
        return "The function name is not valid. Grading failed. "
    input_args = tests[1]
    max_score = tests[2]

    try: 
        with open("ADIA_M1/" + func.__name__, "rb") as file:
            expected_results = pickle.load(file)
    except FileNotFoundError:
        return "Function name not valid. Grading failed. "
    
    passed_tests = 0
    total_tests = 0
    failed_messages = ""

    for arg, expected_output in zip(input_args, expected_results): 
        total_tests += 1
        real_output = func(**arg)

        passed = compare_returns(expected_output, real_output)

        if passed:
            passed_tests +=1 
            continue 

        failed_messages += failed_case_message(expected_output, real_output, func.__name__, arg)

    score = passed_tests/total_tests*max_score
    feedback = f"Passed {passed_tests}/{total_tests}.\nScore: {score}"+failed_messages
    return feedback
# def grade_code(func, max_score=5):
#     import pickle 

#     with open("ADIA_M1/tests_" + func.__name__, "rb") as f:
#         test_cases = pickle.load(f)

#     passed_tests = 0
#     total_tests = 0
#     failed_messages = ""

#     for case in test_cases: 
#         total_tests += 1
#         real_output = func(**case[0])
#         expected_output = case[1]

#         passed = compare_returns(expected_output, real_output)

#         if passed:
#             passed_tests +=1 
#             continue 

#         failed_messages += failed_case_message(expected_output, real_output, func.__name__, case[0])

#     score = passed_tests/total_tests*max_score
#     feedback = f"Passed {passed_tests}/{total_tests}.\nScore: {score}"+failed_messages
#     return feedback







### For interactive functions: 
from contextlib import redirect_stdout
from io import StringIO
import builtins
import sys

class PatchedInput:
    def __init__(self, input_values):
        self.input_values = input_values
        self.input_copy = input_values.copy()
        self.original_input = builtins.input
        self.original_output = sys.stdout
        self.captured_lines = []
        self.captured_io = StringIO()
        self.input_lines = []
        self.output_lines = []
        self.failed_to_end = False
        self.ended_soon = False
        
    def __enter__(self):
        builtins.input = self.custom_input
        sys.stdout = self.captured_io
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.input_values:
            print("FUNCTION SHOULD HAVE CONTINUED, BUT INSTEAD ENDED.")
            self.ended_soon = True
        builtins.input = self.original_input
        sys.stdout = self.original_output
        self.clean_up()
    
    def custom_input(self, prompt):
        self.input_lines.append(prompt)
        self.captured_lines.append(prompt)
        print(prompt, end='\n')
        if self.input_values:
            return self.input_values.pop(0)
        else:
            print("THE FUNCTION SHOULD HAVE ENDED HERE, BUT INSTEAD CONTINUED.")
            self.failed_to_end = True
            self.__exit__
    
    def clean_up(self):
        self.captured_lines = self.captured_io.getvalue().splitlines()
        if self.failed_to_end:
            self.captured_lines = self.captured_lines[0:self.captured_lines.index("THE FUNCTION SHOULD HAVE ENDED HERE, BUT INSTEAD CONTINUED.")+1]
        i = 0
        for input_line in self.input_lines:
            try:
                self.captured_lines[self.captured_lines.index(input_line)] = input_line + self.input_copy[i]
            except:
                pass
            i += 1

def simulate_interaction(input_values, function, args={}):
    """Function that automatically interacts with an interactive function in Python given a pre-selected
        list of input values. It returns a PatchedInput instance (pi) with pi.captured_lines showing the
        full interaction, pi.failed_to_end =True in case the function did not end with the provided arguments
        and pi.ended_soon=True in case the function ended without using all provided input arguments. 
    
        Parameters:
            input_values (list[str]): The list of pre-selected input values to test the function. 
            function (func): The interactive function which takes the input values. 
            args (dict{str:any}, Optional, default:None): arguments required by the function. 
        
        """
    patched_input = PatchedInput(input_values)
    with patched_input:
        try:
            function(**args)
        except:
            return patched_input
            pass
    return patched_input

# def grade_interactive_function(func):
#     ### Get the inputs
#     import pickle 
#     with open("ADIA_M1/tests_" + func.__name__, "rb") as file:
#         input_func = pickle.load(file)
#     test_inputs, args, max_score = input_func()

#     ### Get the solution function
#     with open("ADIA_M1/" + func.__name__, "rb") as file:
#         sol_func = pickle.load(file)

#     failed_messages = ""

#     passed_tests = 0
#     total_tests = 0

#     for input_values, arg in zip(test_inputs, args):
#         total_tests += 1
#         ### Run the simulation to obtain expected values. 
#         exp_pi = simulate_interaction(input_values.copy(), sol_func, arg)
#         real_pi = simulate_interaction(input_values.copy(), func, arg)

#         exp_interaction = "\n".join(exp_pi.captured_lines)
#         real_interaction = "\n".join(real_pi.captured_lines)

#         if exp_interaction != real_interaction:
#             failed_messages += failed_case_message(exp_interaction, real_interaction, func.__name__, arg)
#         else:
#             passed_tests += 1

#     score = passed_tests/total_tests*max_score 
#     feedback = f"Passed {passed_tests}/{total_tests}.\nScore: {score}"+failed_messages
#     return feedback

# def grade_interactive_function_old(func):
#     ### Get the inputs
#     import pickle 
#     with open("ADIA_M1/tests_" + func.__name__, "rb") as file:
#         input_code = pickle.load(file)

#     # Create a temporary namespace (dictionary) to hold executed code
#     temp_namespace = {}

#     # Execute the code in this namespace
#     exec(input_code, temp_namespace)
    
#     # Extract the function object (whatever its original name was)
#     # Find the first callable in the namespace that isn't built-in
#     loaded_func = next(
#         obj for obj in temp_namespace.values()
#         if callable(obj) and obj.__name__ != "<lambda>"
#     )
    
#     # Assign to your fixed variable name
#     input_func = loaded_func
    
#     test_inputs, args, max_score = input_func()

#     ### Get the solution function
#     with open("ADIA_M1/" + func.__name__, "rb") as file:
#         sol_code = pickle.load(file)

#     # Create a temporary namespace (dictionary) to hold executed code
#     temp_namespace = {}

#     # Execute the code in this namespace
#     exec(sol_code, temp_namespace)
    
#     # Extract the function object (whatever its original name was)
#     # Find the first callable in the namespace that isn't built-in
#     loaded_func = next(
#         obj for obj in temp_namespace.values()
#         if callable(obj) and obj.__name__ != "<lambda>"
#     )
    
#     # Assign to your fixed variable name
#     sol_func = loaded_func

#     failed_messages = ""

#     passed_tests = 0
#     total_tests = 0

#     for input_values, arg in zip(test_inputs, args):
#         total_tests += 1
#         ### Run the simulation to obtain expected values. 
#         exp_pi = simulate_interaction(input_values.copy(), sol_func, arg)
#         real_pi = simulate_interaction(input_values.copy(), func, arg)

#         exp_interaction = "\n".join(exp_pi.captured_lines)
#         real_interaction = "\n".join(real_pi.captured_lines)

#         if exp_interaction != real_interaction:
#             failed_messages += failed_case_message(exp_interaction, real_interaction, func.__name__, arg)
#         else:
#             passed_tests += 1

#     score = passed_tests/total_tests*max_score 
#     feedback = f"Passed {passed_tests}/{total_tests}.\nScore: {score}"+failed_messages
#     return feedback
def grade_interactive_function_and_code(func):
    import pickle 
    try:
        with open("ADIA_M1/tests_" + func.__name__, "rb") as file:
            test_inputs, args, max_score, max_comparisons = pickle.load(file)
    except FileNotFoundError:
        return "The function name is not valid. Grading failed. "

    ### check that the function doesn't have too many comparisons: 
    if count_comparisons(func) > max_comparisons: 
        return f"Score: 0 \nYour function has too many comparison statements. If you actually use a dictionary, \n your function should have no more than {max_comparisons} comparison statements"

    try: 
        with open("ADIA_M1/" + func.__name__, "rb") as file:
            exp_interactions = pickle.load(file)
    except FileNotFoundError:
        return "The function name is not valid. Grading failed. "
    
    failed_messages = ""

    passed_tests = 0
    total_tests = 0

    for input_values, arg, exp_interaction in zip(test_inputs, args, exp_interactions):
        total_tests += 1
        ### Run the simulation to obtain expected values. 
        real_pi = simulate_interaction(input_values.copy(), func, arg)
        real_interaction = "\n".join(real_pi.captured_lines)

        if exp_interaction != real_interaction:
            failed_messages += failed_case_message(exp_interaction, real_interaction, func.__name__, arg)
        else:
            passed_tests += 1

    score = passed_tests/total_tests*max_score 
    feedback = f"Passed {passed_tests}/{total_tests}.\nScore: {score}"+failed_messages
    return feedback
    

def grade_interactive_function(func):
    import pickle 
    try:
        with open("ADIA_M1/tests_" + func.__name__, "rb") as file:
            test_inputs, args, max_score = pickle.load(file)
    except FileNotFoundError:
        return "The function name is not valid. Grading failed. "

    try: 
        with open("ADIA_M1/" + func.__name__, "rb") as file:
            exp_interactions = pickle.load(file)
    except FileNotFoundError:
        return "The function name is not valid. Grading failed. "
    
    failed_messages = ""

    passed_tests = 0
    total_tests = 0

    for input_values, arg, exp_interaction in zip(test_inputs, args, exp_interactions):
        total_tests += 1
        ### Run the simulation to obtain expected values. 
        real_pi = simulate_interaction(input_values.copy(), func, arg)
        real_interaction = "\n".join(real_pi.captured_lines)

        if exp_interaction != real_interaction:
            failed_messages += failed_case_message(exp_interaction, real_interaction, func.__name__, arg)
        else:
            passed_tests += 1

    score = passed_tests/total_tests*max_score 
    feedback = f"Passed {passed_tests}/{total_tests}.\nScore: {score}"+failed_messages
    return feedback


def grade_interactive_function_with_randomization(func):
    import pickle 
    import random
    try:
        with open("ADIA_M1/tests_" + func.__name__, "rb") as file:
            test_inputs, args, max_score, seeds = pickle.load(file)
    except FileNotFoundError:
        return "The function name is not valid. Grading failed. "

    try: 
        with open("ADIA_M1/" + func.__name__, "rb") as file:
            exp_interactions = pickle.load(file)
    except FileNotFoundError:
        return "The function name is not valid. Grading failed. "
    
    failed_messages = ""

    passed_tests = 0
    total_tests = 0

    for input_values, arg, exp_interaction, seed in zip(test_inputs, args, exp_interactions, seeds):
        total_tests += 1
        ### Run the simulation to obtain expected values. 
        random.seed(seed)
        real_pi = simulate_interaction(input_values.copy(), func, arg)
        real_interaction = "\n".join(real_pi.captured_lines)

        if exp_interaction != real_interaction:
            failed_messages += failed_case_message(exp_interaction, real_interaction, func.__name__, arg)
        else:
            passed_tests += 1

    score = passed_tests/total_tests*max_score 
    feedback = f"Passed {passed_tests}/{total_tests}.\nScore: {score}"+failed_messages
    return feedback


def test_attributes(test_class, input_args, expected_args):
    feedback = ""
    passed = True
    for args, expected in zip(input_args, expected_args):
        arg_text = [str(key)+"="+str(value) for key, value in args.items()]
        arg_text = ", ".join(arg_text)
        ### check that the object can be initialized with the given arguments
        try: 
            instance = test_class(**args)
        except TypeError:
            passed = False
            feedback += f"\nCalling {test_class.__name__}({arg_text}) could not be initialized. Did you correctly set all attribute names?"
            continue

        ### Check this specific case of argument initialization
        passed_case = True
        case_feedback = f"\nCalling {test_class.__name__}({arg_text}) returned an error in its attributes:"

        ### check that they contain all attributes after initialization: 
        for arg in expected:
            try: 
                getattr(instance, arg)
            except AttributeError: 
                case_feedback += f"\nThe instance does not contain the attribute '{arg}'."
                passed_case = False
        
        if not passed_case: 
            feedback += case_feedback 
            continue
        
        ### Check that attributes contain the expected values after initialization
        for arg, value in expected.items():
            if getattr(instance, arg) != value: 
                case_feedback += f"\nThe attribute '{arg}' is set to {getattr(instance, arg)} instead of {value}"
                passed_case = False 
                passed = False
        if not passed_case:
            feedback += case_feedback + "\n"

    return feedback, passed



def test_methods(test_class, input_args, expected_results):
    feedback = ""
    passed = True
    for args, results in zip(input_args, expected_results):
        arg_text = [str(key)+"="+str(value) for key, value in args.items()]
        arg_text = ", ".join(arg_text)
        instance = test_class(**args)
        passed_case = True
        case_feedback = f"\n\nCalling {test_class.__name__}({arg_text}) returned an error in its methods:"

        for method, exp_value in results.items():
            real_method = getattr(instance, method)
            real_result = real_method()
            if real_result != exp_value:
                passed_case = False 
                passed = False
                case_feedback += f"\n{instance.__class__.__name__}.{method}() returned {real_result} instead of {exp_value}"
        
        if not passed_case: 
            feedback += case_feedback
    return feedback[2:], passed


def test_class(test_class):
    ### Get input_values 
    try: 
        import pickle
        with open("ADIA_M1/tests_"+test_class.__name__, "rb") as file: 
            input_args, expected_args, expected_results = pickle.load(file)
    except:
        return "Invalid function name. Make sure your auto-grader is updated.", False

    ### test that the class can be initialized and contains all the right attribute values after initialization
    fb, passed = test_attributes(test_class, input_args, expected_args)

    if not passed: 
        return fb, False
    
    ### test that the methods in the class work correctly: 
    feedback, passed = test_methods(test_class, input_args, expected_results)

    if not passed:
        return feedback, False
    
    return "Congrats! Everything works perfectly.", True

import random 

class MontyHallGame:
    def __init__(self):
        ### choose a door to have a car, and the rest have goats. 
        self.goat_doors = random.sample([1, 2, 3], k=2)
        self.car_door = [x for x in [1, 2, 3] if x not in self.goat_doors][0]
        self.player_selection = None
        self.revealed_goat_door = None

    def set_player_choice(self, choice):
        if choice in [1, 2, 3]:
            if choice == self.revealed_goat_door: 
                print("You shouldn't select the door that's been opened and contains a goat! Try again")
                return
            self.player_selection = choice
        else:
            print("Invalid selection. You must choose 1, 2 or 3.")

    def reveal_goat(self):
        if not self.player_selection: 
            raise AssertionError("The player selection has not been made yet. Cannot reveal a goat. ")
        elif self.revealed_goat_door is not None:
            return self.revealed_goat_door
        else:
            ### Ensure you reveal a door with a goat if the player did NOT choose it. 
            revealed_goats = [door for door in self.goat_doors if door != self.player_selection]
            goat_door = random.choice(revealed_goats)
            self.revealed_goat_door = goat_door
            return goat_door
        
    def check_winner(self):
        if self.player_selection == self.car_door:
            return True 
        else:
            return False

def test_inintialization(test_class):
    ### Check that the object can be initialized: 
    try: 
        instance = test_class()
    except:
        return f"{test_class.__name__}() cannot be initialized. Check your class definition. ", False
    
    ### Check that it contains the right attributes: 
    try: 
        instance.chosen_door 
    except: 
        return f"{test_class.__name__} does not contain the attribute 'chosen_door'.", False
    
    ### Check that chosen_door is set correctly: 
    num_tests = 50 
    import random
    seeds = [random.random() for i in range(num_tests)]
    for s in seeds: 
        random.seed(s)
        selection = random.choice([1, 2, 3])
        random.seed(s)
        instance = test_class()
        if instance.chosen_door != selection: 
            return f"Error. The chosen_door attribute should be set with random.choice([1, 2, 3]).", False 
    return "", True




def test_switch_behavior(test_class): 
    feedback, passed = test_inintialization(test_class)

    if not passed: 
        return feedback, False
    
    num_tests = 100 
    worked = 0 

    for s in range(num_tests):
        test_player = test_class()
        initial_selection = test_player.chosen_door 
        Game = MontyHallGame()
        test_player.play(Game)
        if Game.player_selection != initial_selection:
            if Game.player_selection is not None:
                worked += 1

    if worked != num_tests:
        return f"Your switching strategy is not implemented correctly. Switched {worked}/{num_tests} times.", False
    else: 
        return "Congrats! Your swtich strategy works as expected.", True
    
def test_keep_behavior(test_class):
    feedback, passed = test_inintialization(test_class)

    if not passed: 
        return feedback, False
    
    num_tests = 100 
    worked = 0 

    for s in range(num_tests):
        test_player = test_class()
        initial_selection = test_player.chosen_door 
        Game = MontyHallGame()
        test_player.play(Game)
        if Game.player_selection == initial_selection:
            if Game.player_selection is not None:
                worked += 1

    if worked != num_tests:
        return f"Your keeping strategy is not implemented correctly. Switched {worked}/{num_tests} times.", False
    else: 
        return "Congrats! Your keep strategy works as expected.", True
    
def test_inintialization_2(test_class):
    ### Check that the object can be initialized: 
    try: 
        instance = test_class(p_switch=0.5)
    except:
        return f"{test_class.__name__}() cannot be initialized. Check your class definition. ", False
    
    ### Check that it contains the right attributes: 
    try: 
        instance.chosen_door 
    except: 
        return f"{test_class.__name__} does not contain the attribute 'chosen_door'.", False
    
    try: 
        instance.p_switch
    except:
        return f"{test_class.__name__} does not contain the attribute 'p_switch'", False
    
    ### Check that attribute p_switch is set correctly: 
    p_values = [i*0.01 for i in range(10, 10, 10)]
    for p in p_values: 
        instance = test_class(p_switch=p)
        if instance.p_switch != p:
            return f"{test_class.__name__}(p_switch={p}) is not properly initialized to have an attribute of p_switch set to {p}.", False
        
    
    ### Check that chosen_door is set correctly: 
    num_tests = 50 
    import random
    seeds = [random.random() for i in range(num_tests)]
    for s in seeds: 
        random.seed(s)
        selection = random.choice([1, 2, 3])
        random.seed(s)
        instance = test_class(p_switch=0.5)
        if instance.chosen_door != selection: 
            return f"Error. The chosen_door attribute should be set with random.choice([1, 2, 3]).", False 
    return "", True

def test_rswitch_behavior(test_class, num_tests=100):
    feedback, passed = test_inintialization_2(test_class)

    if not passed:
        return feedback, False
    
    p_values = [i*0.01 for i in range(10, 100, 10)]

    seeds = [random.random()*43243718954 for i in range(num_tests)]
    feedback = ""
    correct = True

    for p in p_values:
        switched = 0
        switched_worked = 0
        stayed = 0
        stayed_worked = 0
        i = 0
        for s in seeds:
            i += 1
            test_player = test_class(p_switch=p)
            initial_selection = test_player.chosen_door
            Game = MontyHallGame()
            random.seed(s)
            test_player.play(Game)
            random.seed(s)
            p_val = random.random()
            if p_val < p: 
                ### should have switched
                switched += 1
                if initial_selection != Game.player_selection:
                    if Game.player_selection is not None:
                        switched_worked += 1
            else:
                ### should have stayed
                stayed += 1
                if initial_selection == Game.player_selection:
                    if initial_selection is not None:
                        stayed_worked += 1
        if switched != switched_worked or stayed != stayed_worked: 
            feedback += f"\nGiven p_switch: {p}, switched {switched_worked}/{switched} times and stayed {stayed_worked}/{stayed} times."
            correct = False

    if correct: 
        return "Random switch behavior works as expected", True
    else: 
        return "Your random switching strategy is off. It should switch if random.random() < self.p_switch\n" + feedback, False

