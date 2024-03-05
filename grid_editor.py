import tkinter as tk
import random

# Constants for grid dimensions and initial click value
GRID_ROWS, GRID_COLS = 28, 28
INITIAL_GRID_VALUE = 0 # Black
INITIAL_CLICK_VALUE = 255  # White

# Helper function to convert a grayscale value to a hex color string
def gray_to_hex(gray_value):
    hex_value = '{:02x}'.format(gray_value)
    return f'#{hex_value}{hex_value}{hex_value}'

class GridEditor:
    def __init__(self, master, initial=None):
        self.master = master
        if initial is None:
            self.grid = [[INITIAL_GRID_VALUE for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        else:
            self.grid = initial
        self.label_grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.click_value = INITIAL_CLICK_VALUE
        self.last_pos = None
        self.create_widgets()
        self.bind_events()

    def create_widgets(self):
        for i in range(GRID_ROWS):
            for j in range(GRID_COLS):
                label = tk.Label(self.master, bg=gray_to_hex(self.grid[i][j]), width=2, height=1)
                label.grid(row=i, column=j)
                label.pos = (i, j)
                self.label_grid[i][j] = label

        self.info_label = tk.Label(self.master, text="")
        self.info_label.grid(row=GRID_ROWS+1, column=0, columnspan=GRID_COLS)

        self.create_controls()

    def create_controls(self):
        tk.Button(self.master, text='Set All', command=self.set_click_value).grid(row=GRID_ROWS, column=0, columnspan=GRID_COLS//4)
        tk.Button(self.master, text='Invert', command=self.invert_grid).grid(row=GRID_ROWS, column=GRID_COLS//4, columnspan=GRID_COLS//4)
        tk.Button(self.master, text='Random', command=self.randomize_grid).grid(row=GRID_ROWS, column=(2*GRID_COLS)//4, columnspan=GRID_COLS//4)
        tk.Button(self.master, text='Reset', command=self.reset_grid).grid(row=GRID_ROWS, column=(3*GRID_COLS)//4, columnspan=GRID_COLS//4)
        
        self.click_value_entry = tk.Entry(self.master, width=15)
        self.click_value_entry.grid(row=GRID_ROWS+2, column=0, columnspan=GRID_COLS//2)
        self.click_value_entry.insert(0, str(self.click_value))
        tk.Button(self.master, text='Update Click Value', command=self.update_click_value).grid(row=GRID_ROWS+2, column=GRID_COLS//2, columnspan=GRID_COLS//2)

    def flip_color(self, label):
        i, j = label.pos
        # we want to create a brush effect to make it easier to paint
        # immediate surrounding pixels are a lighter value
        inner_ring_color = (self.click_value // 5)

        # Update surrounding pixels
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                new_i, new_j = i + di, j + dj
                # Check bounds
                if 0 <= new_i < GRID_ROWS and 0 <= new_j < GRID_COLS:
                    # Determine color based on distance from the center
                    if di == 0 and dj == 0:
                        # Center pixel
                        self.grid[new_i][new_j] = self.click_value
                    else:
                        # Surrounding pixels
                        self.grid[new_i][new_j] += inner_ring_color
                        if self.grid[new_i][new_j] > 255:
                            self.grid[new_i][new_j] = 255

                    
                    # Update the label color
                    self.label_grid[new_i][new_j].configure(bg=gray_to_hex(self.grid[new_i][new_j]))


    def on_press(self, event):
        widget = self.master.winfo_containing(event.x_root, event.y_root)
        if widget and hasattr(widget, 'pos'):
            self.flip_color(widget)
            self.last_pos = widget.pos

    def on_drag(self, event):
        widget = self.master.winfo_containing(event.x_root, event.y_root)
        if widget and hasattr(widget, 'pos') and widget.pos != self.last_pos:
            self.flip_color(widget)
            self.last_pos = widget.pos

    def update_info(self, event):
        widget = self.master.winfo_containing(event.x_root, event.y_root)
        if widget and isinstance(widget, tk.Label) and hasattr(widget, 'pos'):
            self.info_label.configure(text=f"Row: {widget.pos[0]}, Column: {widget.pos[1]}, Value: {self.grid[widget.pos[0]][widget.pos[1]]}")

    def set_click_value(self):
        for i in range(GRID_ROWS):
            for j in range(GRID_COLS):
                self.grid[i][j] = self.click_value
                self.label_grid[i][j].configure(bg=gray_to_hex(self.grid[i][j]))

    def reset_grid(self):
        for i in range(GRID_ROWS):
            for j in range(GRID_COLS):
                self.grid[i][j] = INITIAL_GRID_VALUE
                self.label_grid[i][j].configure(bg=gray_to_hex(INITIAL_GRID_VALUE))


    def invert_grid(self):
        for i in range(GRID_ROWS):
            for j in range(GRID_COLS):
                self.grid[i][j] = 255 - self.grid[i][j]
                self.label_grid[i][j].configure(bg=gray_to_hex(self.grid[i][j]))

    def randomize_grid(self):
        for i in range(GRID_ROWS):
            for j in range(GRID_COLS):
                self.grid[i][j] = random.randint(0, 255)
                self.label_grid[i][j].configure(bg=gray_to_hex(self.grid[i][j]))

    def update_click_value(self):
        try:
            value = int(self.click_value_entry.get())
            if 0 <= value <= 255:
                self.click_value = value
            else:
                self.set_entry_error('Invalid value')
        except ValueError:
            self.set_entry_error('Invalid value')

    def set_entry_error(self, message):
        self.click_value_entry.delete(0, 'end')
        self.click_value_entry.insert(0, message)

    def bind_events(self):
        self.master.bind('<Button-1>', self.on_press)
        self.master.bind('<B1-Motion>', self.on_drag)
        self.master.bind('<Motion>', self.update_info)

def draw_number(initial=None):
    root = tk.Tk()
    app = GridEditor(root, initial)
    root.mainloop()
    return app.grid

def main():
    draw_number()

if __name__ == "__main__":
    main()