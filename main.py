import dearpygui.dearpygui as dpg
import pathlib
import os
import tkinter as tk
from tkinter import filedialog

def get_file_icon(path: pathlib.Path):
    """Returns an emoji icon and color for a given file path."""
    suffix = path.suffix.lower()
    
    # Colors (RGB)
    COLOR_DEFAULT = (200, 200, 220)
    COLOR_PYTHON = (75, 150, 230) # Blue
    COLOR_IMAGE = (180, 100, 255) # Purple
    COLOR_DATA = (100, 220, 120)  # Green
    COLOR_WEB = (240, 200, 80)   # Yellow
    
    if suffix == '.py':
        return "🐍", COLOR_PYTHON
    elif suffix in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.webp']:
        return "🖼️", COLOR_IMAGE
    elif suffix in ['.json', '.xml', '.yaml', '.yml', '.toml']:
        return "{}", COLOR_DATA
    elif suffix in ['.html', '.css', '.js', '.ts']:
        return "🌐", COLOR_WEB
    elif suffix in ['.txt', '.md', '.rst']:
        return "📝", COLOR_DEFAULT
    elif suffix in ['.ods', '.xlsx', '.csv', '.xls']:
        return "📊", COLOR_DATA
    elif suffix in ['.zip', '.rar', '.7z', '.tar', '.gz']:
        return "📦", (180, 180, 180)
    elif suffix == '.pdf':
        return "📕", (230, 80, 80)
    elif suffix in ['.exe', '.bat', '.ps1']:
        return "⚙️", (160, 160, 160)
    
    return "📄", COLOR_DEFAULT

def sanitize_text(text):
    """Sanitizes text to avoid issues with Dear PyGui's internal text rendering."""
    try:
        return text.replace('\x00', '')
    except:
        return "?"

def build_tree(path: pathlib.Path, visited=None):
    """Recursively builds the file tree using Dear PyGui's container stack."""
    if visited is None:
        visited = set()
    
    # Avoid infinite loops / circular symlinks
    try:
        resolved = path.resolve()
        if resolved in visited: return
        visited.add(resolved)
    except:
        pass

    try:
        if not path.is_dir():
            return

        try:
            items = list(path.iterdir())
        except PermissionError:
            dpg.add_text("🚫 Access Denied", color=(255, 50, 50))
            return

        # Filter hidden folders (starting with dot)
        items = [i for i in items if not i.name.startswith('.')]

        # Sort: Directories first, then Files by extension, then Alphabetical
        items.sort(key=lambda x: (x.is_file(), x.suffix.lower() if x.is_file() else "", x.name.lower()))

        for item in items:
            try:
                if item.is_dir():
                    # Using context manager 'with' handles parentage automatically via stack
                    with dpg.tree_node(label=sanitize_text(f"📁 {item.name}"), default_open=True):
                        build_tree(item, visited)
                else:
                    icon, color = get_file_icon(item)
                    label = sanitize_text(f"{icon}  {item.name}")
                    dpg.add_text(label, color=color)
            except Exception as e:
                print(f"Error adding item {item}: {e}")

    except Exception as e:
        dpg.add_text(f"⚠️ Error: {str(e)}", color=(255, 50, 50))

def refresh_view(sender, app_data, user_data):
    """Callback to refresh the file tree based on the input path."""
    path_str = dpg.get_value("path_input")
    show_full_path = dpg.get_value("full_path_toggle")
    container = "tree_container"
    
    # Clear existing children
    dpg.delete_item(container, children_only=True)
    
    if not path_str:
        dpg.add_text("Please enter a valid path.", parent=container)
        return

    path = pathlib.Path(path_str)
    
    if not path.exists():
        dpg.add_text(f"Path does not exist: {path_str}", parent=container, color=(255, 50, 50))
        return
        
    if not path.is_dir():
        dpg.add_text(f"Path is not a directory: {path_str}", parent=container, color=(255, 50, 50))
        return

    # Set up the top-level group inside the container to start the recursion
    with dpg.group(parent=container):
        display_name = str(path.resolve()) if show_full_path else path.name
        dpg.add_text(f"📂 {display_name}", color=(120, 200, 255)) # Slightly different color for root
        dpg.add_separator()
        build_tree(path)

def open_dir_dialog(sender, app_data, user_data):
    """Opens a native Windows directory selection dialog."""
    try:
        root = tk.Tk()
        root.withdraw() 
        root.attributes('-topmost', True)
        path = filedialog.askdirectory(mustexist=True)
        root.destroy()
        
        if path:
            dpg.set_value("path_input", path)
            refresh_view(None, None, None)
    except Exception as e:
        print(f"Dialog Error: {e}")

def restore_ui():
    """Restores UI elements after a screenshot."""
    dpg.configure_item("controls_group", show=True)
    dpg.configure_item("screenshot_button", show=True)
    dpg.configure_item("status_text", show=True)
    dpg.configure_item("app_header", show=True)

def take_screenshot():
    """Takes a ultra-clean screenshot by hiding all UI and waiting for render frames."""
    # 1. Hide everything
    dpg.configure_item("controls_group", show=False)
    dpg.configure_item("screenshot_button", show=False)
    dpg.configure_item("status_text", show=False)
    dpg.configure_item("app_header", show=False)
    if dpg.does_item_exist("main_sep"): 
        dpg.configure_item("main_sep", show=False)
    
    # 2. Define the capture step (runs 2 frames later to ensure UI is hidden in GPU buffer)
    def capture_step():
        output_file = "directory_structure.png"
        dpg.output_frame_buffer(file=output_file)
        
        # 3. Define the restore step (runs 2 frames after capture)
        def restore_step():
            restore_ui()
            if dpg.does_item_exist("main_sep"): 
                dpg.configure_item("main_sep", show=True)
            dpg.set_value("status_text", f"Clean screenshot saved to {output_file}")

        dpg.set_frame_callback(dpg.get_frame_count() + 2, callback=restore_step)

    # Start the sequence
    dpg.set_frame_callback(dpg.get_frame_count() + 2, callback=capture_step)


# DPG Context Setup
dpg.create_context()

# Theme
with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (25, 25, 30), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, (220, 220, 230), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Header, (40, 40, 50), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8, category=dpg.mvThemeCat_Core)

dpg.bind_theme(global_theme)

with dpg.window(tag="Primary Window"):
    dpg.add_text("Directory Visualizer", tag="app_header", color=(100, 200, 255))
    
    with dpg.group(tag="controls_group"):
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="path_input", default_value=os.getcwd(), width=500, hint="Enter directory path...")
            dpg.add_button(label="Browse...", callback=open_dir_dialog)
            dpg.add_button(label="Visualize", callback=refresh_view)
        
        with dpg.group(horizontal=True):
            dpg.add_checkbox(label="Show Full Path", tag="full_path_toggle", default_value=False, callback=refresh_view)
            dpg.add_text(" (Toggle to change directory display name)", color=(150, 150, 150))

    dpg.add_button(label="📸 Save Clean Screenshot", tag="screenshot_button", callback=take_screenshot)
    dpg.add_text("", tag="status_text", color=(100, 255, 100))
    
    dpg.add_separator(tag="main_sep")
    
    # Scrollable container for the tree
    with dpg.child_window(tag="tree_container", border=False, autosize_x=True, autosize_y=True):
        dpg.add_text("Enter a path and click Visualize to see the structure.", color=(150, 150, 150))

dpg.create_viewport(title='Directory Visualizer', width=900, height=700)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)

# Initial load
refresh_view(None, None, None)

dpg.start_dearpygui()
dpg.destroy_context()
