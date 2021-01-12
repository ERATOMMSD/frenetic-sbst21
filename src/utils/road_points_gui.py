import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import MouseButton
import numpy as np
import sys
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import subprocess

sys.path.append('../..')

import code_pipeline.tests_generation as test
import another_visualizer as vis

class RoadFigure:
    # button press/release handling is discussed in: https://matplotlib.org/2.2.2/gallery/event_handling/poly_editor.html?highlight=polygoninteractor
    # https://stackoverflow.com/questions/50439506/dragging-points-in-matplotlib-interactive-plot
    def get_nearest_index(self, tx, ty):
        min_dist_sq = self.map_size ** 2
        nearest_i = 0
        for i in range(self.xs.shape[0]):
            x = self.xs[i]
            y = self.ys[i]
            dist_sq = (x - tx) ** 2 + (y - ty) ** 2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest_i = i
        return nearest_i

    def button_press_callback(self, event):
        print("button press : {:.2f} - {:.2f}".format(event.x, event.y))
        txy = self.ax.transData.inverted().transform([event.x, event.y])
        tx = txy[0]
        ty = txy[1]
        self.drag_index = self.get_nearest_index(tx, ty)

    def button_release_callback(self, event):
        print("button release : {:.2f} - {:.2f}".format(event.x, event.y))
        txy = self.ax.transData.inverted().transform([event.x, event.y])
        tx = txy[0]
        ty = txy[1]
        if self.drag_index is not None:
            i = self.drag_index
            if event.button == MouseButton.LEFT:
                self.xs[i] = tx
                self.ys[i] = ty
            else:
                old_xs = self.xs
                old_ys = self.ys
                self.xs = np.zeros(self.xs.shape[0] + 1)
                self.ys = np.zeros(self.ys.shape[0] + 1)
                self.xs[0:i+1] = old_xs[0:i+1]
                self.ys[0:i+1] = old_ys[0:i+1]
                self.xs[i+1] = tx
                self.ys[i+1] = ty
                if i < self.xs.shape[0] - 1:
                    self.xs[i+2:] = old_xs[i+1:]
                    self.ys[i+2:] = old_ys[i+1:]
            self.update_canvas()

    def update_canvas(self):
        self.line.set_xdata(self.xs)
        self.line.set_ydata(self.ys)
        self.canvas.draw()
        self.canvas.flush_events()
        self.update_callback(self.xs, self.ys)

    def __init__(self, master, map_size, nof_points, update_callback=None):
        self.map_size = map_size
        self.nof_points = nof_points
        self.figure = plt.figure()
        self.ax = plt.gca()
        self.ax.set_aspect('equal')
        self.xs = np.linspace(0.1*self.map_size, 0.9*self.map_size, num=self.nof_points)
        self.ys = np.linspace(0.1*self.map_size, 0.9*self.map_size, num=self.nof_points)
        self.line, = self.ax.plot(self.xs, self.ys, marker='o', markersize=6)
        plt.title('Left click to move a point; Right click to add a new point')
        self.drag_index = None
        self.update_callback = update_callback

        self.canvas = FigureCanvasTkAgg(self.figure, master=master)
        self.canvas.mpl_connect('button_press_event', self.button_press_callback)
        self.canvas.mpl_connect('button_release_event', self.button_release_callback)
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, master)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        self.update_canvas()

    def redraw(self, nof_points):
        self.nof_points = nof_points
        self.xs = np.linspace(0.1*self.map_size, 0.9*self.map_size, num=self.nof_points)
        self.ys = np.linspace(0.1*self.map_size, 0.9*self.map_size, num=self.nof_points)
        self.update_canvas()

    def set_focus(self):
        self.canvas.get_tk_widget().focus_set() # needed to capture key press events

