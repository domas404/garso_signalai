import os
import sys
import copy
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import numpy as np
from scipy.io import wavfile
from handle_data import handle_signal, handle_fade
from plot_data import plot_mono, plot_stereo
from spectrum_analysis import analyze_spectrum
from abc import ABC, abstractmethod

class FileData:
    def __init__(self, file_path, samplerate, data):
        self.file_name = os.path.basename(file_path)
        self.samplerate = samplerate
        self.data = np.array(data, dtype=int)
        self.bit_depth = data.dtype.itemsize * 8
        self.duration = len(data)/samplerate
        self.channel_count = 1 if len(data.shape) < 2 else data.shape[1]
        self.data_with_fade = None
        self.frame_size_in_ms = 0

    def set_data(self, data):
        self.data = data
        self.duration = len(data)/self.samplerate

    def transpose_data(self):
        if self.channel_count > 1:
            new_data = np.array(self.data)
            new_data = np.transpose(new_data)
            self.data = new_data.tolist()

    def apply_fade(self, data_with_fade):
        self.data_with_fade = np.array(data_with_fade, dtype=int)

    def clone(self):
        return copy.deepcopy(self)

    def set_frame_size(self):
        self.frame_size_in_ms = int(input("Enter frame size in ms.\n> "))

root = Tk()
root.withdraw()

def read_data():
    file_path = askopenfilename()
    samplerate, data = wavfile.read(file_path)
    file = FileData(file_path, samplerate, data)
    root.update()
    return file

class FileProcessing:

    _state = None

    def __init__(self, state):
        self.set_state(state)
        self.file_name = ""
    
    def set_state(self, state):
        self._state = state
        self._state.context = self

    def init_file(self):
        file = read_data()
        self.file = file
        self.file_name = file.file_name
        self.prepare_data()
    
    def prepare_data(self):
        if self.file.channel_count > 1:
            self.plot = plot_stereo
            self.file.transpose_data()
        else:
            self.plot = plot_mono
    
    def execute_function(self, func):
        func(self.file)

    def plot_file_data(self, plot_type):
        handle_signal(self.file, plot_type, self.plot)

    def choose_option(self):
        self._state.print_options(self.file_name)
        plot_menu_input = input("> ")
        self.set_state(self._state.execute_option(plot_menu_input))

class Dialog(ABC):

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context) -> None:
        self._context = context

    @abstractmethod
    def print_options(self, file_name) -> None:
        pass

    @abstractmethod
    def execute_option(self) -> None:
        pass

class MainMenu(Dialog):

    def print_options(self, file_name):
        print("MENU\n",
              "[1] Open file\n",
              "[2] Quit")

    def execute_option(self, input):
        if input == "1":
            self.context.init_file()
            return FileMenu()
        elif input == "2":
            sys.exit()

class FileMenu(Dialog):

    def print_options(self, file_name):
        print(f"FILE '{file_name}' MENU\n",
              "[1] Time domain plots\n",
              "[2] Fade effect\n",
              "[3] Spectrum analysis\n",
              "[0] Main menu")

    def execute_option(self, input):
        if input == "0":
            return MainMenu()
        elif input == "1":
            return TimeDomainPlotMenu()
        elif input == "2":
            self.context.execute_function(handle_fade)
        elif input == "3":
            self.context.execute_function(analyze_spectrum)
        return FileMenu()

class TimeDomainPlotMenu(Dialog):
    options = {
        "1": "energyPlot",
        "2": "zeroCrossingRatePlot",
        "3": "timePlot",
        "4": "segmentPlot",
        "0": "fileMenu"
    }
    def print_options(self, file_name):
        print(f"'{file_name}' time domain plot MENU\n",
              "[1] Energy plot\n",
              "[2] ZCR plot\n",
              "[3] Time plot\n",
              "[4] Segment plot\n",
              "[0] File menu")

    def execute_option(self, input):
        if input == "0":
            return FileMenu()
        elif input in self.options:
            self.context.plot_file_data(self.options[input])
        return TimeDomainPlotMenu()

if __name__ == "__main__":
    new_dialog = FileProcessing(MainMenu())
    while True:
        new_dialog.choose_option()
