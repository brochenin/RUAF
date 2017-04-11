
1. REQUIREMENTS
The SIMPLE tools require a recent version of python, present in the path variable. They have been tested with versions 3.4 and 3.6.

The GRAPH tools have the same python requirements, and additionally require pdflatex in the path variable.

The tools have been tested on Apple MacOS and Microsoft Windows

2. SETTINGS
Before using the tools, the user must edit the SETTINGS.txt file. As an example, this file is by default:
__________________________________
"input file",mycourse-1_step-activity.csv
"features output file",mycourse-1_result.csv
"number of seconds under which an activity is ignored",60
"drop out threshold",3
"come back threshold",3
"late or early threshold",2
__________________________________

Only the items after the comma can be edited. The order of the items should not be changed. The input and output must be edited as needed by the user:
- The "input file" is the path to a step activity file provided by FutureLearn.
- The "features output file" is the path to where the output should be.

The user may also edit the other parameters if they wish:
- The "number of seconds under which an activity is ignored" is the minimum amount of time a user should spend on a resource. Under this minimum, the user is considered as having ignored a resource.
- The "drop out threshold" is 1/t, where t is the proportion of resources a user must have done after some point in order to not be considered dropping out (see article for details). Here, with 3, the proportion of resources that must have been done is 1/3.
- The "come back threshold" is the amount of other resources a user mus have seen before coming bac to another in order to be counted in the 'drop' feature.
- The "late or early threshold" is the threshold used used for the computation of the 'late' and 'early' features (see article for details).


3. TOOLS
The SIMPLE tools export the features computed in the output file chosen in the settings.

The GRAPH tools additionally provide a pdf visualisation of them in the latex folder, under the name "graphs.pdf".

To use the tools simply double-click on the OS_TOOL file corresponding to your system. For instance, for the SIMPLE tool on WINDOWS, double-click on WINDOWS_SIMPLE.bat file.


4. COMMAND LINE
The SIMPLE tool can also be used in command line, "python FutureLearnProcess.py SETTINGS.txt". The GRAPH tool can be executed in command line by copying the results of the simple tool in the graph folder under the name data.csv, and using the command line "pdflatex graphs.tex" in the graph folder.