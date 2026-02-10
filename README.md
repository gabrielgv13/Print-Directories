# Print-Directories

A Python tool built with **Dear PyGui** to visualize and capture clean screenshots of Windows directory structures.

## Features
- **Visual File Tree**: Displays folders and files with high-fidelity icons and type-based coloring.
- **Smart Sorting**: Groups directories first, then groups files by extension (alphabetical).
- **Clean Screenshots**: High-fidelity capture that hides all UI elements and window controls, leaving only the file tree on a premium dark background.
- **Full Path Toggle**: Quickly switch the display between the folder name or the absolute path.
- **Native Browser**: Uses the Windows directory picker for easy navigation.
- **Filtered**: Automatically ignores hidden folders like `.venv`.

## How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the App**:
   ```bash
   python main.py
   ```

## Usage
- Click **Browse** to select a directory.
- Click **Visualize** to generate the tree.
- Use **Show Full Path** to toggle the top label.
- Click **Save Clean Screenshot** to generate a `directory_structure.png` file in the root folder.
