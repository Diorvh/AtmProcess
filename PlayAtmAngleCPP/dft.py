import numpy as np
import matplotlib.pyplot as plt

def dft(signal,freq=None):#freq为采样频率
    signal=signal-np.mean(signal)#减去直流分量
    if freq==None:
        freq=len(signal)
    fft_result = np.fft.fft(signal)
    frequencies = np.fft.fftfreq(len(signal), 1 / freq)
    magnitude = np.abs(fft_result)/len(signal)*2
    phase = np.angle(fft_result)
    return frequencies,magnitude,phase
def idft(magnitude,phase):
    return np.real(np.fft.ifft(magnitude*len(magnitude)/2 * np.exp(1j * phase)))
def lowpass(signal,freq,cutoff_freq):#保留cutoff_freq及以下的频率
    avg=np.mean(signal)
    frequencies,magnitude,phase=dft(signal,freq)
    for i in range(cutoff_freq+1,len(magnitude)//2):
        magnitude[i],phase[i]=0,0
        magnitude[-i],phase[-i]=0,0
    return idft(magnitude,phase)+avg
#限幅滤波
def AmpFilter(signal,error_max):
    for i in range(1,len(signal)):
        if np.abs(signal[i]-signal[i-1])>=error_max:
            signal[i]=signal[i-1]
    return signal
#SG滤波器

def analyze_signal(signal, Fs):
    frequencies,magnitude,phase=dft(signal,Fs)
    restored_signal=idft(magnitude,phase)
    N=len(signal)
    # Create a time array for the original signal
    t = np.linspace(0.0, N / Fs, N, endpoint=False)
    
    # Plot the original signal
    plt.figure(figsize=(10, 8))
    plt.subplot(5, 1, 1)
    plt.plot(t, signal)
    plt.title('Original Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')

    # Plot the magnitude spectrum
    plt.subplot(5, 1, 2)
    plt.plot(frequencies[:N // 2], magnitude[:N // 2])
    plt.title('Magnitude Spectrum')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')

    # Plot the phase spectrum
    plt.subplot(5, 1, 3)
    plt.plot(frequencies[:N // 2], phase[:N // 2])
    plt.title('Phase Spectrum')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Phase (radians)')

    # Display the restored signal
    plt.subplot(5, 1, 4)
    plt.plot(t, restored_signal)
    plt.title('Restored Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')

    plt.subplot(5, 1, 5)
    plt.plot(t, lowpass(signal,len(signal),6))
    plt.title('lowpass')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    
    plt.tight_layout()
    plt.show()

if __name__=='__main__':
    # Example usage:
    Fs = 1000  # Sampling frequency in Hz
    T = 1.0   # Duration in seconds
    N = int(T * Fs)  # Number of samples
    t = np.linspace(0.0, 1.0, N, endpoint=False)
    freq = 5  # Frequency in Hz
    signal = np.sin(2 * np.pi * freq * t)+6*np.sin(2 * np.pi * freq*5 * t+np.pi/3)+5
    # signal[250]+=100

    # Analyze the signal
    analyze_signal(signal, Fs)
