import tkinter as tk
import random

color_change_interval = 0.1
interval_label = None
interval_fade_step = 0
increase_mode = True

def create_random_grid(size):
    return [[random.choice([i/10 for i in range(11)]) for _ in range(size)] for _ in range(size)]

def color_mapping(value):
    gray_scale = int(value * 255)
    return f'#{gray_scale:02x}{gray_scale:02x}{gray_scale:02x}'


def draw_grid(canvas, grid, square_size):
    for i, row in enumerate(grid):
        for j, value in enumerate(row):
            color = color_mapping(value)
            rectangle = canvas.create_rectangle(j * square_size, i * square_size,
                                                (j + 1) * square_size, (i + 1) * square_size,
                                                fill=color)
            canvas.tag_bind(rectangle, '<Button-1>', lambda event, i=i, j=j: on_square_click(event, canvas, grid, i, j, square_size))
            canvas.tag_bind(rectangle, '<B1-Motion>', lambda event, i=i, j=j: on_square_drag(event, canvas, grid, square_size))
    canvas.bind('<Key>', lambda event: process_key(event, canvas, grid, square_size))
    canvas.focus_set()

def process_key(event, canvas, grid, square_size):
    global color_change_interval
    global increase_mode
    if event.keysym == 'Escape':
        canvas.master.quit()
    elif event.keysym.lower() == 'b':
        set_grid_color(canvas, grid, square_size, "black")
    elif event.keysym.lower() == 'w':
        set_grid_color(canvas, grid, square_size, "white")
    elif event.keysym.lower() == 't':
        increase_mode = not increase_mode
        show_interval_label(canvas, square_size)
    elif event.keysym == 'minus':
        color_change_interval = max(color_change_interval - 0.1, 0.1)
        show_interval_label(canvas, square_size)
    elif event.keysym == 'equal':
        color_change_interval = min(color_change_interval + 0.1, 1.0)
        show_interval_label(canvas, square_size)

def show_interval_label(canvas, square_size):
    global interval_label
    global interval_fade_step
    global increase_mode
    global color_change_interval
    if interval_label:
        canvas.delete(interval_label)
    interval_fade_step = 0
    interval_label_text = f"{'Increase' if increase_mode else 'Decrease'}: {color_change_interval:.1f}"
    interval_label = canvas.create_text(canvas.winfo_width() - 5, 5, text=interval_label_text, anchor=tk.NE, font=("Arial", 12))
    fade_interval_label(canvas)


def fade_interval_label(canvas):
    global interval_label
    global interval_fade_step
    if interval_fade_step < 10:
        interval_fade_step += 1
        fade_color = f"#{255 - interval_fade_step * 25:02x}{255 - interval_fade_step * 25:02x}{255 - interval_fade_step * 25:02x}"
        canvas.itemconfig(interval_label, fill=fade_color)
        canvas.after(300, lambda: fade_interval_label(canvas))


def set_grid_color(canvas, grid, square_size, color):
    global interval_label
    for i, row in enumerate(grid):
        for j, value in enumerate(row):
            grid[i][j] = 1.0 if color == "white" else 0.0
            rectangle_id = canvas.find_closest(j * square_size + square_size // 2, i * square_size + square_size // 2)
            if canvas.type(rectangle_id[0]) == 'rectangle':  # Only change the fill and outline for rectangles
                canvas.itemconfig(rectangle_id, fill=color)


def on_square_click(event, canvas, grid, i, j, square_size):
    global last_visited_square
    global color_change_interval
    global increase_mode
    last_visited_square = (i, j)
    
    if increase_mode:
        grid[i][j] = min(grid[i][j] + color_change_interval, 1.0)
    else:
        grid[i][j] = max(grid[i][j] - color_change_interval, 0.0)

    color = color_mapping(grid[i][j])
    rectangle_id = canvas.find_closest(j * square_size + square_size // 2, i * square_size + square_size // 2)
    canvas.itemconfig(rectangle_id, fill=color)  # Removed the outline=color parameter


def on_square_drag(event, canvas, grid, square_size):
    global last_visited_square
    x, y = event.x, event.y
    overlapping_items = canvas.find_overlapping(x - 1, y - 1, x + 1, y + 1)
    if overlapping_items:
        rectangle_id = overlapping_items[0]
        coords = canvas.coords(rectangle_id)
        i, j = int(coords[1] // square_size), int(coords[0] // square_size)
        if (i, j) != last_visited_square:
            on_square_click(event, canvas, grid, i, j, square_size)

def main():
    grid_size = 24
    square_size = 20
    grid = create_random_grid(grid_size)

    window = tk.Tk()
    window.title("Random Grid")
    canvas = tk.Canvas(window, width=grid_size * square_size, height=grid_size * square_size)
    canvas.pack()

    draw_grid(canvas, grid, square_size)
    window.mainloop()

if __name__ == "__main__":
    main()
