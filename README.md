# AutoGen_IterativeCoding
This repository demonstrates how a simple iterative coding loop, with history and resume capability, can be implemented in the AutoGen Framework. 

# Overview
This project results from an extension of the paradigm demonstrated in early versions of [AutoGen_MemoryManager](https://github.com/Andyinater/AutoGen_MemoryManager), where allowing an agent to have a fixed, trustworthy memory relieves the cognitive burden required to achieve the desired effect. This work is inspired by the author's personal struggles in achieving performant code when applying the [AutoGen examples](https://microsoft.github.io/autogen/docs/Examples/AutoGen-AgentChat/) to sufficiently different use cases. While this flow can achieve more performant code where the AutoGen examples failed, this repo's primary function is to provide an example of a more generic code production workflow.

Currently, this project can only produce Python code. With some work, this can be adapted.

# How it Works

* Writing and reading information outside of the conversation's context window lets the user reset the window and reduce token usage – without losing valuable context for agents.
* Creating a project plan and presenting it to agents on every iteration keeps the scope focused.
* Presenting only the latest version of code and comments prevents agents from getting 'distracted' by previously faulty code or now-irrelevant comments.

The program consists of two phases. In the **planning phase**, a user's request results in a detailed plan for a Python project. In the **iteration phase**, the Python script is created and improved over several code-and-review cycles. 

![Diagram depicting the program phases, including the interactions between user/agents, creation of files, and presentation of files to agents.](/flow.png)

## Planning Phase
The planning phase consists of a conversation between the human user (**Manager**) and an AI planner assistant (**Planner**). 

The Manager is asked to request a Python creation, for example, "Make me a python app that displays the current time on an analog clock face." The Manager is also asked to provide a name for the project, which will be used to create a new project folder in the working directory.

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

Ensure both `main.py` and `IterativeTools.py` are in your working directory. 

Start the program with `python main.py`. The program checks if you have a `IterCode_Projects` folder in your working directory. If it does not find one, it will create one. All projects will be saved in subfolders within the `IterCode_Projects` folder.

### Planning the Project

The planning phase begins when you enter a request for a Python creation.
> Make a python app that writes the current time to an analog clock.

Press **Enter** to continue, then enter a project name. Because this is used to name the project folder, it must follow standard directory naming rules.
> AnalogClock

Press **Enter** to begin the conversation with the Planner. It takes the request and produce an initial plan:

```
Plan:
1. Create a graphical user interface (GUI) for the analog clock.
2. Implement a function to retrieve the current time.
3. Implement a function to convert the current time into the corresponding positions of the clock hands.
4. Update the GUI to display the clock hands at the correct positions based on the current time.
5. Continuously update the clock display to show the current time in real-time.
```

If the plan misses specific features or has any other issues, you (as the Manager) can tell the Planner what needs to be changed. It will return an updated plan.

Once the Planner returns an acceptable plan, enter `sounds good`. The Planner will make a function call to write the plan to the project folder; press **Enter** to auto-reply and execute the function call. The Planner provides confirmation when the call is complete.

Enter `exit` to end the conversation with the Planner. The first iteration phase (iteration 0) will begin immediately.

## Iterating Through Code-Review Cycles
All iterations start with a conversation between you (as the Manager) and the Coder.  

The saved plan is presented to the Coder. If there are existing scripts or comments in the project folder, the latest versions of each are also presented. The Coder then writes code to the console. Enter `exit` to end the conversation with the Coder and execute a function call to write the code to a new `script_vn.py` file in the project folder. 

A conversation between the Manager and the Reviewer begins immediately. The saved plan and latest version of the script are presented to the Reviewer. If there are existing comments in the project folder, the latest version is also presented. The Reviewer then writes comments to the console. Enter `exit` to end the conversation with the Review and execute a function call to write the comments to a new `comments_vn.txt` file in the project folder. 

The next loop starts immediately with a new conversation between the Manager and the Coder.

End the program at any time by terminating it. 

>[!IMPORTANT]
>Remember that code or comments shown in the console window are only written to the project folder after a function call. Review the latest files in your working directory before terminating the program.

## Testing an Iteration

You can run the scripts written to the project folder while in the iteration phase. Instead of entering `exit` to end the conversation and move to the next agent, you can provide feedback directly to the Coder or Reviewer. They will return updated code or comments. Enter `exit` when you are ready to continue.

For example, imagine you have asked for "an app that lets me play Tetris". After some iterations, the Reviewer may conclude that the code is performant and meets the requirements of the plan. However, when you test the script yourself, you realize the blocks are falling far too fast for a human to react to. You can tell the Reviewer this and they will revise their comments accordingly. You can then continue to the next iteration where the Coder will adjust the script to (hopefully!) solve the issue.

## Continuing a Project

When re-running `main.py`, the program checks for existing projects in the `IterCode_Projects` folder. If it finds existing projects, you will be asked if you want to start a new project or continue an existing project. 

If you continue an existing project, an iteration will begin immediately, with the plan, latest script, and latest comments presented to the Coder.

# Known Issues

* Sometimes the Reviewer will produce a 100+ point list of the same issue.
* Due to above issue, Reviewer may perpetually suggest to "iterate".
* There is no code to exit the program, the user must terminate it outside of the console window.
