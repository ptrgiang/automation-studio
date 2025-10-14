# Automation Studio v2

**Visual automation tool for repetitive GUI tasks across any application**

Automate repetitive tasks in any desktop application with powerful recording and playback capabilities. Record your actions once, replay unlimited times.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python automation_studio.py
```

## ✨ Features

- **🎬 Action Recording** - Record mouse clicks, keyboard input, scrolling, and more
- **🖼️ Image Recognition** - Find and interact with UI elements using template matching
- **📦 Batch Processing** - Process multiple variables automatically from a list
- **💾 Save & Reuse** - Save simulations as JSON files for repeated use
- **🎨 Professional UI** - Modern, intuitive interface with tree view and status indicators
- **⚡ Fast & Reliable** - Efficient execution with safety features (ESC to stop)
- **🔧 Modular Architecture** - Clean, maintainable codebase

## 📸 Screenshots

### Professional UI
- Modern blue/gray theme
- Tree view with action details
- Menu bar and toolbar
- Status bar with progress indicators
- Built-in Variable manager

## 🎯 Use Cases

- **Form Filling** - Batch update forms with different data
- **Data Entry** - Automate repetitive data input tasks
- **Application Testing** - Perform repeated UI interactions
- **System Administration** - Automate routine desktop tasks
- **Quality Checks** - Verify application functionality systematically

## 📋 Action Types

| Action | Description |
|--------|-------------|
| **Click** | Click at specific coordinates or current position |
| **Type** | Type text with variable substitution ({VARIABLE}) |
| **Set Value** | Click, clear, and type in one action |
| **Delete** | Clear field contents (ctrl+a, backspace, triple-click) |
| **Scroll** | Scroll by amount or to top/bottom |
| **Wait** | Pause for duration or wait for image to appear |
| **Find Image** | Locate UI element using image recognition |
| **Move Mouse** | Relative mouse movement in any direction |

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Architecture overview and technical documentation
- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Developer reference and examples
- **[BUTTON_STYLES_GUIDE.md](BUTTON_STYLES_GUIDE.md)** - UI styling reference

## 🏗️ Architecture

### Modular Design

```
automation_studio.py     # Main application entry point
src/
├── studio_layout.py       # Main UI layout and panels
├── action_card.py         # UI for individual action cards
├── visual_canvas.py       # Canvas for displaying screenshots and annotations
├── property_editor.py     # Panel for editing action properties
├── action_schema.py       # Data models for actions
├── screenshot_manager.py  # Handles screenshotting and file management
├── capture_overlay.py     # Overlay for capturing screen regions
├── action_recorder.py     # Logic for recording user actions
├── executor.py            # Engine for playing back workflows
├── theme.py               # UI styling and icons
├── workflow_templates.py  # Manages workflow templates
└── workflow_comments.py   # Manages comments on actions
```

### Professional Features

- Modern design with tree view action list
- Full menu bar and toolbar
- Enhanced multi-field dialogs
- Status bar with progress indicators
- Built-in Variable manager
- Keyboard shortcuts for all actions
- Double-click actions for details

## 🔧 Requirements

```
pyautogui==0.9.54
pillow==10.4.0
opencv-python==4.10.0.84
pytesseract==0.3.13
```

**Optional:**
- Tesseract OCR (not currently used but dependency installed)

## 💡 Basic Usage

### Recording a Simulation

1. Launch the application
2. Click action buttons to record steps
3. For image-based actions, position mouse and wait for capture
4. Save simulation to JSON file

### Playing Back

**Single Variable:**
1. Load simulation
2. Click "Play Single"
3. Enter variable
4. Watch automation run

**Batch Processing:**
1. Manage variables (File → Manage Variables)
2. Add variables to list
3. Load simulation
4. Click "Play Batch"
5. Press ESC to stop anytime

### Variable Substitution

Use `{VARIABLE}` placeholder in Type and Set Value actions:
- Single play: Replaced with entered variable
- Batch play: Replaced with each variable from list

## ⚙️ Configuration

**config.json:**
```json
{
  "pause_between_actions": 1.0,
  "typing_interval": 0.1,
  "scroll_amount": -300,
  "screenshot_on_error": true,
  "max_retries": 3
}
```

## 🛡️ Safety Features

- **FAILSAFE** - Move mouse to corner to abort
- **ESC Key** - Stop simulation gracefully
- **Always on Top** - Keep control window accessible
- **Enable/Disable Steps** - Skip actions without deletion
- **Visual Feedback** - Status updates for all operations

## ⌨️ Keyboard Shortcuts

- **Ctrl+O** - Open simulation
- **Ctrl+S** - Save simulation
- **Ctrl+Z** - Undo last action
- **Ctrl+Q** - Quit application
- **ESC** - Stop simulation
- **Enter** - Submit dialog
- **ESC** - Cancel dialog

## 🎨 Customization

### Change Theme Colors

Edit `src/theme.py`:
```python
class ModernTheme:
    PRIMARY = "#2563eb"      # Your color
    SUCCESS = "#10b981"      # Your color
    # etc.
```

### Add Custom Actions

1. Define dataclass in `src/actions.py`
2. Add recorder method in `src/recorder.py`
3. Add executor method in `src/executor.py`
4. Wire up in main application

See `DEVELOPER_GUIDE.md` for detailed instructions.

## 🐛 Troubleshooting

### Import Errors
```bash
# Ensure running from project root
cd automation-studio
python automation_studio.py
```

### PyAutoGUI Issues
- Enable FAILSAFE (move mouse to corner)
- Increase wait times between actions
- Verify screen resolution matches recordings

### Image Recognition Fails
- Lower confidence threshold (0.7 instead of 0.9)
- Recapture template in current resolution
- Ensure target is visible on screen

## 📊 Performance

- **Startup:** Instant
- **Recording:** Real-time, no lag
- **Playback:** Determined by wait times
- **File I/O:** Fast, JSON-based
- **UI:** Responsive, threaded execution

## 🤝 Contributing

This is a professional automation tool. When extending:
- Follow modular architecture
- Use type hints
- Document new features
- Test thoroughly before batch operations
- Respect separation of concerns

## ⚠️ Disclaimer

This tool automates interactions with desktop applications. Use responsibly:
- Test simulations thoroughly before batch operations
- Monitor first few executions
- Have fallback plans
- Don't rely solely on automation for critical operations

## 📜 License

This project is for automation and productivity purposes. Use at your own discretion.

## 🎓 Learning Resources

- **Python Tkinter** - GUI framework
- **PyAutoGUI** - Automation library
- **OpenCV** - Image processing
- **Design Patterns** - Modular architecture

## 📞 Support

For questions or issues:
1. Check documentation files
2. Review inline code comments
3. Check `simulation_gui.log` for errors
4. Consult `DEVELOPER_GUIDE.md` for examples

---

**Made with ❤️ for users who value their time**
