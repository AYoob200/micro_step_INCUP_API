"""
Tkinter Desktop UI for the Dopamine Coach Decomposition Agent (Gemini).
Run this file to open a native desktop window.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
from decomposition_agent import DecompositionAgent


def process_request():
    user_input = input_text.get("1.0", tk.END).strip()
    if not user_input:
        messagebox.showwarning("Warning", "Please enter an intention.")
        return

    # Disable button and update status
    process_btn.config(state=tk.DISABLED)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, "Processing... Please wait a moment.")

    def run_agent():
        try:
            agent = DecompositionAgent()
            result = agent.decompose(user_input)
            json_output = result.to_json()

            # Update UI from the main thread
            root.after(0, update_output, json_output, None)
        except Exception as e:
            root.after(0, update_output, None, str(e))

    # Run in a separate thread so the UI doesn't freeze
    threading.Thread(target=run_agent, daemon=True).start()


def update_output(result, error):
    process_btn.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    if error:
        output_text.insert(tk.END, f"Error:\n{error}")
    else:
        output_text.insert(tk.END, result)


# Build the main Tkinter window
root = tk.Tk()
root.title("🧠 Dopamine Coach: Task Decomposition Engine (Gemini)")
root.geometry("800x600")

main_frame = ttk.Frame(root, padding="15")
main_frame.pack(fill=tk.BOTH, expand=True)

# Input Section
ttk.Label(main_frame, text="User Intention:", font=("Helvetica", 10, "bold")).pack(
    anchor=tk.W, pady=(0, 5)
)
input_text = tk.Text(main_frame, height=5, wrap=tk.WORD, font=("Helvetica", 11))
input_text.pack(fill=tk.X, pady=(0, 10))
input_text.insert("1.0", "I need to redesign my database schema for better performance")

# Button
process_btn = ttk.Button(
    main_frame, text="Generate JSON Output", command=process_request
)
process_btn.pack(pady=(0, 10), ipadx=10, ipady=5)

# Output Section
ttk.Label(
    main_frame, text="Decomposition Output (JSON):", font=("Helvetica", 10, "bold")
).pack(anchor=tk.W, pady=(0, 5))

# Add scrollbar to output text
output_frame = ttk.Frame(main_frame)
output_frame.pack(fill=tk.BOTH, expand=True)

output_scroll = ttk.Scrollbar(output_frame)
output_scroll.pack(side=tk.RIGHT, fill=tk.Y)

output_text = tk.Text(
    output_frame, wrap=tk.WORD, font=("Courier", 10), yscrollcommand=output_scroll.set
)
output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
output_scroll.config(command=output_text.yview)

if __name__ == "__main__":
    root.mainloop()