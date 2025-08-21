from ursina import *

app = Ursina()

window.borderless = False
window.title = "Level Grid Example"
window.size = (800, 600)

# Sample list of (x, y, z) tuples
cells = [
    (0, 0, 0.2),
    (1, 0, 0.5),
    (2, 1, 0.8),
    (0, 2, 0.3),
    (1, 2, 0.7),
]

# Settings
grid_size = 3  # how wide and tall the grid is
cell_spacing = 0.5  # how far apart cells are

for x, y, z in cells:
    dot = Entity(
        model="square",
        color=color.color(0, 0, 1 - z),  # darker = higher z
        scale=0.1 + 0.2 * z,  # slightly bigger with more z
        position=(x * cell_spacing, y * cell_spacing, 0),
    )

app.run()
