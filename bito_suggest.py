# Import necessary modules and libraries
import sublime
import sublime_plugin
import subprocess
import os
import threading
import time


# Helper function to execute a command and return the output
def check_output(cmd):
    pop = os.popen(cmd)
    ret = pop.read()
    pop.close()
    return ret


# Sublime Text command for running Bito suggestions
class BitoSuggestCommand(sublime_plugin.TextCommand):
    """Command to run Bito suggestions"""

    def run(self, edit):
        # Get the last selection in the view
        sel = self.view.sel()[-1]

        # Insert new lines at the end of the selection
        self.view.insert(edit, sel.end(), "\n\n")

        # Display a status message indicating that Bito is running
        sublime.status_message("Running Bito...")

        # Create a new thread to run the get_suggestion method
        child = threading.Thread(target=self.get_suggestion, args=(edit, sel))
        child.start()

    def get_suggestion(self, edit, sel):
        """Method to fetch suggestions from Bito"""

        # Formulate the input code for Bito
        input_code = (
            "bito <<EOF\nPlease continue the following code.  DO NOT replicate the code"
            " given to you, just continue with the code.  Always enclose the code in tags"
            " ```like this```.  Make sure to heed any comments near the end of the code,"
            " and if the last comment does have have a code block that it describes, you must"
            " create the code block.  If there is nothing to be done, output a comment that says so"
            f"\n\n{self.view.substr(sublime.Region(0, sel.end()))}\n\nEOF"
        )

        # Execute the Bito command and get the result
        result = check_output(input_code)

        # Extract the relevant code block from the result
        if "```" in result:
            result = result.split("```")[1]
            if result.startswith("python"):
                result = result[6:]
        # If there are no tags, assume the whole thing is code

        # Run the "insert_this" command with the obtained result
        self.view.run_command(
            "insert_this", {"characters": result, "where": sel.end() + 2}
        )


# Sublime Text command for inserting text at a specific position
class InsertThisCommand(sublime_plugin.TextCommand):
    """Command to insert text at a specific position"""

    def run(self, edit, where, characters):
        """Method to perform the insertion"""

        # Insert the specified characters at the given position
        self.view.insert(edit, where, characters)
