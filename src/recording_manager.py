"""
Recording manager for capturing user actions.
"""
from tkinter import messagebox
from src.action_recorder import ActionRecorder, RecordingState
from src.recording_overlay import RecordingOverlay

class RecordingManager:
    def __init__(self, app):
        self.app = app
        self.action_recorder = None
        self.recording_overlay = None
        self.is_recording = False

    def start_recording(self):
        """Start recording mode"""
        if self.is_recording:
            return

        # Ask for confirmation
        if not messagebox.askyesno("Start Recording",
                                   "Start recording your actions?\n\n" +
                                   "All clicks, typing, and scrolling will be captured.\n" +
                                   "Press 'Stop' in the overlay when done."):
            return

        # Minimize main window
        self.app.root.iconify()

        # Create recorder
        self.action_recorder = ActionRecorder(
            self.app.screenshot_manager,
            on_action_recorded=self._on_action_recorded,
            on_state_change=self._on_recording_state_change
        )

        # Create overlay
        self.recording_overlay = RecordingOverlay(
            self.app.root,
            on_pause=self.pause_recording,
            on_resume=self.resume_recording,
            on_stop=self.stop_recording
        )
        self.recording_overlay.show()

        # Start recording after short delay
        self.app.root.after(1000, self._begin_recording)

        self.is_recording = True
        self.app.record_btn.config(state='disabled')
        self.app.update_status("Recording started...")

    def _begin_recording(self):
        """Begin actual recording (after delay)"""
        if self.action_recorder:
            self.action_recorder.start_recording()

    def pause_recording(self):
        """Pause recording"""
        if self.action_recorder and self.action_recorder.is_recording():
            self.action_recorder.pause_recording()
            if self.recording_overlay:
                self.recording_overlay.set_paused(True)

    def resume_recording(self):
        """Resume recording"""
        if self.action_recorder and self.action_recorder.is_paused():
            self.action_recorder.resume_recording()
            if self.recording_overlay:
                self.recording_overlay.set_paused(False)

    def stop_recording(self):
        """Stop recording and process captured actions"""
        if not self.is_recording or not self.action_recorder:
            return

        # Stop recording
        recorded_actions = self.action_recorder.stop_recording()

        # Destroy overlay
        if self.recording_overlay:
            self.recording_overlay.destroy()
            self.recording_overlay = None

        # Restore main window
        self.app.root.deiconify()
        self.app.root.lift()
        self.app.root.focus_force()

        # Add recorded actions to workflow
        if recorded_actions:
            for action in recorded_actions:
                self.app.actions.append(action)

            self.app._refresh_workflow()

            # Load first screenshot if this is the first set of actions
            if len(recorded_actions) > 0 and recorded_actions[0].has_visual_data():
                if not self.app.visual_canvas.has_screenshot():
                    from PIL import Image
                    try:
                        screenshot = Image.open(recorded_actions[0].visual.screenshot_path)
                        self.app.visual_canvas.load_screenshot(screenshot)
                    except:
                        pass

            # Add all annotations
            for i, action in enumerate(self.app.actions):
                if action.has_visual_data():
                    self.app._add_canvas_annotation(action, i)

            messagebox.showinfo("Recording Complete",
                              f"Recorded {len(recorded_actions)} action{'s' if len(recorded_actions) != 1 else ''}!\n\n" +
                              "Actions have been added to your workflow.")

            self.app.update_status(f"Recording complete: {len(recorded_actions)} actions added")
        else:
            messagebox.showinfo("Recording Complete", "No actions were recorded.")
            self.app.update_status("Recording stopped (no actions)")

        # Cleanup
        self.is_recording = False
        self.action_recorder = None
        self.app.record_btn.config(state='normal')

    def _on_action_recorded(self, action):
        """Callback when action is recorded"""
        if self.recording_overlay:
            count = self.action_recorder.get_recorded_count()
            self.recording_overlay.update_count(count)

    def _on_recording_state_change(self, state):
        """Callback when recording state changes"""
        pass
