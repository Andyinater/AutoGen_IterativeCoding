import autogen
import os
from AndyTools import ManualManager, ManualGroupChat

# llm model 
llm_model = 'gpt-3.5-turbo'#'gpt-3.5-turbo' 'gpt-4-0613'

# working directory 
working_dir = 'Coding_WorkDir/'

# number of iterations before stopping (can always exit early or resume later)
n_code_iterations = 10

config_list = [
    {
        'model': llm_model,
        'api_key': 'YOUR API KEY HERE',
    }  # OpenAI API endpoint for gpt-3.5-turbo
 
]

print(config_list)

llm_config = {"config_list": config_list, "seed": 42}

gpt_config = {
    "seed": 42,  # change the seed for different trials
    "temperature": 0,
    "config_list": config_list,
    "request_timeout": 120,
}

# -- Agent Functions --

# write the settled plan to a master plan text file      
def write_settled_plan(the_plan):
    plan_name = working_dir+"MasterPlan.txt"


    with open(plan_name, "w") as plan_file:
        plan_file.write(the_plan)
        

# -- Helper Functions --

# Read and return a text file contents
def read_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            contents = file.read()
        return contents
    except FileNotFoundError:
        print("File not found.")
    except IOError:
        print("Error reading file.")
        

# Write latest python code iteration to an automatically incrementing script file.
def write_latest_iteration(code_block):
    script_name = working_dir+"script_v1.py"
    version = 1

    while os.path.exists(script_name):
        version += 1
        script_name = f"{working_dir}/script_v{version}.py"

    with open(script_name, "w") as script_file:
        script_file.write(code_block)
        
# Write latest review comment iteration to an automatically incrementing comment file.
def write_latest_iteration_comments(comment):
    script_name = working_dir+"comments_v1.log"
    version = 1

    while os.path.exists(script_name):
        version += 1
        script_name = f"{working_dir}/comments_v{version}.log"

    with open(script_name, "w") as script_file:
        script_file.write(comment)

# Retrieve the highest-number version code iteration        
def retrieve_latest_iteration():
    files = os.listdir(working_dir)
    py_files = [file for file in files if file.endswith('.py')]
    version_numbers = []
    for file in py_files:
        version = file.split('_v')[-1].split('.py')[0]
        version_numbers.append(int(version))
    max_version = max(version_numbers)
    for file in py_files:
        if file.endswith(f'_v{max_version}.py'):
            return file
    return None
    
# Retrieve the highest-number version comment iteration   
def retrieve_latest_iteration_comment():
    files = os.listdir(working_dir)
    py_files = [file for file in files if file.endswith('.log')]
    version_numbers = []
    for file in py_files:
        version = file.split('_v')[-1].split('.log')[0]
        version_numbers.append(int(version))
    max_version = max(version_numbers)
    for file in py_files:
        if file.endswith(f'_v{max_version}.log'):
            return file
    return None

# Write the latest code iteration to a text file
def write_latest_iteration_manual(code_message):
    if code_message[0] == '`':
        # remove code block formatting
        code_message = code_message.replace('`','')
        
        # remove python from start of code
        code_message = code_message[6:]
        
        write_latest_iteration(code_message)
    
    else:
        write_latest_iteration(code_message)

# Check if a version 1 file has already been generated      
def does_version_one_exist():
    plan_name = working_dir+"comments_v1.log"
    if os.path.exists(plan_name):
        return True
    else:
        return False
        
# Check if a master plan text file has already been generated      
def does_master_plan_exist():
    plan_name = working_dir+"MasterPlan.txt"
    if os.path.exists(plan_name):
        return True
    else:
        return False
    
# Human user proxy - used for planning group chat and code iteration input.
user_proxy = autogen.UserProxyAgent(
   name="manager",
   system_message="A human manager. They will dictate the task and test finished drafts",
   code_execution_config={"last_n_messages": 3, "work_dir": "CodeGroupLogic"},
   function_map={"write_latest_iteration": write_latest_iteration, "write_settled_plan": write_settled_plan},
)

# Planner agent - used to develop the numbered plan
planner = autogen.AssistantAgent(
    name="planner",
    llm_config={
        "temperature": 0,
        "request_timeout": 600,
        "seed": 42,
        "model": llm_model,
        "config_list": config_list,
        "functions": [
            {
                "name": "write_settled_plan",
                "description": "Writes the manager approved plan to a saved file. Only call this function if the manager has approved the plan. DO NOT USE THIS BEFORE RECEIVING MANAGER APPROVAL. Only pass in the approved plan. Pass it in such a way that print(the_plan) would not fail. You can only call this function AFTER the manager gives confirmation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "the_plan": {
                            "type": "string",
                            "description": "the setteld plan to be saved. Be sure the_plan is passed in such that calling print(the_plan) would be successful. ",
                        },
                    },
                    "required": ["the_plan"],
                },
            },
        ],
    },
    system_message="""You and your group will be tasked with creating a python app which accomplishes the managers request. 
Your job is the planner. When presented with a request, first try to understand what the manager is asking. Do this by explaining in more detail what the manager is asking for, and what the main challenges will be. Be specific and concise.

Next, you should develop a plan to solve the request. Explain what will need to be done, and why, in the app. Have a logical order - this will be passed on to the programmer as a settled plan.

Here is an example of what a settled plan would look like for a request:

-----------

The manager has asked us to {the managers request}.

In other words, what the manager is asking for is {more complete request definition/explanation}

This means, we need to {


A successful app for this task must achieve these things:
1. Functionality/Feature 1
    - Guide for achieving Functionality/Feature 1 
2. Functionality/Feature 2
    - Guide for achieving Functionality/Feature 2 
3. Functionality/Feature 3
    - Guide for achieving Functionality/Feature 3 

Do you agree, manager?

------------

Nice and short and succicnt, while still having the necessary information. Please use this as a guide.

Work with the manager until the manager approves of the plan. The manager will approve of the plan by using the phrase "sounds good"

Once the manager said "sounds good", you can write a call to write_settled_plan to write the settled plan into memory. Do not alter the plan after manager approval. Simply remove the question, "Do you agree, manager?".
    
""",
)

