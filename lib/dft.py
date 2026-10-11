import numpy as np


def dft(signal, freq=None):
    signal = signal - np.mean(signal)
    if freq is None:
        freq = len(signal)
    fft_result = np.fft.fft(signal)
    frequencies = np.fft.fftfreq(len(signal), 1 / freq)
    magnitude = np.abs(fft_result) / len(signal) * 2
    phase = np.angle(fft_result)
    return frequencies, magnitude, phase
