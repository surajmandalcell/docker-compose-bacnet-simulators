import os
import sys
import curses
import subprocess
import signal

IGNORE_LIST = ['.git', 'venv', '__pycache__', 'node_modules', '.vscode', '_scripts']

def get_folders(root_dir='.'):
    return [d for d in os.listdir(root_dir) 
            if os.path.isdir(os.path.join(root_dir, d)) and d not in IGNORE_LIST]

def draw_menu(stdscr, selected_row_idx, folders):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    # Draw title
    title = "Select simulator"
    stdscr.attron(curses.color_pair(2))
    stdscr.addstr(1, 2, title)
    stdscr.attroff(curses.color_pair(2))
    stdscr.addstr(2, 2, "=" * len(title))

    # Draw folders
    for idx, folder in enumerate(folders):
        y = 4 + idx
        x = 2
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, f"> {folder}")
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, f"  {folder}")
    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    folders = get_folders()
    current_row = 0

    while True:
        draw_menu(stdscr, current_row, folders)
        try:
            key = stdscr.getch()
        except KeyboardInterrupt:
            return None  # Handle Ctrl+C

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(folders) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            selected_folder = folders[current_row]
            return selected_folder

def signal_handler(sig, frame):
    print("\nCtrl+C pressed. Exiting gracefully.")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    selected_folder = curses.wrapper(main)
    if selected_folder:
        gui_path = os.path.join(selected_folder, 'gui.py')
        if os.path.exists(gui_path):
            try:
                subprocess.run([sys.executable, gui_path])
            except KeyboardInterrupt:
                print("\nCtrl+C pressed. Exiting gracefully.")
        else:
            print(f"No gui.py found in {selected_folder}")
    else:
        print("No folder selected. Exiting.")