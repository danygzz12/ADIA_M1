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
    
def failed_case_message(expected_output, real_output, func_name, arg, arg_name=True):
    if arg_name:
        arg_text = [str(key)+"="+str(value) for key, value in arg.items()]
    else:
        arg_text = [str(value) for value in arg.values()]
    arg_text = ", ".join(arg_text)
    return f"\nCalling {func_name}({arg_text}) returned: \n{real_output}. \nExpected: \n{expected_output} \n"


def grade_code(func, max_score=5):
    import pickle 

    with open("ADIA_M1/tests_" + func.__name__, "rb") as f:
        test_cases = pickle.load(f)

    passed_tests = 0
    total_tests = 0
    failed_messages = ""

    for case in test_cases: 
        total_tests += 1
        real_output = func(**case[0])
        expected_output = case[1]

        passed = compare_returns(expected_output, real_output)

        if passed:
            passed_tests +=1 
            continue 

        failed_messages += failed_case_message(expected_output, real_output, func.__name__, case[0])

    score = passed_tests/total_tests*max_score
    feedback = f"Passed {passed_tests}/{total_tests}.\nScore: {score}"+failed_messages
    return feedback
