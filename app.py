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

    def bump_time(self, hours, minutes, seconds):
        self.hours += hours
        self.minutes += minutes
        self.seconds += seconds
        if self.seconds >= 60 or self.seconds < 0:
            print(self.minutes, self.seconds)
            self.minutes += int(self.seconds // 60)
            self.seconds = self.seconds % 60
        if self.minutes >= 60 or self.minutes < 0:
            self.hours += int(self.minutes // 60)
            self.minutes = self.minutes % 60
        self.hours = self.hours % 24


    def __init__(self):
        self.button_states = Buttons(self)
        self.ff_rate = 1
        try:
            now = time.localtime()
            self.update_time(now)
            self.seconds = now.tm_sec
        except:
            print("Couldn't get starting time. Starting at midnight")
            self.hours = 0
            self.minutes = 0
            self.seconds = 0

        self.updated_seconds = False

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            # The button_states do not update while you are in the background.
            # Calling clear() ensures the next time you open the app, it stays
            # open. Without it the app would close again immediately.
            self.button_states.clear()
            self.minimise()
        if self.button_states.get(BUTTON_TYPES["DOWN"]):
            self.ff_rate += 1
            if self.ff_rate > 60:
                self.ff_rate = 60
            self.bump_time(0, self.ff_rate, 0)
        elif self.button_states.get(BUTTON_TYPES["UP"]):
            self.ff_rate += 1
            if self.ff_rate > 60:
                self.ff_rate = 60
            self.bump_time(0, -self.ff_rate, 0)

        else:
            self.ff_rate = 1

        try:
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
        except:
            # no clock, just count monotonically upwards instead
            self.bump_time(0, 0, delta / 1000)

    def draw(self, ctx):
        ctx.save()
        ctx.rgb(0, 0, 0).rectangle(-120, -120, 240, 240).fill()
        ctx.line_width = 6.0
        ctx.rgb(*nr_red).arc(0, 0, r1, 0, 2 * pi, True).stroke()
        ctx.rgb(*nr_red).arc(0, 0, r2, 0, 2 * pi, True).stroke()
        seconds = self.seconds
        angle = radians(seconds * 6 + 180)
        arr1 = arrow(25, 13, 13, r1 * -1 * sin(angle), r1 * cos(angle), angle)
        arr2 = arrow(-25, 11, -13, -(r2 * -1 * sin(angle)), r2 * cos(angle), -angle)
        draw_polygon(ctx, arr1, nr_red)
        draw_polygon(ctx, arr2, nr_red)
        ctx.font = 'Arimo Bold'
        ctx.font_size = 60
        ctx.text_align = ctx.CENTER
        # for some reason my 2024 badge crashes here, so let's bodge the y coord instead
        # ctx.text_baseline = 'center'
        ctx.rgb(1, 1, 1).move_to(0, 16).text(f"{self.hours:02d}:{self.minutes:02d}")
        ctx.restore()


__app_export__ = RailClockApp