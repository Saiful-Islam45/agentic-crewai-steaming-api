# website_builder_api/crew_runner.py

import os
import sys
import re
import threading
import queue # Python's built-in queue module
from io import StringIO
from dotenv import load_dotenv
from crewai import Crew, Process

# Load environment variables
load_dotenv()

# Import agents and tasks from their respective files
from .crew_agents import (
    market_research_lead_agent,
    demographic_data_analyst_agent,
    niche_demand_analyst_agent
)
from .crew_tasks import (
    demographic_analysis_task,
    niche_demand_analysis_task,
    market_viability_report_task
)

# Define a marker to signal the end of the stream from the thread
END_OF_STREAM_MARKER = "__END_OF_CREW_OUTPUT__"
ERROR_STREAM_MARKER = "__CREW_ERROR_OCCURRED__"

# Enhanced function to strip ANSI escape codes
def strip_ansi_codes(s):
    """
    Strips ANSI escape codes and other non-printable control characters from a string.
    Ensures input is treated as a string.
    """
    if not isinstance(s, str):
        s = str(s)

    # Regex to match common ANSI escape codes (e.g., \x1b[...m)
    s = re.sub(r'\x1b\[[0-9;]*m', '', s)
    # Remove other common non-printable ASCII characters (e.g., carriage return, form feed)
    s = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', s)
    return s

# Function to format CrewAI output into basic Markdown for line-by-line display
def format_crewai_output_to_markdown(line_text):
    """
    Formats a single line of CrewAI verbose output into basic Markdown.
    Returns the formatted string *without* a trailing newline.
    """
    if not isinstance(line_text, str):
        line_text = str(line_text)

    stripped_line = strip_ansi_codes(line_text).strip()

    if not stripped_line:
        return ""

    if stripped_line.startswith("---") or stripped_line.startswith("==="):
        content = stripped_line.replace('-', '').replace('=', '').strip()
        return f"\n---\n**{content}**"
    elif " Crew Execution Started " in stripped_line or " Task Output " in stripped_line:
        return f"\n**{stripped_line}**"

    if stripped_line.startswith("Thought:"):
        return f"**Thought:** {stripped_line[len('Thought:'):].strip()}"
    elif stripped_line.startswith("Tool Executing:"):
        tool_info = stripped_line[len('Tool Executing:'):].strip()
        return f"**Tool Executing:** `{tool_info}`"
    elif stripped_line.startswith("Final Answer:"):
        return f"**Final Answer:** {stripped_line[len('Final Answer:'):].strip()}"
    elif stripped_line.startswith("Observation:"):
        return f"**Observation:** {stripped_line[len('Observation:'):].strip()}"
    elif stripped_line.startswith("Action:"):
        return f"**Action:** {stripped_line[len('Action:'):].strip()}"
    elif stripped_line.startswith("Action Input:"):
        action_input = stripped_line[len('Action Input:'):].strip()
        return f"**Action Input:** `{action_input}`"
    elif stripped_line.startswith("Agent:"):
        return f"**Agent:** {stripped_line[len('Agent:'):].strip()}"
    elif stripped_line.startswith("Task:"):
        return f"**Task:** {stripped_line[len('Task:'):].strip()}"

    return stripped_line


class StreamCapture:
    """
    A custom stream object that captures stdout and puts it into a queue.
    It also writes to the original stdout so console output is preserved.
    """
    def __init__(self, queue_instance, original_stdout):
        self.queue = queue_instance
        self._original_stdout = original_stdout # The actual sys.stdout object
        self.buffer = ''

    def write(self, s):
        # Write to the original stdout first, so it appears in the console
        self._original_stdout.write(s)
        self._original_stdout.flush() # Ensure it's flushed to console immediately

        self.buffer += s
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            formatted_line = format_crewai_output_to_markdown(line)
            if formatted_line:
                self.queue.put(formatted_line + "\n") # Put into queue for main thread

    def flush(self):
        # When flush is called, put any remaining content in the buffer into the queue
        if self.buffer:
            formatted_line = format_crewai_output_to_markdown(self.buffer)
            if formatted_line:
                self.queue.put(formatted_line + "\n")
            self.buffer = ''
        self._original_stdout.flush() # Also flush the original stdout


