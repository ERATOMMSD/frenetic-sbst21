import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import MouseButton
import numpy as np
import os
import subprocess
import sys
import tkinter as tk
import tkinter.scrolledtext as scrolledtext

sys.path.append('../..')

import code_pipeline.tests_generation as test
import another_visualizer as vis
import frenet
import rd.nn as nn

class OobDistancesFigure:
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
        txy = self.ax.transData.inverted().transform([event.x, event.y])
        tx = txy[0]
        ty = txy[1]
        self.drag_index = self.get_nearest_index(tx, ty)

    def button_release_callback(self, event):
        txy = self.ax.transData.inverted().transform([event.x, event.y])
        tx = txy[0]
        ty = txy[1]
        if self.drag_index is not None:
            i = self.drag_index
            if event.button == MouseButton.LEFT:
                # self.xs[i] = tx # don't change x
                self.ys[i] = ty
            self.update_canvas()

    def update_canvas(self):
        self.ax.set_ylim([-2.5, 2.5])
        self.line.set_xdata(self.xs)
        self.line.set_ydata(self.ys)
        self.canvas.draw()
        self.canvas.flush_events()
        oob_distances = self.ys
        kappas = nn.oob_distances_to_kappas(self.nn_model, oob_distances)
        self.update_callback(kappas)

    def __init__(self, master, map_size, nof_points, update_callback, weights_json_filepath, biases_json_filepath, oob_values):
        # self.nn_model = nn.get_model('../../rd/19/80-30-110.trained-on-600.weights.json', '../../rd/19/80-30-110.trained-on-600.biases.json')
        self.nn_model = nn.get_model(weights_json_filepath, biases_json_filepath)
        self.map_size = map_size
        self.nof_points = nof_points
        self.figure = plt.figure()
        self.ax = plt.gca()
        # self.ax.set_aspect('equal')
        self.xs = np.linspace(0.1*self.map_size, 0.9*self.map_size, num=self.nof_points)
        self.ys = 0 * self.xs
        self.ys = oob_values
        self.line, = self.ax.plot(self.xs, self.ys, marker='o', markersize=6)
        plt.title('Left click to move a point in $y$ direction')
        plt.xlabel("$s$")
        plt.ylabel("oob_distances")
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

    def redraw(self, nof_points, weights_json_filepath, biases_json_filepath, oob_values):
        self.nn_model = nn.get_model(weights_json_filepath, biases_json_filepath)
        self.nof_points = nof_points
        self.xs = np.linspace(0.1*self.map_size, 0.9*self.map_size, num=self.nof_points)
        self.ys = 0 * self.xs
        self.ys = oob_values
        self.update_canvas()

    def set_focus(self):
        self.canvas.get_tk_widget().focus_set() # needed to capture key press events

