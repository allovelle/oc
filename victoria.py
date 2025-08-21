from ursina import *

app = Ursina()

window.borderless = False
window.title = "Level Grid Example"
window.size = (800, 600)


class square:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.rot = 0

    def edge(self):
        sign = abs(self.rot - 1) - self.rot
        return self.rot % 2


z = 0
cell_spacing = 0.15

for x in range(10):
    for y in range(10):
        e = Entity(
            model="quad",
            color=color.rgb(0, 0, 1 - z),  # darker = higher z
            position=(x * cell_spacing, y * cell_spacing, 0),
            scale=0.1 + 0.2 * z,  # slightly bigger with more z
            rotation=(0, 0, 0),
        )

Button.default_color = color.red
b = Button(
    model="quad",
    scale=0.05,
    x=-0.5,
    color=color.lime,
    text="text scale\ntest",
    text_size=0.5,
    text_color=color.black,
)
b.text_size = 0.5
b.on_click = Sequence(
    Wait(0.5),
    Func(print, "aaaaaa"),
)

app.run()
