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


def idft(magnitude, phase):
    return np.real(np.fft.ifft(magnitude * len(magnitude) / 2 * np.exp(1j * phase)))


def lowpass(signal, freq, cutoff_freq):
    average = np.mean(signal)
    frequencies, magnitude, phase = dft(signal, freq)
    for index in range(cutoff_freq + 1, len(magnitude) // 2):
        magnitude[index], phase[index] = 0, 0
        magnitude[-index], phase[-index] = 0, 0
    return idft(magnitude, phase) + average


def AmpFilter(signal, error_max):
    for index in range(1, len(signal)):
        if np.abs(signal[index] - signal[index - 1]) >= error_max:
            signal[index] = signal[index - 1]
    return signal
