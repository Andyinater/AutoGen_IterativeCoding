# AutoGen_IterativeCoding
This repository demonstrates how a simple iterative coding loop, with history and resume capability, can be implemented in the AutoGen Framework. 

# Overview
This project results from an extension of the paradigm demonstrated in early versions of [AutoGen_MemoryManager](https://github.com/Andyinater/AutoGen_MemoryManager), where allowing an agent to have a fixed, trustworthy memory relieves the cognitive burden required to achieve the desired effect. This work is inspired by the author's personal struggles in achieving performant code when applying the [AutoGen examples](https://microsoft.github.io/autogen/docs/Examples/AutoGen-AgentChat/) to sufficiently different use cases. While this flow can achieve more performant code where the AutoGen examples failed, this repo's primary function is to provide an example of a more generic code production workflow.

Currently, this project can only produce Python code. With some work, this can be adapted.

# How it Works

* Writing and reading information outside of the conversation's context window lets the user clear the window and reduce token usage – without losing valuable context for agents.
* Creating a project plan and presenting it to agents on every iteration keeps the scope focused.
* Presenting only the latest version of code and comments prevents agents from getting 'distracted' by previously faulty code or now-irrelevant comments.

The program consists of two phases. In the **planning phase**, a user's request results in a detailed plan for a Python project. In the **iteration phase**, the Python script is created and improved over several code-and-review cycles. 

![Diagram depicting the program phases, including the interactions between user/agents, creation of files, and presentation of files to agents.](/flow.png)

## Planning Phase
The planning phase consists of a conversation between the human user (**Manager**) and an AI planner assistant (**Planner**). The Manager is first prompted:

>What Python creation would you like? Type below:

Here the Manager can request the Python app they would like:

>Make me a python app that displays the current time on an analog clock face.

The Manager is also asked to provide a name for the project, which will be used to create a new project folder in the working directory.

The Planner then creates a list of functional requirements that define the successful completion of the task. If the Manager is not happy with the plan, they can converse with the Planner to edit the plan. Once the Manager deems the plan sufficient, they can direct the plan to be saved. The plan will be saved in the project folder.

This concludes the planning phase. The iteration phase begins immediately after exiting the conversation with the Planner.

## Iteration Phase
The iteration phase consists of individual conversations between the Manager and one of two assistants: the **Coder** or the **Reviewer**.

### Iteration 0
If coming directly from the planning phase, the iteration phase begins with the Coder's first attempt at satisfying the plan. 

The Coder is presented with the plan, and its output is recorded to a Python script file in the project folder, starting at `script_v1.py`.

The Reviewer is then presented with the plan and the v1 script. It is asked to evaluate the code and produce a list of criticisms/comments the Coder can use to guide the next iteration. The list is recorded to a `.txt` file in the project folder, starting at `comments_v1.py`.

The Manager can also test the code if desired and provide feedback to the Reviewer or Coder.

### Iteration _n_
After the first iteration, the main iterative loop begins.

The Coder is presented with the plan, the latest script `script_v1.py`, and the latest comments `comments_v1.py`. It produces another iteration of the code, attempting to resolve the Reviewer comments while also adhering to the plan. The new script file will have its version number incremented by 1, resulting in `script_v2.py`.

The Reviewer is then presented with the plan and the latest script `script_v2.py`. It is asked to evaluate the code and produce a list of criticisms/comments the Coder can use to guide the next iteration. The new comment file will have its version number incremented by 1, resulting in `comments_v2.py`.

The Manager can also test the code if desired and provide feedback to the Reviewer or Coder.

The loop continues until some iteration _n_, when the user is happy with performance of the latest script.

# Getting Started

The author assumes you have [installed AutoGen](https://github.com/microsoft/autogen#installation) and have it running on your system. 

## Preparing the Workspace

Ensure the directory defined in `working_dir` exists in the active directory – this is where the plan will be stored, as well as all script iterations.

Also ensure the file `AndyTools.py` is in the same directory as `IterativeCoding.py` – this contains overridden AutoGen `GroupChat` and `GroupChatManager` classes to allow manual control of group chat speakers.

## Starting a Fresh Project

To start a fresh project, the `working_dir` should not contain any files.

Start the program with `python IterativeCoding.py`.

### Planning the Project

The planning phase begins when you enter a request for a Python creation.
> Make a python app that writes the current time to an analog clock.

Press `Enter` to continue, then enter a project name. Because this is used to name the project subfolder in the working directory, it must follow standard directory naming rules.
> AnalogClock

Press `Enter` to begin the conversation with the Planner. It takes the request and produce an initial plan:

```
Plan:
1. Create a graphical user interface (GUI) for the analog clock.
2. Implement a function to retrieve the current time.
3. Implement a function to convert the current time into the corresponding positions of the clock hands.
4. Update the GUI to display the clock hands at the correct positions based on the current time.
5. Continuously update the clock display to show the current time in real-time.
---------------------------------------------------------------------------------
Who speaks next:Manager
```
If the plan misses specific features or has any other issues, you can tell the Planner what needs to be changed, and it will update the plan.

Once the Planner returns an acceptable plan, enter `sounds good`. The Planner will make a function call to write the plan to the project folder; press `Enter` to auto-reply and execute the function call. The Planner provides confirmation when the call is complete.

A complete planning phase will look similar to this:

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

At this point the terminal should be released. The iteration phase can now begin.

## Iterating a Project

The iteration phase runs the same whether starting the iteration phase directly after planning or when resuming it after stopping a previous run.

Begin the iteration phase by calling the main script again: `python IterativeCoding.py`

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

# Future Work


