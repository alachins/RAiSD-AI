# Developer reference

## RAiSD-AI

The RAiSD-AI-GUI relies on the RAiSD-AI tool to perform its computations. For more information about RAiSD-AI, please refer to the general [README.md](../README.md). It contains detailed information about the tool, its capabilities, and how it works.

## Install and Run

The process of installing and running the GUI is the same as for normal users, see the appropriate chapters [Installing the GUI](/README.md#installing-the-gui) and [Running the GUI](/README.md#running-the-gui) in the project [README.md](../README.md).

When working on the GUI, make sure to activate the `raisd-ai-gui` environment so that running and testing the GUI will work correctly.

## Configuration

The GUI relies on a configuration file to mirror the allowed operations, parameters, and their values in the RAiSD-AI tool. This allows the GUI to be flexible and adaptable to changes in the underlying tool without requiring significant code changes.

When making changes to the RAiSD-AI tool, make sure to update the configuration file accordingly to reflect the changes. This will ensure that the GUI continues to function correctly and provides an accurate interface for users to interact with the RAiSD-AI tool.

### Config schema

Refer to the TODO: schema file for details on the structure and content of the configuration file.

## Structure

All the files related to the GUI is organized within the `gui/` folder. This includes all the code, the configuration file, stylesheets and images, the saved settings, tests, and the main app file. 

> [!NOTE]
> The only exception is the `environment-raisd-ai-gui.yml` file, which is located in the root of the project. 

The GUI code is divided into 5 main packages:
- [`components`](/gui/components/): Contains all the reusable components that are used throughout the GUI.
- [`execution`](/gui/execution/): Contains the code responsible for executing commands with the RAiSD-AI tool.
- [`model`](/gui/model/): Contains the data models used in the GUI.
- [`pages`](/gui/pages/): Contains the different pages of the GUI. These are the Run page, History page, and Settings page.
- [`style`](/gui/style/): Contains the stylesheets and images used to style the GUI.
- [`window`](/gui/window/): Contains the set-up window, splash screen, and the main window of the GUI.

### components

This package contains all the components that are used throughout the GUI. Some of them are separated into subpackages that are more specific to a certain page or functionality, while others are more general and can be used across different pages. These components are designed to be reusable and modular, allowing for easy maintenance and updates to the GUI.

### execution

This package contains the code responsible for executing the RAiSD-AI tool based on the parameters provided by the user through the GUI. It handles the communication between the GUI and the underlying RAiSD-AI tool, ensuring that the correct commands are executed and that the results are properly processed.

### model

This package contains the data models used in the GUI to represent the operations, parameters, results, history, settings, and other relevant data. These models are designed to provide a separation between the data and the GUI, making it easier to handle user input, display results, and maintain the overall state of the application.

### pages

This package contains the different pages of the GUI. These are the main page, history page, and settings page. The main page allows users to configure and run RAiSD-AI operations, the history page displays past operations and their results, and the settings page allows users to change certain settings.

### style

This package contains the stylesheets and images used to style the GUI. The stylesheets define the visual appearance of the GUI, including colors, fonts, and layout. This separation of style from functionality allows for easier maintenance and updates to the GUI's appearance.

### window

This package contains the window parts of the GUI. This includes the set-up window which allows the user to change the default settings, and set their initial workspace folder. It also includes the splash screen, which is shown while the app is loading. Lastly, it includes the main window which sets up the different pages of the GUI and handles how these pages are connected.

## Testing

Pytest is used for testing the GUI. The tests are located in the [gui/tests/](/gui/tests/) folder. To run the tests, make sure to activate the `raisd-ai-gui` environment and then run the following command in the terminal:

```bash
pytest
```

To specify the path of the folder/file you want to test, you can add it to the command. For example, to unit test the `test_parameter.py` file in the `model` package, you can run:

```bash
pytest gui/tests/unit/model/test_parameter.py
```

To get coverage information, add the `--cov=gui/` option to the command:

```bash
pytest --cov=gui/model --cov=gui/execution
```

Optionally add `--cov-report=term-missing` to get the line numbers that are not covered:

```bash
pytest --cov=gui/ --cov-report=term-missing
```