import autogen
import os

class IterativeCoding:
    def __init__(self, gpt_config):
        self.gpt_config = gpt_config
        self.llm_config = gpt_config['config_list']
        self.config_list = gpt_config['config_list']
        self.llm_model = gpt_config['config_list'][0]['model']
        self.n_code_iterations = 10  # Set your desired number of code iterations here
        self.one_done = False
        self.resumed_flow = False

        
        #-------------------------------- AGENTS -----------------------------------------------
        
        # Human user proxy - used for planning group chat and code iteration input.
        self.user_proxy = autogen.UserProxyAgent(
           name="manager",
           system_message="A human manager. They will dictate the task and test finished drafts",
           code_execution_config={"last_n_messages": 3, "work_dir": "IterativeCoding_AutoReply"},
           function_map={"write_latest_iteration": self.write_latest_iteration, "write_settled_plan": self.write_settled_plan},
        )

        # Planner agent - used to develop the numbered plan
        self.planner = autogen.AssistantAgent(
            name="planner",
            llm_config={
                "temperature": 0,
                "request_timeout": 600,
                "seed": 42,
                "model": self.llm_model,
                "config_list": self.config_list,
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

        This means, we need to {expand on functional requirements}


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
        self.coder = autogen.AssistantAgent(
            name="programmer",
            llm_config=self.gpt_config,
            system_message="""You and your group will be tasked with creating a python app which accomplishes the managerss request. Your job is the coder. You will be presented with a plan consisting of the necessary features and functional components. You will produce a python script which attempts to accomplish all of the tasks. However, some tasks are harder than others, and it may be best to leave a comment about what should be there, or what needs to be done. This is an iterative process, so you can expect a chance to revisit the code to fill in the blanks. You do not need to do everything on the first try. If you believe a section of code will be too hard to figure out on the first time, please consider leaving a note that can be tackled on the next iteration.
            
            Do not participate in any conversation or dialog. Your only output should be well formatted code blocks, and nothing else. It is someone elses job to review.
            
            You are only to produce code-blocks. Do not preempt the code with any extra text, and do not add any after it. 
            """
        )


        # Reviewer Agent - Used to review code iterations and provide a numbered list of criticisms to improve the code in the next iteration
        # TODO: Still unexpected behaviour sometimes, like listing the same issue 100 times, or saying things are not implemented when they are. Coder tends to know when reviewer is wrong, but this is a source of agent confusion and may be limiting potential.
        self.reviewer = autogen.AssistantAgent(
            name="reviewer",
            system_message="""You and your group will be tasked with creating a python app which accomplishes the items set out in the plan. You are the reviewer. 
        You will review the managers request, the planners interpretation of the request, the approved plan, and the latest code iteration.

        Read through the code, and explain what you see in the code. Explain what look like it should work OK, as it relates to the request and plan.

        If there are errors, the code will go through another iteration. If you believe there are errors, to help guide the programmer, explain what is not OK, and why it is not OK.

        Do not write any code. Just explain in easy to understand terms.

        Your job is critical - please be logical, focus, and try your best.
            
        """,
            llm_config=self.gpt_config,
        )
        
 
        

    def read_text_file(self, file_path):
        # Implement your file reading logic here
        try:
            with open(file_path, 'r') as file:
                contents = file.read()
            return contents
        except FileNotFoundError:
            print("File not found.")
        except IOError:
            print("Error reading file.")

    def write_latest_iteration_manual(self, code_message):
        # Implement writing the latest iteration manually here
        if code_message[0] == '`':
            # remove code block formatting
            code_message = code_message.replace('`','')
            
            # remove python from start of code
            code_message = code_message[6:]
            
            self.write_latest_iteration(code_message)
        
        else:
            self.write_latest_iteration(code_message)

    def write_latest_iteration_comments(self, comment):
        # Implement writing the latest iteration comments here
        script_name = self.working_dir+"comments_v1.log"
        version = 1

        while os.path.exists(script_name):
            version += 1
            script_name = f"{self.working_dir}/comments_v{version}.log"

        with open(script_name, "w") as script_file:
            script_file.write(comment)

    def retrieve_latest_iteration(self):
        # Implement logic to retrieve the latest iteration here
        files = os.listdir(self.working_dir)
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
        
    # Write latest python code iteration to an automatically incrementing script file.
    def write_latest_iteration(self, code_block):
        script_name = self.working_dir+"script_v1.py"
        version = 1

        while os.path.exists(script_name):
            version += 1
            script_name = f"{self.working_dir}/script_v{version}.py"

        with open(script_name, "w") as script_file:
            script_file.write(code_block)
            
    # write the settled plan to a master plan text file      
    def write_settled_plan(self, the_plan):
        plan_name = self.working_dir+"MasterPlan.txt"


        with open(plan_name, "w") as plan_file:
            plan_file.write(the_plan)
            
    def list_subdirectories(self,directory):
        subdirectories = []
        if os.path.exists(directory) and os.path.isdir(directory):
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    subdirectories.append(item)
        return subdirectories
    
    # Set project directory, must be passed in with trailing slash eg. "pdir/"
    def setProjectDir(self,project_dir):
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        
        self.project_dir = project_dir
        
    # Check if a version 1 file has already been generated      
    def does_version_one_exist(self):
        plan_name = self.working_dir+"comments_v1.log"
        if os.path.exists(plan_name):
            return True
        else:
            return False
            
    # Retrieve the highest-number version comment iteration   
    def retrieve_latest_iteration_comment(self,):
        files = os.listdir(self.working_dir)
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

    def run(self):
        
        found_dirs = self.list_subdirectories(self.project_dir)

        # No previously found projects
        if len(found_dirs) == 0:
            # Start new project
            print("No previous projects found! Starting a new project...")
            self.manager_request = input("Welcome to Iterative Coding! What python creation would you like? Type below:\n")
            self.project_name = input("What name would you like to give this project? Type below (must follow directory naming rules):\n")
            
            self.working_dir =  self.project_dir + self.project_name + "/"
            os.makedirs(self.working_dir)
            self.resumed_flow = False
            
        else:
            # handle new or old project
            user_selection = input("Welcome to Iterative Coding! Would you like to:\n1. Start a new project. \n2. Continue an old project.\n\nSelection:")
            
            if int(user_selection[0]) == 1:
                # Start a new Project
                manager_request = input("Welcome to Iterative Coding! What python creation would you like? Type below:\n")
                project_name = input("What name would you like to give this project? Type below (must follow directory naming rules):\n")
                
                self.manager_request = manager_request
                self.project_name = project_name  
                self.working_dir =  self.project_dir + self.project_name + "/"
                os.makedirs(self.working_dir)
                self.resumed_flow = False
                
            elif int(user_selection[0]) == 2:
                # list old projects
                print("\nThe following project folders were found:\n")
                
                for i in range(len(found_dirs)):
                    print("{sel}. {pdir}".format(sel = i, pdir = found_dirs[i]))
                    
                p_num = int(input("\nSelect project to continue:")[0])
                
                self.project_name = found_dirs[p_num] 
                self.working_dir =  self.project_dir + self.project_name + "/"
                self.one_done = self.does_version_one_exist()
                self.resumed_flow = True
                
        
  
        # If this is a first-time flow
        if not self.resumed_flow:
            self.user_proxy.initiate_chat(
                self.planner,
                message=self.manager_request,
            )
            # exit()

        # Begin the code iteration cycle
        for i in range(self.n_code_iterations):
            # First cycle of iterations has no review comments yet, so is a slightly different logic loop.
            if i == 0 and not self.one_done:
                plan_message = self.read_text_file(self.working_dir + 'MasterPlan.txt')

                # Send the coder the plan - Let it generate a first code iteration
                self.user_proxy.initiate_chat(
                    self.coder,
                    message=plan_message,
                )

                # Write the coder's code to a script_vn.py file
                self.write_latest_iteration_manual(self.coder.last_message()['content'])

                # Send the reviewer the plan and the code - Let it generate some feedback
                self.user_proxy.initiate_chat(
                    self.reviewer,
                    message=plan_message + '\n\n\n Latest Code Iteration \n\n\n' + self.read_text_file(self.working_dir + self.retrieve_latest_iteration())
                )

                # Write the reviewer's comments to a comments_vn.py file
                self.write_latest_iteration_comments(self.reviewer.last_message()['content'])

            # If not the first iteration, do regular iteration
            else:
                if self.one_done:
                    # Send coder the plan, latest code iteration, and last review
                    plan_message = self.read_text_file(self.working_dir + 'MasterPlan.txt')
                    code_iteration = self.read_text_file(self.working_dir + self.retrieve_latest_iteration())
                    code_review_comments = self.read_text_file(self.working_dir + self.retrieve_latest_iteration_comment())

                    self.user_proxy.initiate_chat(
                        self.coder,
                        message=plan_message + '\n\n\n Latest Code Iteration \n\n\n' + code_iteration + '\n\n Latest Code Review Comments \n\n' + code_review_comments
                    )

                    self.resumed_flow = False
                else:
                    # Send coder the plan, latest code iteration, and last review
                    plan_message = self.read_text_file(self.working_dir + 'MasterPlan.txt')
                    code_iteration = self.read_text_file(self.working_dir + self.retrieve_latest_iteration())

                    self.user_proxy.initiate_chat(
                        self.coder,
                        message=plan_message + '\n\n\n Latest Code Iteration \n\n\n' + code_iteration + '\n\n Latest Code Review Comments \n\n' + self.reviewer.last_message()['content']
                    )

                # Write the coder's code to a script_vn.py file
                self.write_latest_iteration_manual(self.coder.last_message()['content'])

                # Send the reviewer the plan and the code - Let it generate some feedback
                plan_message = self.read_text_file(self.working_dir + 'MasterPlan.txt')
                code_iteration = self.read_text_file(self.working_dir + self.retrieve_latest_iteration())

                self.user_proxy.initiate_chat(
                    self.reviewer,
                    message=plan_message + '\n\n\n Latest Code Iteration \n\n\n' + code_iteration
                )

                self.write_latest_iteration_comments(self.reviewer.last_message()['content'])


