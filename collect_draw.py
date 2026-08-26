"""collect_draw.py
Reproducible collector for the empirical test of the Configuration-Drift
Hypothesis, designed to adhere to the CORRECTED math (exact/lattice recurrence,
not eps-ball point references).

Run it, then draw with the mouse (hold left button and move). To test the
hypothesis fairly, draw circles that DRIFT: let each new circle migrate to a
new region of the canvas, so the configuration-space walk carries you away from
old configs over time (this is the drifted-walk regime where exact recurrence
is predicted to DECAY). Aim for a few hundred circles / a few thousand points.
Every pen sample is recorded with its timestamp. Press 'S' (or close the window)
to stop and save drawing_data.csv with columns:  index, x, y, t_seconds, stroke.

Analysis (analyze_exact.py for exact 4-D config recurrence; analyze_drawing.py
for corrected tgap point/centroid recurrence) then computes the recurrence
density over time and a sign-aware shuffle-null p-value.
"""

import csv
import time
import tkinter as tk

OUT = "drawing_data.csv"
MIN_DT = 0.015          # throttle: >=15 ms between samples so consecutive
                        # points are spaced (not sub-pixel adjacent along the
                        # pen path) -- avoids trivial adjacency "recurrence".
MAX_POINTS = 4000       # hard cap to keep the analysis tractable


class Collector:
    def __init__(self, root):
        self.root = root
        self.root.title("Configuration-Drift collector -- draw with the mouse")
        self.canvas = tk.Canvas(root, width=900, height=600, bg="white",
                                cursor="cross")
        self.canvas.pack()
        self.label = tk.Label(root, text="Draw circles that DRIFT to new areas over time. Press 'S' to save & quit.")
        self.label.pack()
        self.points = []
        self.drawing = False
        self.stroke = 0
        self.t0 = time.time()
        self.last_t = -1.0
        self.canvas.bind("<ButtonPress-1>", self.down)
        self.canvas.bind("<B1-Motion>", self.motion)
        self.canvas.bind("<ButtonRelease-1>", self.up)
        self.root.bind("s", self.save)

    def down(self, e):
        self.drawing = True
        self.stroke += 1
        self.record(e)

    def motion(self, e):
        if self.drawing:
            self.record(e)

    def up(self, e):
        self.drawing = False

    def record(self, e):
        now = time.time() - self.t0
        if now - self.last_t < MIN_DT:
            return
        if len(self.points) >= MAX_POINTS:
            return
        self.last_t = now
        self.points.append((len(self.points), e.x, e.y, now, self.stroke))
        self.label.config(
            text=f"circles: {self.stroke}   points: {len(self.points)}   "
                 f"(press 'S' to save & quit)")
        # light visual feedback
        self.canvas.create_oval(e.x - 1, e.y - 1, e.x + 1, e.y + 1, fill="black")

    def save(self, *_):
        with open(OUT, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["index", "x", "y", "t_seconds", "stroke"])
            w.writerows(self.points)
        print(f"saved {len(self.points)} points across {self.stroke} circles/strokes to {OUT}")
        self.root.destroy()


if __name__ == "__main__":
    r = tk.Tk()
    Collector(r)
    r.mainloop()
