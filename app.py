from math import pi, cos, sin, radians

import app

from events.input import Buttons, BUTTON_TYPES
import time

r1 = 103
r2 = 90

def arrow(size, skew, thickness, x, y, angle):
    points = [(0, 0), (size, skew), (size + thickness, skew), (thickness, 0), (size + thickness, -skew), (size, -skew)]
    points = [(p[0] - size * 1.5 // 2, p[1]) for p in points]
    points = [
        (int(round(px * cos(angle) - py * sin(angle))),
         int(round(px * sin(angle) + py * cos(angle))))
        for px, py in points
    ]
    points = [(p[0] + x, p[1] + y) for p in points]
    return points

def draw_polygon(ctx, points, fill_color):
    ctx.move_to(points[0][0], points[0][1])
    for point in points[1:]:
        ctx.line_to(point[0], point[1])
    ctx.close_path()
    if fill_color is not None:
        ctx.rgb(*fill_color).fill()

def hex_to_tuple(hex_color):
    """Convert a hex color to an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

nr_red = hex_to_tuple("#db010e")

class RailClockApp(app.App):
    def update_time(self, localtime):
        self.hours = localtime.tm_hour
        self.minutes = localtime.tm_min

    def __init__(self):
        self.button_states = Buttons(self)
        now = time.localtime()
        self.update_time(now)
        self.seconds = now.tm_sec

        self.updated_seconds = False

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            # The button_states do not update while you are in the background.
            # Calling clear() ensures the next time you open the app, it stays
            # open. Without it the app would close again immediately.
            self.button_states.clear()
            self.minimise()
        now = time.localtime()
        self.update_time(now)

        # Update every frame so it's smooth:
        self.seconds += delta / 1000
        # Plus sync every minute to avoid drift:
        # (but do it at the 45 second mark, so the magic moment the arrows meet is smooth!)
        if now.tm_sec == 45:
            if not self.updated_seconds:
                self.seconds = 45
            self.updated_seconds = True
        else:
            self.updated_seconds = False

    def draw(self, ctx):
        ctx.save()
        ctx.rgb(0, 0, 0).rectangle(-120, -120, 240, 240).fill()
        ctx.line_width = 5.0
        ctx.rgb(*nr_red).arc(0, 0, r1, 0, 2 * pi, True).stroke()
        ctx.rgb(*nr_red).arc(0, 0, r2, 0, 2 * pi, True).stroke()
        seconds = self.seconds
        angle = radians(seconds * 6 + 180)
        arr1 = arrow(25, 13, 13, r1 * -1 * sin(angle), r1 * cos(angle), angle)
        arr2 = arrow(-25, 11, -13, -(r2 * -1 * sin(angle)), r2 * cos(angle), -angle)
        draw_polygon(ctx, arr1, nr_red)
        draw_polygon(ctx, arr2, nr_red)
        ctx.font = 'Arimo Bold'
        ctx.text_align = ctx.CENTER
        ctx.text_baseline = 'middle'
        ctx.font_size = 60
        ctx.rgb(1, 1, 1).move_to(0, 0).text(f"{self.hours}:{self.minutes:02d}")
        ctx.restore()


__app_export__ = RailClockApp