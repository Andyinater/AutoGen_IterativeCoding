
import tkinter as tk
import time

class ClockApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Analog Clock")
        
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack()
        
        self.clock_face = self.canvas.create_oval(50, 50, 350, 350, width=2)
        self.hour_hand = self.canvas.create_line(200, 200, 200, 150, width=4)
        self.minute_hand = self.canvas.create_line(200, 200, 200, 100, width=3)
        self.second_hand = self.canvas.create_line(200, 200, 200, 75, width=2)
        
        self.update_clock()
        
    def update_clock(self):
        current_time = time.strftime("%H:%M:%S")
        hour, minute, second = current_time.split(":")
        
        hour_angle = (int(hour) % 12) * 30 + int(minute) / 2
        minute_angle = int(minute) * 6 + int(second) / 10
        second_angle = int(second) * 6
        
        self.canvas.delete("all")
        self.clock_face = self.canvas.create_oval(50, 50, 350, 350, width=2)
        self.hour_hand = self.canvas.create_line(200, 200, 200 + 80 * math.sin(math.radians(hour_angle)), 200 - 80 * math.cos(math.radians(hour_angle)), width=4)
        self.minute_hand = self.canvas.create_line(200, 200, 200 + 120 * math.sin(math.radians(minute_angle)), 200 - 120 * math.cos(math.radians(minute_angle)), width=3)
        self.second_hand = self.canvas.create_line(200, 200, 200 + 140 * math.sin(math.radians(second_angle)), 200 - 140 * math.cos(math.radians(second_angle)), width=2)
        
        self.root.after(1000, self.update_clock)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ClockApp()
    app.run()