def _run_crew_in_thread(location: str, niche: str, output_queue: queue.Queue, original_stdout):
    """
    Helper function to run the CrewAI process in a separate thread.
    Redirects stdout to capture verbose output and puts it into the queue.
    """
    # Create the Crew (must be done in the thread if agents/tasks are not thread-safe)
    market_research_crew = Crew(
        agents=[
            market_research_lead_agent,
            demographic_data_analyst_agent,
            niche_demand_analyst_agent
        ],
        tasks=[
            demographic_analysis_task,
            niche_demand_analysis_task,
            market_viability_report_task
        ],
        verbose=True,
        process=Process.sequential
    )

    # Store the thread's original stdout
    thread_original_stdout = sys.stdout
    # Redirect sys.stdout for this thread to our custom StreamCapture
    sys.stdout = StreamCapture(output_queue, original_stdout)

    try:
        # Kick off the crew with the user's input
        raw_result = market_research_crew.kickoff(inputs={'location': location, 'niche': niche})
        final_result = str(raw_result)

        # Flush any remaining output from the buffer
        sys.stdout.flush()

        # Put the final result into the queue
        final_result_text = strip_ansi_codes(final_result)
        output_queue.put(f"\n\n**FINAL RESULT:**\n```\n{final_result_text}\n```\n")

    except Exception as e:
        error_message = f"Error during CrewAI execution: {str(e)}\n"
        output_queue.put(ERROR_STREAM_MARKER + error_message)
        # Also print to the original stdout (console) directly
        original_stdout.write(f"\n--- Thread Error (Server Console) ---\n{error_message}\n")
        original_stdout.flush()
    finally:
        # Restore sys.stdout for this thread
        sys.stdout = thread_original_stdout
        # Signal the end of the stream
        output_queue.put(END_OF_STREAM_MARKER)


def run_market_research_crew(location: str, niche: str):
    """
    Executes the market research CrewAI process and yields its verbose output,
    formatted with Markdown, in real-time using threading.
    """
    output_queue = queue.Queue()
    # Pass the original sys.stdout object to the thread for console printing
    original_stdout = sys.stdout

    # Start the CrewAI process in a separate thread
    crew_thread = threading.Thread(
        target=_run_crew_in_thread,
        args=(location, niche, output_queue, original_stdout)
    )
    crew_thread.daemon = True # Allow main program to exit even if thread is running
    crew_thread.start()

    # Continuously yield from the queue until the end marker is received
    while True:
        try:
            # Use a timeout to prevent blocking indefinitely if the thread crashes
            item = output_queue.get(timeout=1) # Short timeout for responsiveness
            if item == END_OF_STREAM_MARKER:
                break
            elif item.startswith(ERROR_STREAM_MARKER):
                # If an error marker is received, yield the error message and break
                yield item[len(ERROR_STREAM_MARKER):]
                break
            else:
                yield item
        except queue.Empty:
            # If the queue is empty after timeout, check if the thread is still alive
            if not crew_thread.is_alive():
                # If thread died and queue is empty, something went wrong
                yield "Error: CrewAI thread terminated unexpectedly or timed out.\n"
                break
            # Otherwise, continue waiting (loop again)
            continue
        except Exception as e:
            yield f"Error in main stream consumer: {str(e)}\n"
            break

    # Ensure the thread has finished before exiting the generator
    # A small join timeout is good practice, but daemon thread means it won't block main exit.
    crew_thread.join(timeout=5)
    if crew_thread.is_alive():
        original_stdout.write("Warning: CrewAI thread did not terminate gracefully.\n")
        original_stdout.flush()