# Coding agent - used to generate code iterations
coder = autogen.AssistantAgent(
    name="programmer",
    llm_config=gpt_config,
    system_message="""You and your group will be tasked with creating a python app which accomplishes the managerss request. Your job is the coder. You will be presented with a plan consisting of the necessary features and functional components. You will produce a python script which attempts to accomplish all of the tasks. However, some tasks are harder than others, and it may be best to leave a comment about what should be there, or what needs to be done. This is an iterative process, so you can expect a chance to revisit the code to fill in the blanks. You do not need to do everything on the first try. If you believe a section of code will be too hard to figure out on the first time, please consider leaving a note that can be tackled on the next iteration.
    
    Do not participate in any conversation or dialog. Your only output should be well formatted code blocks, and nothing else. It is someone elses job to review.
    
    You are only to produce code-blocks. Do not preempt the code with any extra text, and do not add any after it. 
    """
)


# Reviewer Agent - Used to review code iterations and provide a numbered list of criticisms to improve the code in the next iteration
# TODO: Still unexpected behaviour sometimes, like listing the same issue 100 times, or saying things are not implemented when they are. Coder tends to know when reviewer is wrong, but this is a source of agent confusion and may be limiting potential.
reviewer = autogen.AssistantAgent(
    name="reviewer",
    system_message="""You and your group will be tasked with creating a python app which accomplishes the items set out in the plan. You are the reviewer. 
You will review the managers request, the planners interpretation of the request, the approved plan, and the latest code iteration.

Read through the code, and explain what you see in the code. Explain what look like it should work OK, as it relates to the request and plan.

If there are errors, the code will go through another iteration. If you believe there are errors, to help guide the programmer, explain what is not OK, and why it is not OK.

Do not write any code. Just explain in easy to understand terms.

Your job is critical - please be logical, focus, and try your best.
    
""",
    llm_config=gpt_config,
)

# group of agents/user that participate in planning group chat
planning_group = [user_proxy, planner]


# Flag for if a master plan already exists
resumed_flow = does_master_plan_exist()

# Flag for if a v1 already exists
one_done = does_version_one_exist()

# If this is a first-time flow
if not resumed_flow:
    task_to_do = input("What python creation would you like? Type below:\n")
    user_proxy.initiate_chat(
        planner,
        message=task_to_do,
    )
    
    # Exit python program after writing master plan - Restarting the program will go right into iterations.
    # TODO: This is done because an error is thrown if the next chat starts after this one, because it ended with a function call from Planner 
    # See PR #80 for more info.
    exit()

# Begin the code iteration cycle
for i in range(n_code_iterations):

    # First cycle of iterations has no review comments yet, so is a slightly different logic loop. Do not use this step if this is a resumed flow.
    if i == 0 and not one_done:
        
        # Send the coder the plan - Let it generate a first code iteration
        user_proxy.initiate_chat(
            coder, 
            message=read_text_file(working_dir+'MasterPlan.txt')
        )
        
        # Write the coder's code to a script_vn.py file
        write_latest_iteration_manual(coder.last_message()['content'])
        
        
        # Send the reviewer the plan and the code - Let it generate some feedback
        user_proxy.initiate_chat(
            reviewer, 
            message=read_text_file(working_dir+'MasterPlan.txt') + '\n\n\n Latest Code Iteration \n\n\n' + read_text_file(working_dir+retrieve_latest_iteration())
        )
        
        # Write the reviewer's comments to a comments_vn.py file
        write_latest_iteration_comments(reviewer.last_message()['content'])
        

        
    # If not first iteration, do regular iteration
    else:
        
        if one_done:
            # Send coder the plan, latest code iteration, and last review
            user_proxy.initiate_chat(
                coder, 
                message=read_text_file(working_dir+'MasterPlan.txt') + '\n\n\n Latest Code Iteration \n\n\n' + read_text_file(working_dir+retrieve_latest_iteration()) + '\n\n Latest Code Review Comments \n\n' + read_text_file(working_dir+retrieve_latest_iteration_comment())
            )
            
            resumed_flow = False
        
        else:
            # Send coder the plan, latest code iteration, and last review
            user_proxy.initiate_chat(
                coder, 
                message=read_text_file(working_dir+'MasterPlan.txt') + '\n\n\n Latest Code Iteration \n\n\n' + read_text_file(working_dir+retrieve_latest_iteration()) + '\n\n Latest Code Review Comments \n\n' + reviewer.last_message()['content']
            )
        
        # Write the coder's code to a script_vn.py file
        write_latest_iteration_manual(coder.last_message()['content'])
        
        # Send the reviewer the plan and the code - Let it generate some feedback
        user_proxy.initiate_chat(
            reviewer, 
            message=read_text_file(working_dir+'MasterPlan.txt') + '\n\n\n Latest Code Iteration \n\n\n' + read_text_file(working_dir+retrieve_latest_iteration())
        )
        
        write_latest_iteration_comments(reviewer.last_message()['content'])
        


















