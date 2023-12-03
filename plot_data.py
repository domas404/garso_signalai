import os
from datetime import timedelta
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import patches as mpatches
import numpy as np

font = {'size': 11}
matplotlib.rc('font', **font)

class PlotTools:

    def get_time(self, file, frame_length, start_time=0):
        time = np.linspace(start_time, start_time + file.duration, frame_length)
        return time

    def convert_time_to_readable_string(self, time_in_seconds):
        time_string = str(timedelta(seconds=time_in_seconds))[2:]
        if len(time_string) > 6:
            time_string = time_string[:9]
        else:
            time_string += ".000"
        return time_string

    def get_time_input(self, duration, stamp):
        print(f"Audio length: {self.convert_time_to_readable_string(duration)}")
        print(f"Enter {stamp} time.")
        mins = 0
        input_ok = False
        while not input_ok:
            try:
                if duration > 60:
                    mins = float(input("Minutes:\n> "))
                secs = float(input("Seconds:\n> "))
                if secs >= 60 or secs < 0:
                    raise ValueError("Incorrect time value")
                if mins*60+secs > duration:
                    raise ValueError("Time value out of bounds")
                input_ok = True
            except ValueError as ve:
                print(f"Error: {ve}. Try again.")
        return (mins*60) + secs

    def create_legend_patch(self, label):
        return mpatches.Patch(color='none', label=label)

    def plot_file_property_legend(self, channel_count, samplerate, bit_depth):
        channels_label = self.create_legend_patch(
            f'{channel_count} channel{"s" if channel_count > 1 else ""}')
        samplerate_label = self.create_legend_patch(f"{samplerate/1000} kHz")
        bit_depth_label = self.create_legend_patch(f"{bit_depth}-bit")
        handles = [channels_label, samplerate_label, bit_depth_label]
        leg = plt.legend(
            handles=handles,
            handlelength=0,
            borderpad=0.8,
            bbox_to_anchor=(1.01, 1),
            loc='upper left',
            borderaxespad=0.
        )
        plt.gca().add_artist(leg)

    def plot_time_legend(self, duration, frame_size_in_ms=0):
        time_legend = []
        if frame_size_in_ms > 0:
            frame_size_legend = self.create_legend_patch(f"Interval:\n{frame_size_in_ms} ms")
            time_legend.append(frame_size_legend)
        audio_time = self.create_legend_patch(
            f"File length:\n{self.convert_time_to_readable_string(duration)}")
        time_legend.append(audio_time)
        plt.legend(
            handles=time_legend,
            handlelength=0,
            borderpad=0.8,
            bbox_to_anchor=(1.01, 0),
            loc='lower left',
            borderaxespad=0.)

    def create_subplots(self, rows, file_name, width=12, height=8):
        figure, _ = plt.subplots(nrows=rows, ncols=1, sharey=True, sharex=True)
        figure.set_figwidth(width)
        figure.set_figheight(height)
        figure.suptitle(os.path.basename(file_name))
        return figure

    def get_values(self, file, data, start_time=0):
        length = len(data) if file.channel_count == 1 else len(data[0])
        x = self.get_time(file, length, start_time=start_time)
        if file.duration >= 60:
            x = x/60
        return x, data

    def add_labels(self, xlabel, ylabel, duration, y_label, x_label=""):
        if x_label == "":
            x_label = "Time, min" if duration > 60 else "Time, s"
        xlabel(x_label, fontsize=13)
        ylabel(y_label, fontsize=13)

    def add_figure_legend(self, file):
        plt.subplot(file.channel_count, 1, 1)
        self.plot_file_property_legend(file.channel_count, file.samplerate, file.bit_depth)

    def add_time_legend(self, duration, channel_count, frame_size):
        if channel_count > 1:
            plt.subplot(channel_count, 1, channel_count)
        if frame_size > 0:
            self.plot_time_legend(duration, frame_size_in_ms=frame_size)
        else:
            self.plot_time_legend(duration)

    def plot(self, x, y, file, line_wt=0.5):
        colors = ['#4986CC', '#3F4756', '#A3ACBD', '#C66481', '#8D3150']
        if file.channel_count == 1:
            y = [y]
        for i, channel in enumerate(y):
            plt.subplot(file.channel_count, 1, i+1)
            plt.grid(color='#ddd')
            plt.plot(x, channel, linewidth=line_wt, color=colors[i%len(colors)])

    def add_segments(self, x, segments, duration, channel_count):
        if segments is not None:
            if channel_count == 1:
                segments = [segments]
            for i, channel in enumerate(segments):
                plt.subplot(channel_count, 1, i+1)
                for segment in channel:
                    plt.axvline(
                        x=x[segment] if duration < 60 else x[segment]/60,
                        color='#ff3838',
                        lw=0.5)

    def show_plot(self):
        plt.tight_layout()
        plt.show()

class Plot:
    def __init__(self, plot_tools):
        self.plot = plot_tools

    def plot_time(self, file, data, segments=None, y_label='', start_time=0, duration=0):
        fig_height = 6
        if file.channel_count == 1:
            fig_height = 4
        figure = self.plot.create_subplots(file.channel_count, file.file_name, 10, fig_height)
        x, y = self.plot.get_values(file, data, start_time=start_time)
        self.plot.add_figure_legend(file)
        if duration == 0:
            duration = file.duration
        self.plot.add_time_legend(duration, file.channel_count, file.frame_size_in_ms)
        self.plot.plot(x, y, file)
        self.plot.add_segments(x, segments, file.duration, file.channel_count)
        self.plot.add_labels(figure.supxlabel, figure.supylabel, file.duration, y_label)
        self.plot.show_plot()

    def plot_spectrum(self, file, x, y):
        figure = self.plot.create_subplots(file.channel_count, file.file_name, 9, 5)
        self.plot.plot(x, y, file)
        self.plot.add_labels(figure.supxlabel, figure.supylabel, file.duration, y_label="", x_label="Frequency, Hz")
        self.plot.show_plot()

    def compare_time_plots(self, file1, file2, start):
        x1, y1 = self.plot.get_values(file1, file1.data, start_time=start)
        x2, y2 = self.plot.get_values(file2, file2.data, start_time=start)
        figure = self.plot.create_subplots(2, file1.file_name, 10, 6)

        plt.subplot(2, 1, 1)
        plt.grid(color='#ddd')
        plt.plot(x1, y1, linewidth=0.5)
        self.plot.plot_file_property_legend(file1.channel_count, file1.samplerate, file1.bit_depth)

        plt.subplot(2, 1, 2)
        plt.grid(color='#ddd')
        plt.plot(x2, y2, linewidth=0.5)

        self.plot.add_time_legend(file1.duration, file1.channel_count, file2.frame_size_in_ms)
        self.plot.add_labels(figure.supxlabel, figure.supylabel, file1.duration, y_label="")
        self.plot.show_plot()

plot_tools = PlotTools()
new_plot = Plot(plot_tools)
