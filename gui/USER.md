# User manual

## RAiSD-AI

The RAiSD-AI GUI relies on the RAiSD-AI tool to perform its computations. For more information about RAiSD-AI, please refer to the general [README.md](/README.md). It contains detailed information about the tool, its capabilities, and how it works.

## The RAiSD-AI GUI

The RAiSD-AI GUI provides a visual interface for running RAiSD-AI operations. On top of that, it adds several useful features:

1. **Sequential Operations**: The GUI allows you to [chain together multiple operations](#operation-selection-tab) in a single run, automatically passing the output of one operation as input to the next. This eliminates the need to manually run each operation or manage intermediate files.

2. **Parameter Validation**: Only valid parameters can be used. The GUI highlights invalid or missing parameters, ensuring you can only proceed when all inputs are correct.

3. **History Page**: All previous runs are stored and can be reviewed. You can reuse parameters from past runs to quickly set up new ones.

4. **Workspace Management**: All runs and their results are stored in a workspace folder, which can be changed at any time.

The GUI is especially useful for users who want to avoid manual command-line input, reduce errors, and keep track of their runs in an organized way.


## Install and Run

For information about installing and running the GUI, see the appropriate chapters [Installing the GUI](/README.md#installing-the-gui) and [Running the GUI](/README.md#running-the-gui) in the project [README file](/README.md)

## The Interface

The RAiSD-AI GUI consists of several pages that allow you to navigate through the different features and functionalities of the tool. Below is an overview of all pages.

### Complete Setup Window

![Screenshot of Setup Window](/screenshots/setup-dialog.filled-in.png)

The 'Complete Setup' window is the window you will see first when you use the GUI for the first time. 

It asks you to select a workspace where all your runs and their results will be stored. You can choose an existing folder or create a new one. Next to that, it allows you to change the default settings. 

> [!WARNING]
> Make sure to choose the same executable and environment manager as you chose when installing the GUI. 

The workspace and selected settings can be changed later in the [settings page](#settings-page).


### Run Page

The Run page is the main page of the GUI. It is used to execute RAiSD-AI operations. Its tabs allows you to select the operation you want to perform, configure the parameters, start the execution, monitor the progress, and view the results.

#### Operation Selection Tab

![Screenshot of the Run Page Operation Selection with Run ID](/screenshots/run-page.operation-selection.run1.multiple-operations.png)

The operation selection tab is the first step when running RAiSD-AI operations. It has three main input sections:

1. **Run ID**: This is a unique identifier for each run. It helps you keep track of different runs and their results. The results of the run will be stored in a directory whose name is the run ID inside the workspace.

2. **Operation Selection**: Here, you can choose the type of operation you want to perform.

3. **Input Data**: This section allows you to input the data required for the selected operation. This can include files, folders, and parameters.

The operation selection guides you through the possible combinations of operations and input types in a simple step-by-step manner. When choosing an operation to run, this section will ask you how you want to provide input data. That can often be either through uploading a file, or by running another operation to generate the necessary files. 

For example, the Model training operation needs a directory with two subdirectories containing prepared data. However, instead of having to run Data preparation twice, and then running Model training separately using the generated directory, you can choose to run these operations together. (See the screenshot above, where running multiple operations is selected.)

This works for any operation which is dependent on the output of another operation. However, you don't have to run all operations every time. Instead, if you have already prepared your data once, for instance, you can reuse it in future operations.

> [!NOTE]
> If the choice of run id or other input parameters will cause data to be overwritten, the GUI will show a warning and ask for confirmation before proceeding.

#### Parameter Input Tab

![Screenshot of the Run Page Parameter Input uncollapsed](/screenshots/run-page.parameter-input.run1.png)

The parameter input tab allows you to configure the parameters for the selected operations. The parameters are organized into sections, and there are specific sections each related to the selected operations. You can expand or collapse each section to focus on the parameters that are most relevant.

Most parameters have default values. To reset a parameter to its default value, click on the reset button next to it. If a parameter value is invalid or missing, the GUI will show which parameters are causing the issue. You are only able to continue to the next step if all parameters values are valid and the required ones are provided.

#### Parameter Confirmation Tab

![Screenshot of the Run Page Parameter Confirmation](/screenshots/run-page.parameter-confirmation.run1.png)

The parameter confirmation tab allows you to review the paramete values you have set before starting the execution. It provides a summary of all the parameters and their values. You can go back to the previous tab to edit if needed. Once you are satisfied with the parameters, you can proceed to run the commands.

The parameters that the GUI generated and which will be passed to RAiSD-AI are also shown in this tab. To copy these either click on one line to copy it or use the `Copy all commands` button to the whole command which will be executed by the GUI. This includes environment activation, the right RAiSD-AI executable, and the generated parameters.

The command that each line of parameters will be run with is also shown separately.

#### Run Tab

![Screenshot of the Run Page Run Tab](/screenshots/run-page.run.run1.running.png)

The run tab allows you to monitor the progress of the execution. It shows the status of each command, the output, and any errors that may occur. You can also stop the execution if needed.

Each command that will be run is symbolized with a box with it's name. The color of the box indicates the status of the command:
- *Empty*: Not started
- *Yellow*: Running
- *Blue*: Completed successfully
- *Red*: Completed with error

To see the output of the RAiSD-AI tool use the *"Toggle Console"* button. This will show the standard output on the left and error output on the right. You can toggle the console at any time during the execution to check the output.

#### Results Tab

![Screenshot of the Run Page Results Tab](/screenshots/run-page.results.run1.png)

The results tab allows you to view the results of the execution. It shows the files in the output folder of the run. You can double click on a file to view its contents. 
- The **RAiSD_Info** files contain the terminal output of the RAiSD-AI tool for each command that was run. This can be useful for debugging and understanding the results.
- The **RAiSD_Report** files contain the output of a sweep scan operation.

Below the file browser you can view the parameters that were used for the run. If you want to slightly modify these parameters and run again, you can click  the *"Edit Run"* button. This will take you back to the [operation selection tab](#operation-selection-tab) with the operations and parameters pre-filled with the values from the previous run. When you want to start a new run without the previous values, you can click the *"New Run"* button.

### History Page

The history page allows you to view all your previous runs and their results. It shows a list of all runs with their run ID, ordered by date. You can click on a run to view its details and results.

You can click the *"Reuse"* button to reuse the selected operations and parameters of that previous run for a new run. This will take you to the run page's [operation selection tab](#operation-selection-tab) with the operations and parameters pre-filled with the values from the selected run.

![Screenshot of the History Page](/screenshots/history-page.run1.png)

### Settings Page

The Settings page allows you to configure the GUI settings. Here you can change the workspace, which is the folder where your runs and their results are stored. You can also change the path to the RAiSD-AI tool, the environment manager, or the environment name if needed.

![Screenshot of the Settings Page](/screenshots/settings-page.png)
