import tkinter as tk
import random
import keras
import numpy

# load images for display
mnist = keras.datasets.mnist
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()
images = train_images
len_images = len(images)

# Constants for grid dimensions and initial click value
GRID_ROWS, GRID_COLS = 28, 28
INITIAL_GRID_VALUE = 0 # Black
INITIAL_CLICK_VALUE = 255  # White


# Helper function to convert a grayscale value to a hex color string
def gray_to_hex(gray_value):
    hex_value = '{:02x}'.format(gray_value)
    return f'#{hex_value}{hex_value}{hex_value}'

class GridEditor:
    def __init__(self, initial=None, prediction_callback=None, models=None):
        self.master = tk.Tk()
        if initial is None:
            self.grid = [[INITIAL_GRID_VALUE for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        else:
            self.grid = initial
        self.label_grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.click_value = INITIAL_CLICK_VALUE
        self.last_pos = None
        self.prediction_callback = prediction_callback
        self.models = models # dict of model_name: model
        self.create_widgets()
        self.create_controls()
        self.bind_events()
        self.master.mainloop()

    ### INITIAL SETUP ###
    def create_controls(self):
        # Row 1
        buttons_row_1 = {
            "Set All": self.set_random_example,
            "Invert": self.invert_grid,
            "Randomize": self.randomize_grid,
            "Reset": self.reset_grid,
            "Predict": self.update_predictions
        }
        num_buttons_row_1 = len(buttons_row_1)
        for i, (name, fun) in enumerate(buttons_row_1.items()):
            tk.Button(self.master, text=name, command=fun).grid(row=GRID_ROWS, column=((i * GRID_COLS) // num_buttons_row_1), columnspan=GRID_COLS // num_buttons_row_1)

        # Row 2
        buttons_row_2 = {
            "Update Click Value": self.update_click_value,
            "Random Example": self.set_random_example,
        }
        num_buttons_row_2 = len(buttons_row_2) + 1 # account for click value widget
        for i, (name, fun) in enumerate(buttons_row_2.items()): # i + 1 to account for click value widget
            tk.Button(self.master, text=name, command=fun).grid(row=GRID_ROWS + 1, column=(((i + 1) * GRID_COLS) // num_buttons_row_2), columnspan=GRID_COLS // num_buttons_row_2)

        
        #tk.Button(self.master, text='Random Example', command=self.set_random_example).grid(row=GRID_ROWS, column=0, columnspan=GRID_COLS//4)
        #tk.Button(self.master, text='Set All', command=self.set_click_value).grid(row=GRID_ROWS, column=0, columnspan=GRID_COLS//4)
        #tk.Button(self.master, text='Invert', command=self.invert_grid).grid(row=GRID_ROWS, column=GRID_COLS//4, columnspan=GRID_COLS//4)
        #tk.Button(self.master, text='Random', command=self.randomize_grid).grid(row=GRID_ROWS, column=(2*GRID_COLS)//4, columnspan=GRID_COLS//4)
        #tk.Button(self.master, text='Reset', command=self.reset_grid).grid(row=GRID_ROWS, column=(3*GRID_COLS)//4, columnspan=GRID_COLS//4)
        #tk.Button(self.master, text='Predict', command=self.update_predictions).grid(row=GRID_ROWS+2, column=GRID_COLS//4, columnspan=GRID_COLS//2)
        #tk.Button(self.master, text='Update Click Value', command=self.update_click_value).grid(row=GRID_ROWS+2, column=GRID_COLS//2, columnspan=GRID_COLS//2)

    def create_widgets(self):
        for i in range(GRID_ROWS):
            for j in range(GRID_COLS):
                label = tk.Label(self.master, bg=gray_to_hex(self.grid[i][j]), width=2, height=1)
                label.grid(row=i, column=j)
                label.pos = (i, j)
                self.label_grid[i][j] = label

        # Info Widget
        self.info_label = tk.Label(self.master, text="")
        self.info_label.grid(row=GRID_ROWS+2, column=0, columnspan=GRID_COLS)

        # Click Value Widget
        self.click_value_entry = tk.Entry(self.master, width=15)
        self.click_value_entry.grid(row=GRID_ROWS+1, column=0, columnspan=GRID_COLS//2)
        self.click_value_entry.insert(0, str(self.click_value))

        # Prediction Widgets
        if self.models and self.prediction_callback:
            self.model_labels = []
            for i in range(len(self.models)):
                self.model_labels.append(tk.Label(self.master, text=""))
                self.model_labels[i].grid(row=0 + i, column=GRID_COLS, columnspan=GRID_COLS)

    def bind_events(self):
        self.master.bind('<Button-1>', self.on_press)
        self.master.bind('<B1-Motion>', self.on_drag)
        self.master.bind('<Motion>', self.update_info)

    ### Functions
    def set_random_example(self):
        image_idx = random.randint(0, len_images - 1)
        image = images[image_idx]
        for i in range(GRID_ROWS):
            for j in range(GRID_COLS):
                self.grid[i][j] = image[i][j]
                self.label_grid[i][j].configure(bg=gray_to_hex(image[i][j]))

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

    def update_predictions(self):
        self.models = self.prediction_callback(self.grid)
        for i, (model_name, predictions) in enumerate(self.models.items()):
            prediction_string = f"{model_name}: "
            for digit, prediction in predictions.items():
                term = "" if digit == list(predictions.keys())[-1] else ", "
                prediction_string += f"{digit} ({prediction}){term}"
            self.model_labels[i].configure(text=prediction_string)

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

import random
from collections import OrderedDict

def create_random_dict():
    # Generate 9 random float values between 0 and 1
    values = [random.random() for _ in range(9)]
    
    # Add the value 0 at the end to complete the list
    values.append(0.0)
    
    # Calculate the sum of these random values
    total = sum(values)
    
    # Normalize the values so they sum to 1.0
    values = [ round(v / total, 2) for v in values ]
    
    # Shuffle the digits 0-9
    keys = list(range(10))
    random.shuffle(keys)
    
    # Create the dictionary with keys and values
    my_dict = dict(zip(keys, values))
    
    # Sort the dictionary by values in descending order
    ordered_dict = OrderedDict(sorted(my_dict.items(), key=lambda item: item[1], reverse=True))
    
    return ordered_dict

def main():
    models = {
        "model 1": create_random_dict(),
        "model 2": create_random_dict()
    }
    GridEditor(models=models, prediction_callback=create_random_dict)

if __name__ == "__main__":
    main()