class RoadPointsGUI:
    def __init__(self, map_size=200):
        self.map_size = map_size
        self.window = tk.Tk()

        self.top_frame = tk.Frame(master=self.window)
        self.top_frame.pack(fill=tk.X, side=tk.TOP)

        self.nof_points_label = tk.Label(master=self.top_frame, text='Number of road points: ')
        self.nof_points_label.pack(side=tk.LEFT)

        self.nof_points_entry = tk.Entry(master=self.top_frame)
        self.nof_points_entry.insert(0, '10')
        self.nof_points_entry.pack(fill=tk.X, expand=1, side=tk.LEFT)

        self.show_button = tk.Button(master=self.top_frame, command=self.show_road, text='Show road')
        self.show_button.pack(side=tk.LEFT)

        self.center_frame = tk.Frame(master=self.window)
        self.center_frame.pack(fill=tk.BOTH, expand=1, side=tk.TOP)

        self.left_frame = tk.Frame(master=self.center_frame)
        self.left_frame.pack(fill=tk.BOTH, expand=1, side=tk.LEFT, padx=5, pady=5)
        self.right_frame = tk.Frame(master=self.center_frame)
        self.right_frame.pack(fill=tk.BOTH, expand=1, side=tk.LEFT, padx=5, pady=5)

        self.road_points_frame = tk.Frame(master=self.window)
        self.road_points_label = tk.Label(master=self.road_points_frame, text="Road points:")
        self.road_points_label.pack(side=tk.LEFT)
        self.road_points_entry = tk.Entry(master=self.road_points_frame)
        self.road_points_entry.pack(fill=tk.X, expand=1, side=tk.LEFT)
        self.road_points_frame.pack(fill=tk.X, side=tk.TOP)

        self.mock_test_button = tk.Button(master=self.road_points_frame, command=self.run_mock_test, text='Run mock test')
        self.mock_test_button.pack(side=tk.LEFT)
        self.beamng_test_button = tk.Button(master=self.road_points_frame, command=self.run_beamng_test, text='Run beamng test')
        self.beamng_test_button.pack(side=tk.LEFT)

        self.test_result = scrolledtext.ScrolledText(height=20, master=self.window)
        self.test_result.insert(tk.INSERT, " ")
        self.test_result.pack(fill=tk.X, side=tk.TOP)

        self.road_figure = None
        self.visualizer = None
        self.visualize_first_time = True

        self.show_road()

    def show_road(self):
        # clean test result
        self.test_result.delete("1.0", tk.END)
        self.test_result.insert(tk.INSERT, " ")

        try:
            self.number_of_road_points = int(self.nof_points_entry.get().strip())
        except ValueError:
            print('Number of road points must be a number!')
            self.number_of_road_points = 10

        # This is called when we add or move a road point
        def update_callback(xs, ys):
            road_points = []
            self.road_points_str = '['
            self.road_points_file_str = ''
            for i in range(xs.shape[0]):
                road_points.append((xs[i], ys[i]))
                # TODO: change :.2 to have more precision
                self.road_points_str += "({:.5f}, {:.5f})".format(xs[i], ys[i])
                self.road_points_file_str += "{:.5f} {:.5f}".format(xs[i], ys[i])
                if i < xs.shape[0] - 1:
                    self.road_points_str += ','
                    self.road_points_file_str += '\n'
            self.road_points_str += ']'
            self.road_points_entry.delete(0, tk.END)
            self.road_points_entry.insert(0, self.road_points_str)

            # how to show matplotlib figure in tk:
            # https://www.geeksforgeeks.org/how-to-embed-matplotlib-charts-in-tkinter-gui/
            if not self.visualize_first_time:
                self.visualizer_canvas.get_tk_widget().pack_forget()
                self.visualizer_toolbar.pack_forget()
            self.visualizer = vis.RoadTestVisualizerForGUI(self.map_size)
            self.visualizer_figure = self.visualizer.last_submitted_test_figure
            self.visualizer.visualize_road_test(test.RoadTestFactory.create_road_test(road_points))
            self.visualizer_canvas = FigureCanvasTkAgg(self.visualizer_figure, master=self.right_frame)
            self.visualizer_canvas.draw()
            self.visualizer_toolbar = NavigationToolbar2Tk(self.visualizer_canvas, self.right_frame)
            self.visualizer_toolbar.update()
            self.visualizer_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
            self.visualize_first_time = False

        if self.road_figure is None:
            self.road_figure = RoadFigure(self.left_frame, self.map_size, self.number_of_road_points, update_callback)
        else:
            self.road_figure.redraw(self.number_of_road_points)

        self.road_figure.set_focus()

        return 0

    def run_test(self, type):
        with open("../data/road_points.txt", "w") as f:
            f.write(self.road_points_file_str)
        output = subprocess.getoutput("python ../../competition.py --visualize-tests --time-budget 10 --executor {} --map-size 200  --module-name src.generators.file_based_generator --class-name FileBasedGenerator".format(type))
        self.test_result.delete("1.0", tk.END)
        self.test_result.insert(tk.INSERT, output)


    def run_mock_test(self):
        self.run_test("mock")

    def run_beamng_test(self):
        self.run_test("beamng")

    def start(self):
        self.window.mainloop()

    def visualizer_figure(self):
        visualizer = vis.RoadTestVisualizer(250)
        visualizer.visualize_road_test(test.RoadTestFactory.create_road_test([(10, 10), (20, 20)]))
        plt.ioff()
        plt.show()

RoadPointsGUI().start()
