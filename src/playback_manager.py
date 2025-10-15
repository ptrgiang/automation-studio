"""
Playback manager for executing workflows.
"""
from tkinter import messagebox
from src.executor import SimulationExecutor
from src.action_schema import ActionSchemaManager
from src.execution_popup import ExecutionPopup
from pynput import keyboard
import threading

class PlaybackManager:
    def __init__(self, app):
        self.app = app

    def play_workflow(self):
        """Play workflow with a transparent popup for status."""
        if not self.app.actions:
            messagebox.showwarning("No Actions", "No actions to play.")
            return

        is_batch = any('{batch:' in str(action.params.get('text', '')) or '{batch:' in str(action.params.get('value', '')) for action in self.app.actions if action.enabled)

        if is_batch and not self.app.batch_data:
            messagebox.showwarning("No Batch Data", "Workflow requires batch data. Please add data via 'Edit > Manage Variables'.")
            return

        # --- Setup for execution ---
        self.app.root.withdraw()
        popup = ExecutionPopup(self.app.root)
        popup.show()

        stop_execution = False
        pause_execution = False

        def on_press(key):
            nonlocal stop_execution, pause_execution
            try:
                if key.char == 's':
                    stop_execution = True
                elif key.char == 'p':
                    pause_execution = not pause_execution
            except AttributeError:
                pass

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

        def stop_callback():
            return stop_execution

        def pause_callback():
            return pause_execution

        def progress_callback(current_step, next_step):
            self.app.root.after(0, popup.update_progress, current_step, next_step)

        executor = SimulationExecutor(
            stop_callback=stop_callback,
            pause_callback=pause_callback,
            status_callback=lambda msg: self.app.root.after(0, self.app.update_status, msg),
            progress_callback=progress_callback
        )

        def execution_target():
            try:
                classic_actions = ActionSchemaManager.export_simulation(self.app.actions, include_visual=False)
                if is_batch:
                    executor.execute_batch(classic_actions, self.app.batch_data)
                else:
                    executor.execute_simulation(classic_actions)
            finally:
                listener.stop()
                self.app.root.after(0, popup.destroy)
                self.app.root.after(0, self.app.root.deiconify)

        thread = threading.Thread(target=execution_target)
        thread.daemon = True
        thread.start()
