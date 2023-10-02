# AutoGen_IterativeCoding
This repository demonstrates how a simple iterative coding loop, with history and resume capability, can be can be implemented in the AutoGen Framework. 

# Overview
This project is the result from an extension of the paradigm demonstrated in AutoGen_MemoryManager(MAKE THIS A LINK), where allowing an agent to have a fixed, trustworthy memory relieves the cognitive burden that would otherwise be necessary to achieve the same effect. The inspiratiom for this work comes from the author's personal struggles in achieving performant code from the AutoGen Examples for use-cases sufficiently different from those in the example. While in it's current state this flow is able to achieve better results on cases that failed in the examples, this Repo should also serve as an example of a more generic code production workflow.

(CONSIDER A DIAGRAM SHOWING THE BREAKDOWN OF STEPS)

# Example Iterative Code Results
(MAKE SOME CONTENT FOR AN EXAMPLE)


# How it Works
The program runs in two phases: the Planning Phase, and the Iterative Phase.

## Planning Phase
The planning phase consists of a chat between the human user (Manager) and an AI Planner assistant (Planner). The Manager is first prompted:

>What python creation would you like? Type below:

Here the Manager can request the python app they would like. Eg:

>Make me a python app that displays the current time on an analog clock face.

The Planner will then create a list of functional requirements that define a successful completion of the task. If the Manager deems the plan sufficient, they can direct the plan to be saved.

This concludes the Planning Phase.

## Iterative Phase
The iterative phase consists of individual chats between the Manager and either the Coder, or the Reviewer.

### Iteration 0
If coming directly from the planning phase, the Iteration phase will begin with the Coder producing the first attempt at satisfying the plan. 

The Coder's output will be recorded to a python script file in the working directory, starting at `script_v1.py`.

The reviewer will then be presented with the Plan and the content of the most recent script, and is asked to evaluate the code and produce a list of criticisms/comments to be used to guide the next iteration.

The Manager can also test the code if desired at this point and provide feeback to the reviewer to include in the comments.

### Iteration n
After the first iteration, the main iterative loop begins.

The Coder will be presented with the Plan, the latest code iteration, and the latest reviewer comments. They will then produce another iteration of the code, attempting to resolve the reviewer comments while also adhering to the plan.

The reviewer will then be presented with the Plan and the content of the most recent script, and is asked to evaluate the code and produce a list of criticisms/comments to be used to guide the next iteration.

The Manager can also test the code if desired at this point and provide feeback to the reviewer to include in the comments.








# Known Issues
Sometimes the reviewer will produce a 100+ point list of the same issue
