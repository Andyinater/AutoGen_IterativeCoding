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
    llm_config=gpt_config,
    system_message='''You and your group will be tasked with creating a python app which accomplishes the managers request. 
	Your job is the planner. When presented with a request, determine what key features and functional compenents will be required to fulfill the task. Try to keep each feature succinct. You do not need to determine how the feature needs to be solved or implemented, you simply need to recognize what tasks your group will need to solve.
	
	Your only response should be the plan. DO NOT produce code.
    
    Do not include testing in the plan.
    
    If you are requested to adjust the plan by the manager, please do so accordingly.
    
''',
)

# Coding agent - used to generate code iterations
coder = autogen.AssistantAgent(
    name="programmer",
    llm_config=gpt_config,
    system_message="""You and your group will be tasked with creating a python app which accomplishes the managerss request. Your job is the coder. You will be presented with a plan consisting of the necessary features and functional components. You will produce a python script which attempts to accomplish all of the tasks. However, some tasks are harder than others, and it may be best to leave a comment about what should be there, or what needs to be done. This is an iterative process, so you can expect a chance to revisit the code to fill in the blanks. You do not need to do everything on the first try. If you believe a section of code will be too hard to figure out on the first time, please consider leaving a note that can be tackled on the next iteration.
    
    Do not participate in any conversation or dialog. Your only output should be well formatted code blocks, and nothing else. It is someone elses job to review.
    
    
    """
)

# Recorder agent - used to record the master plan to a text file after it is settled
# TODO: Not necessary, should be able to use a hard coded function call on planner's last message - prompt tuning will be required.
recorder = autogen.AssistantAgent(
    name="recorder",
    llm_config={
        "temperature": 0,
        "request_timeout": 600,
        "seed": 42,
        "model": llm_model,
        "config_list": config_list,
        "functions": [
            {
                "name": "write_settled_plan",
                "description": "Writes the settled plan to a saved file. Only call this function if the manager has approved the plan. Only pass in the approved plan. Pass it in such a way that print(the_plan) would not fail. You can only call this function AFTER the manager gives confirmation.",
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
    system_message="""You and your group will be tasked with creating a python app which accomplishes the managers request. Your job is to make sure the final master plan is recorded. When the Manager has approved the planners plan, use the write_settled_plan function to record the plan. Be sure the value for the_plan being passed into the function is correctly formatted.

    The ONLY function call you are permitted to take is 'write_settled_plan'
    
    """
)

# Reviewer Agent - Used to review code iterations and provide a numbered list of criticisms to improve the code in the next iteration
# TODO: Still unexpected behaviour sometimes, like listing the same issue 100 times, or saying things are not implemented when they are. Coder tends to know when reviewer is wrong, but this is a source of agent confusion and may be limiting potential.
reviewer = autogen.AssistantAgent(
    name="reviewer",
    system_message="""You and your group will be tasked with creating a python app which accomplishes the items set out in the plan. You are the reviewer. You will review drafts of code that attempt to accomplish the items in the plan. After reading the code, you should determine if the code could use another iteration, or if it is ready for a manager to test. If you believe the code will throw an error, or is feature incomplete, it MUST go through another iteration. You do not complete this iteration - someone else has that task.
	
	When you respond, please describe succicntly and accurately what deficiencies exist in the current code, such that the code writer will have enough information to modify the code and fix the deficiencies. Respond in a numbered list.
    
    Your only response should be the numbered list. Under no circumstances are you to generate any code.
    
    After the numbered list, respond with simply "ITERATE" or "TEST", depending if you believe the code needs iteration, or if it is ready for testing.
    
    The numbered list should have less than 30 items. It can have any amount between 1 and 30.
""",
    llm_config=gpt_config,
)

# group of agents/user that participate in planning group chat
planning_group = [user_proxy, planner, recorder]


# Overridden GroupChat and GroupChatManager Classes that allows manual control of group chat
# Manager MUST have the name 'Manager' or the overridden class will not work.
# TODO: Could be a 1 on 1 with planner and user, if above Recorder Agent suggestions are used.
groupchat = ManualGroupChat(agents=planning_group, messages=[], max_round=50)
manager = ManualManager(groupchat=groupchat, llm_config=gpt_config, human_input_mode='ALWAYS')

# Flag for if a master plan already exists
resumed_flow = does_master_plan_exist()

# Flag for if a v1 already exists
one_done = does_version_one_exist()

# If this is a first-time flow
if not resumed_flow:
    task_to_do = input("What python creation would you like? Type below:\n")
    user_proxy.initiate_chat(
        manager,
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
        



















