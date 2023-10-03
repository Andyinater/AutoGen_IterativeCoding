# AutoGen_IterativeCoding
This repository demonstrates how a simple iterative coding loop, with history and resume capability, can be implemented in the AutoGen Framework. 

# Overview
This project results from an extension of the paradigm demonstrated in [AutoGen_MemoryManager](https://github.com/Andyinater/AutoGen_MemoryManager), where allowing an agent to have a fixed, trustworthy memory relieves the cognitive load that would otherwise be necessary to achieve the desired effect. The inspiration for this work comes from the author's personal struggles in achieving performant code from the [AutoGen Examples](https://microsoft.github.io/autogen/docs/Examples/AutoGen-AgentChat/) for use cases sufficiently different than those in the example. While in its current state, this flow is able to achieve better results on cases that failed in the examples, this repo should also serve as an example of a more generic code production workflow.

Currently this project only works to produce python code. With some work, this can be adapted.

# How it Works
The program runs in two phases: the Planning Phase, and the Iteration Phase.

![Diagram depicting the program phases, including the interactions between user/agents, creation of files, and presentation of files to agents.](/flow.png)

## Planning Phase
The Planning Phase consists of a chat between the human user (Manager) and an AI Planner assistant (Planner). The Manager is first prompted:

>What python creation would you like? Type below:

Here the Manager can request the python app they would like:

>Make me a python app that displays the current time on an analog clock face.

The Planner will then create a list of functional requirements that define a successful completion of the task. If the Manager deems the plan sufficient, they can direct the plan to be saved. The plan will be saved in the working directory.

This concludes the Planning Phase.

## Iteration Phase
The Iteration Phase consists of individual chats between the Manager and either the Coder or the Reviewer.

### Iteration 0
If coming directly from the Planning Phase, the Iteration Phase will begin with the Coder producing the first attempt at satisfying the plan. 

The Coder's output will be recorded to a python script file in the working directory, starting at `script_v1.py`.

The Reviewer will then be presented with the plan and the content of the most recent script, and is asked to evaluate the code and produce a list of criticisms/comments to be used to guide the next iteration.

The Manager can also test the code if desired and provide feedback to the Reviewer or Coder.

### Iteration n
After the first iteration, the main iterative loop begins.

The Coder will be presented with the plan, the latest code iteration, and the latest Reviewer comments. They will then produce another iteration of the code, attempting to resolve the Reviewer comments while also adhering to the plan.

The Reviewer will then be presented with the plan and the content of the most recent script, and is asked to evaluate the code and produce a list of criticisms/comments to be used to guide the next iteration.

The Manager can also test the code if desired and provide feedback to the Reviewer or Coder.

# Getting Started

The author assumes you have [installed AutoGen](https://github.com/microsoft/autogen#installation) and have it running on your system. 

## Preparing the Work Space

Before you begin, be sure the directory defined in `working_dir` exists in the active directory – this is where the plan will be stored, as well as all script iterations.

Also, be sure the file `AndyTools.py` is in the same directory as `IterativeCoding.py` – this contains overridden AutoGen `GroupChat` and `GroupChatManager` classes to allow manual control of group chat speakers.

## Starting a Fresh Project

To start a fresh project, be sure the `working_dir` contains no files.

Start the program with `python IterativeCoding.py`

### Running the Planning Phase

The planning phase will begin with the user entering the desired application:
> Make a python app that writes the current time to an analog clock.

After hitting `Enter`, the user will be prompted to direct who speaks next:
> Who speaks next: Planner

The user should enter `Planner` to allow the Planner to produce an initial plan:
>Plan:
>1. Create a graphical user interface (GUI) for the analog clock.
>2. Implement a function to retrieve the current time.
>3. Implement a function to convert the current time into the corresponding positions of the clock hands.
>4. Update the GUI to display the clock hands at the correct positions based on the current time.
>5. Continuously update the clock display to show the current time in real-time.
>---------------------------------------------------------------------------------
>Who speaks next:Manager

After the Planner responds, the user should direct the Manager to speak next. If the user desires other features be included, or has any problems with the plan, they can tell the Planner what changes they desire. After this, the user should allow the Planner to speak again.

Once the Planner returns a plan that is acceptable, the user should say "sounds good" through the Manager. The user should then direct the `recorder` to speak next. The recorder will make a function call to write the plan to the working directory, finalizing the application requirements. The `Manager` must be used to execute the function call by sending a blank response (auto-reply). The Manager must then exit the conversation to conclude the planning phase. 

A full planning phase will run something like this:

```
What task do you ask? Type it below:
Make a python app that writes the current time to an analog clock
←[33mmanager←[0m (to chat_manager):

Make a python app that writes the current time to an analog clock

--------------------------------------------------------------------------------
Who speaks next:planner
←[33mplanner←[0m (to chat_manager):

Plan:
1. Create a graphical user interface (GUI) for the analog clock.
2. Implement a function to retrieve the current time.
3. Implement a function to convert the current time into the corresponding positions of the clock hands.
4. Update the GUI to display the clock hands at the correct positions based on the current time.
5. Continuously update the clock display to show the current time in real-time.

--------------------------------------------------------------------------------
Who speaks next:manager
Provide feedback to chat_manager. Press enter to skip and use auto-reply, or type 'exit' to end the conversation: Can you make the hour hand pink too?
←[33mmanager←[0m (to chat_manager):

Can you make the hour hand pink too?

--------------------------------------------------------------------------------
Who speaks next:planner
←[33mplanner←[0m (to chat_manager):

Adjusted Plan:
1. Create a graphical user interface (GUI) for the analog clock.
2. Implement a function to retrieve the current time.
3. Implement a function to convert the current time into the corresponding positions of the clock hands.
4. Update the GUI to display the clock hands at the correct positions based on the current time.
5. Adjust the color of the hour hand to pink.
6. Continuously update the clock display to show the current time in real-time.

--------------------------------------------------------------------------------
Who speaks next:manager
Provide feedback to chat_manager. Press enter to skip and use auto-reply, or type 'exit' to end the conversation: sounds good
←[33mmanager←[0m (to chat_manager):

sounds good

--------------------------------------------------------------------------------
Who speaks next:recorder
←[33mrecorder←[0m (to chat_manager):

←[32m***** Suggested function Call: write_settled_plan *****←[0m
Arguments:
{
  "the_plan": "1. Create a graphical user interface (GUI) for the analog clock.\n2. Implement a function to retrieve the current time.\n3. Implement a function to convert the current time into the corresponding positions of the clock hands.\n4. Update the GUI to display the clock hands at the correct positions based on the current time.\n5. Adjust the color of the hour hand to pink.\n6. Continuously update the clock display to show the current time in real-time."
}
←[32m*******************************************************←[0m

--------------------------------------------------------------------------------
Who speaks next:manager
Provide feedback to chat_manager. Press enter to skip and use auto-reply, or type 'exit' to end the conversation:
←[31m
>>>>>>>> NO HUMAN INPUT RECEIVED.←[0m
←[31m
>>>>>>>> USING AUTO REPLY...←[0m
←[35m
>>>>>>>> EXECUTING FUNCTION write_settled_plan...←[0m
←[33mmanager←[0m (to chat_manager):

←[32m***** Response from calling function "write_settled_plan" *****←[0m
None
←[32m***************************************************************←[0m

--------------------------------------------------------------------------------
Who speaks next:manager
Provide feedback to chat_manager. Press enter to skip and use auto-reply, or type 'exit' to end the conversation: exit
```

At this point the terminal should be released. The Iteration Phase can now begin.

## Iterating a Project

The Iteration Phase runs the same whether starting the Iteration Phase directly after planning or when resuming it after stopping a previous run.

Begin the Iteration Phase by calling the main script again: `python IterativeCoding.py`

The user can continually enter `exit` as the feedback to let the iterations run without additional input. 

The user can provide feedback/direction on the process to either the Coder or the Reviewer, although this functionality has not been thoroughly tested.

The iteration will begin with a chat with the Coder, passing in the plan, and if not the first iteration, the last code iteration and the last review comments as well for context.

Replying `exit` to the Coder will result in a function call to format and write the Coder's last message to a script file with incrementing version numbers.

After this, the Reviewer will be presented with the plan and the latest code and be asked to make comments/criticisms on the code direction. If it concludes another iteration is required, it will end with `ITERATE`. If it concludes testing is required, it will end with `TEST`.

Replying `exit` to the Reviewer will end the current iteration. If `n_code_iterations` has not been exceeded, another iteration will begin by starting a chat with the Coder, passing in the plan, the last code iteration, and the last code review comments as context.

## Testing an Iteration

The user is able to run any script iterations in the `working_dir` while the iterative process is running. Feedback from the code execution can be provided by the user to either the Coder or the Reviewer to incorporate into the program.

# Known Issues

Sometimes the Reviewer will produce a 100+ point list of the same issue.

Due to above issue, Reviewer may perpetually suggest to "iterate".

# I Wish I Had Time To...

Make the planning phase not require a group chat – while demonstrative in how a manual group chat can be made, it is not necessary for the flow to run as intended.

Include Git `diff` style revisioning, or actually *use* Git. (See: [ChatDev](https://github.com/OpenBMB/ChatDev))

Add logic to create working directory if it doesn't exist. Tie in with logic to select which project to continue working on based on directory names.

Include automated testing and code execution during iterations – feed back error messages or Manager comments.

Write the latest review comments to a text file with similar versioning as the scripts - allow resumption with last comments brought in as well.


# Future Work