class OobDistangeGUI:
    def __init__(self, map_size=200):
        self.map_size = map_size
        self.window = tk.Tk()

        self.top_top_frame = tk.Frame(master=self.window)
        self.top_top_frame.pack(fill=tk.X, side=tk.TOP)

        self.weights_json_filepath_label = tk.Label(master=self.top_top_frame, text='NN weights json file:')
        self.weights_json_filepath_label.pack(side=tk.LEFT)
        self.weights_json_filepath_entry = tk.Entry(master=self.top_top_frame)
        self.weights_json_filepath_entry.insert(0, '../../rd/19/80-30-110.trained-on-600.weights.json')
        self.weights_json_filepath_entry.pack(fill=tk.X, expand=1, side=tk.LEFT)

        self.biases_json_filepath_label = tk.Label(master=self.top_top_frame, text='NN biases json file:')
        self.biases_json_filepath_label.pack(side=tk.LEFT)
        self.biases_json_filepath_entry = tk.Entry(master=self.top_top_frame)
        self.biases_json_filepath_entry.insert(0, '../../rd/19/80-30-110.trained-on-600.biases.json')
        self.biases_json_filepath_entry.pack(fill=tk.X, expand=1, side=tk.LEFT)

        self.top_frame = tk.Frame(master=self.window)
        self.top_frame.pack(fill=tk.X, side=tk.TOP)

        # TODO: clean up
        #
        self.frenet_step_label = tk.Label(master=self.top_frame, text='frenet_step:')
        self.frenet_step_label.pack(side=tk.LEFT)
        self.frenet_step_entry = tk.Entry(master=self.top_frame)
        self.frenet_step_entry.insert(0, '10')
        self.frenet_step_entry.pack(fill=tk.X, expand=1, side=tk.LEFT)

        self.x0_label = tk.Label(master=self.top_frame, text='x0:')
        self.x0_label.pack(side=tk.LEFT)
        self.x0_entry = tk.Entry(master=self.top_frame)
        self.x0_entry.insert(0, '100')
        self.x0_entry.pack(fill=tk.X, expand=1, side=tk.LEFT)

        self.y0_label = tk.Label(master=self.top_frame, text='y0:')
        self.y0_label.pack(side=tk.LEFT)
        self.y0_entry = tk.Entry(master=self.top_frame)
        self.y0_entry.insert(0, '10')
        self.y0_entry.pack(fill=tk.X, expand=1, side=tk.LEFT)

        self.theta0_label = tk.Label(master=self.top_frame, text='Theta0:')
        self.theta0_label.pack(side=tk.LEFT)
        self.theta0_entry = tk.Entry(master=self.top_frame)
        self.theta0_entry.insert(0, "{:.2f}".format(np.pi/2))
        self.theta0_entry.pack(fill=tk.X, expand=1, side=tk.LEFT)

        self.nof_points_label = tk.Label(master=self.top_frame, text='Number of oob distances: ')
        self.nof_points_label.pack(side=tk.LEFT)
        self.nof_points_entry = tk.Entry(master=self.top_frame)
        self.nof_points_entry.insert(0, '19')
        self.nof_points_entry.pack(fill=tk.X, expand=1, side=tk.LEFT)

        self.top_bottom_frame = tk.Frame(master=self.window)
        self.top_bottom_frame.pack(fill=tk.X, side=tk.TOP)

        self.oob_label = tk.Label(master=self.top_bottom_frame, text='Initial oob distances: ')
        self.oob_label.pack(side=tk.LEFT)
        self.oob_entry = tk.Entry(master=self.top_bottom_frame)
        self.oob_entry.insert(0, ', '.join(['0' for i in range(19)]))
        self.oob_entry.pack(fill=tk.X, expand=1, side=tk.LEFT)

        self.show_button = tk.Button(master=self.top_bottom_frame, command=self.show_road, text='Show road')
        self.show_button.pack(side=tk.LEFT)

        self.center_frame = tk.Frame(master=self.window)
        self.center_frame.pack(fill=tk.BOTH, expand=1, side=tk.TOP)

        self.left_frame = tk.Frame(master=self.center_frame)
        self.left_frame.pack(fill=tk.BOTH, expand=1, side=tk.LEFT, padx=5, pady=5)
        self.mid_frame = tk.Frame(master=self.center_frame)
        self.mid_frame.pack(fill=tk.BOTH, expand=1, side=tk.LEFT, padx=5, pady=5)
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

        self.curve_figure = None
        self.visualizer = None
        self.visualize_first_time = True
        self.kappa_line = None

        self.show_road()

    def show_road(self):
        # clean test result
        self.test_result.delete("1.0", tk.END)
        self.test_result.insert(tk.INSERT, " ")


        self.weights_json_filepath = self.weights_json_filepath_entry.get().strip()
        self.biases_json_filepath = self.biases_json_filepath_entry.get().strip()

        # TODO: clean up
        # try:
        #     self.number_of_s_points = int(self.nof_points_entry.get().strip())
        # except ValueError:
        #     print('Number of s points must be a number!')
        #     self.number_of_s_points = 19
        self.number_of_s_points = 19

        try:
            self.x0 = float(self.x0_entry.get().strip())
        except ValueError:
            print('x0 must be a number!')
            self.x0 = 100.0

        try:
            self.y0 = float(self.y0_entry.get().strip())
        except ValueError:
            print('y0 must be a number!')
            self.y0 = 10

        try:
            self.theta0 = float(self.theta0_entry.get().strip())
        except ValueError:
            print('theta0 must be a number!')
            self.theta0 = np.pi / 2

        # try:
        #     self.frenet_step = float(self.frenet_step_entry.get().strip())
        # except ValueError:
        #     print('frenet_step must be a number!')
        #     self.frenet_step = 10.0
        self.frenet_step = 10.0

        self.oob_values = np.zeros(self.number_of_s_points)
        try:
            values = [float(v.strip()) for v in self.oob_entry.get().strip().split(",")]
            for i in range(len(values)):
                self.oob_values[i] = values[i]
        except ValueError:
            print('Something wrong with the oob values!')

        # This is called when we add or move a road point
        def update_callback(kappas):
            x0 = self.x0
            y0 = self.y0
            theta0 = self.theta0

            ss = np.arange(0, kappas.shape[0] * self.frenet_step, self.frenet_step)

            (xs, ys) = frenet.frenet_to_cartesian(x0, y0, theta0, ss, kappas)

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
                self.kappa_visualizer_canvas.get_tk_widget().pack_forget()
                self.kappa_visualizer_toolbar.pack_forget()
            self.visualizer = vis.RoadTestVisualizerForGUI(self.map_size)
            self.visualizer_figure = self.visualizer.last_submitted_test_figure
            self.visualizer.visualize_road_test(test.RoadTestFactory.create_road_test(road_points))
            self.visualizer_canvas = FigureCanvasTkAgg(self.visualizer_figure, master=self.right_frame)
            self.visualizer_canvas.draw()
            self.visualizer_toolbar = NavigationToolbar2Tk(self.visualizer_canvas, self.right_frame)
            self.visualizer_toolbar.update()
            self.visualizer_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
            self.visualize_first_time = False
            if self.kappa_line is None:
                self.kappa_visualizer_figure = plt.figure()
                self.kappa_line, = plt.plot(ss, kappas)
                plt.xlabel("$s$")
                plt.ylabel("Curvature $\\kappa(s)$")
            else:
                self.kappa_line.set_xdata(ss)
                self.kappa_line.set_ydata(kappas)
            self.kappa_visualizer_canvas = FigureCanvasTkAgg(self.kappa_visualizer_figure, master=self.mid_frame)
            self.kappa_visualizer_canvas.draw()
            self.kappa_visualizer_toolbar = NavigationToolbar2Tk(self.kappa_visualizer_canvas, self.mid_frame)
            self.kappa_visualizer_toolbar.update()
            self.kappa_visualizer_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        if self.curve_figure is None:
            self.curve_figure = OobDistancesFigure(self.left_frame, self.map_size, self.number_of_s_points, update_callback, self.weights_json_filepath, self.biases_json_filepath, self.oob_values)
        else:
            self.curve_figure.redraw(self.number_of_s_points, self.weights_json_filepath, self.biases_json_filepath, self.oob_values)

        self.curve_figure.set_focus()

        return 0

    def run_test(self, test_type):
        if not os.path.exists('../data'):
            os.makedirs('../data')
        with open("../data/road_points.txt", "w") as f:
            f.write(self.road_points_file_str)
        command = "python ../../competition.py --time-budget 300 --module-name src.generators.naive_generator --class-name NaiveGenerator --executor beamng --beamng-home D:\\Programs\\BeamNG.research.v1.7.0.1 --beamng-user C:\\Users\\mmsd-admin\\Documents\\BeamNG.research"
        if test_type == "mock":
            command = "python ../../competition.py --time-budget 10 --executor mock --map-size 200  --module-name src.generators.file_based_generator --class-name FileBasedGenerator"
        output = subprocess.getoutput(command)
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

OobDistangeGUI().start()
