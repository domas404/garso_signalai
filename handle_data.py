import numpy as np
from scipy.io import wavfile
from plot_data import plot_mono, plot_stereo
from audio_effects import get_fade_data
from audio_analysis import get_energy, get_zcr, get_normalized_data_frames, get_data_frames, find_segments, normalize_data
from abc import ABC, abstractmethod

class PlotData(ABC):

    def plot_data(self, file, get_frames, plot):
        self.set_frame_size(file)
        self.get_data_frames(file, get_frames)
        self.set_values(file)
        self.set_segments(file)
        self.plot_values(file, plot)

    def set_frame_size(self, file):
        file.set_frame_size()

    def get_data_frames(self, file, get_frames):
        if file.channel_count == 1:
            self.data_frames = get_frames([file.data], file.samplerate, file.frame_size_in_ms)
        else:
            self.data_frames = get_frames(file.data, file.samplerate, file.frame_size_in_ms)

    @abstractmethod
    def set_values(self, file):
        pass

    @abstractmethod
    def plot_values(self, file, plot):
        pass

    def set_segments(self, file):
        pass

class PlotEnergy(PlotData):

    def set_values(self, file):
        self.energy = get_energy(self.data_frames)
        if file.channel_count == 1:
            self.energy = self.energy[0]

    def plot_values(self, file, plot):
        plot(file, self.energy, line_wt=1, y_label='Energy')

class PlotZcr(PlotData):

    def set_values(self, file):
        zcr = get_zcr(self.data_frames)
        self.normalized_zcr = []
        for channel in zcr:
            self.normalized_zcr.append(normalize_data(channel))
        if file.channel_count == 1:
            self.normalized_zcr = self.normalized_zcr[0]

    def plot_values(self, file, plot):
        plot(file, self.normalized_zcr, line_wt=1, y_label='Zero-Crossing Rate')

class PlotSegments(PlotData):

    def set_values(self, file):
        self.energy = get_energy(self.data_frames)

    def set_segments(self, file):
        self.segments = []
        step = float(input("Enter step size.\n> "))
        for channel in self.energy:
            self.segments.append(find_segments(channel, step))
        if file.channel_count == 1:
            self.energy = self.energy[0]
            self.segments = self.segments[0]

    def plot_values(self, file, plot):
        plot(file, self.energy, segments=self.segments, line_wt=1, y_label='Energy')

def handle_signal(file, plot_type, plot):

    if plot_type == "timePlot":
        plot(file, file.data, marker=False)
    
    elif plot_type == "zeroCrossingRatePlot":
        new_plot = PlotZcr()
        new_plot.plot_data(file, get_data_frames, plot)

    elif plot_type == "energyPlot":
        new_plot = PlotEnergy()
        new_plot.plot_data(file, get_normalized_data_frames, plot)

    elif plot_type == "segmentPlot":
        new_plot = PlotSegments()
        new_plot.plot_data(file, get_normalized_data_frames, plot)

    del new_plot

def handle_fade(file):

    fade_value_count, fade = get_fade_data(file)
    new_file = file.clone()

    if file.channel_count == 1:
        handle_signal(file, "timePlot", plot_mono)
        fade_in_data, fade_out_data = fade(file.data, fade_value_count)
        new_file_data = (fade_in_data
                        + list(file.data[fade_value_count:len(file.data)-fade_value_count])
                        + fade_out_data)
        new_file.set_data(new_file_data)
        handle_signal(new_file, "timePlot", plot_mono)
    else:
        handle_signal(file, "timePlot", plot_stereo)
        for i in range(0, file.channel_count):
            fade_in_data, fade_out_data = fade(file.data[i], fade_value_count)
            new_file_data = (fade_in_data
                            + list(file.data[i][fade_value_count:len(file.data[i])-fade_value_count])
                            + fade_out_data)
            new_file.data[i] = new_file_data
        handle_signal(new_file, "timePlot", plot_stereo)

    wavfile.write(f'fade_applied/{file.file_name}', file.samplerate, np.int16(new_file_data))
    del new_file
