"""
Alghoritm iterates for every audio file in given directory.
File directory have to be absolute.
Each audio file is processed in order to extract parameters.
Finally all paremters vectors for each y are saved to CSV file.
"""

import os
import numpy as np
import pandas as pd
import librosa
from scipy.stats import kurtosis
from scipy.stats import skew
from scipy.signal import blackmanharris


def parameterstocsv(datadir, patientstatus, df2Csv):
    """
    Attributes
    ----------
    datadir
        Absolute audio files directory
    patientstatus
        Healthy or pathology

    Methods
    ----------
    Returns csv file with extracted features.
    """
    fulldir = os.path.join(os.getcwd(), datadir)
    df2Csv += '.csv'
    allfiles = os.listdir(fulldir)
    columns = ['MFCC1',
               'MFCC2',
               'MFCC3',
               'MCCC4',
               'MFCC5',
               'MFCC6',
               'MFCC7',
               'MFCC8',
               'MFCC9',
               'MFCC10',
               'RMS',
               'ZCR',
               'F0',
               'MAX',
               'MIN',
               'KURTOSIS',
               'SKEWNESS']
    cases = pd.DataFrame(columns=columns)

    for filename in allfiles:
        filepath = os.path.join(datadir, filename)
        cases.loc[len(cases)] = parameters(filepath)

    cases['Status'] = patientstatus
    cases.to_csv(df2Csv, index=False)


def parameters(filepath):
    """
    Compute parametrs vector for each audio file.
    """
    y, sr = librosa.load(filepath)

    if(~(np.isnan(np.sum(y)))):
        framelength = 512
        n_mfcc = 10
        parameters = []

        mfcc = librosa.feature.mfcc(y=y,
                                    sr=sr,
                                    hop_length=framelength,
                                    n_mfcc=n_mfcc)

        for i in range(n_mfcc):
            parameters.append(np.mean(mfcc[i]))

        RMS = librosa.feature.rmse(y, hop_length=framelength)
        parameters.append(np.mean(RMS))
        ZCR = librosa.feature.zero_crossing_rate(y, hop_length=framelength)
        parameters.append(np.mean(ZCR))
        F0 = fundamental_freq(y, sr, framelength)
        parameters.append(F0)
        MAX = np.amax(y)
        parameters.append(MAX)
        MIN = np.amin(y)
        parameters.append(MIN)
        KURTOSIS = kurtosis(y)
        parameters.append(KURTOSIS)
        SKEWNESS = skew(y)
        parameters.append(SKEWNESS)

        return parameters


def fundamental_freq(y, sr, framelength):
    """
    Find fundametal freq with use of FFT.
    """
    N = len(y)
    f0 = []
    for i in range(framelength, N, framelength):
        start = i - framelength
        end = i
        frame = y[start:end]
        f0.append(freq_from_fft(frame, sr))

    return np.mean(f0)


def freq_from_fft(sig, fs):
    """
    Estimate frequency from peak of FFT
    """

    windowed = sig * blackmanharris(len(sig))
    f = np.fft.fft(windowed)

    # Find the peak and interpolate to get a more accurate peak
    i = np.argmax(abs(f))
    true_i = parabolic(np.log(abs(f)), i)[0]

    # Convert to equivalent frequency
    return fs * true_i / len(windowed)


def parabolic(f, x):
    """
    Quadratic interpolation for estimating the true position of an
    inter-sample maximum when nearby samples are known.

    Parameters
    -----------
    f is a vector 
    x is an index for that vector.

    Method
    -----------
    Returns (vx, vy), the coordinates of the vertex of a parabola that goes
    through point x and its two neighbors.
    """
    xv = 1 / 2. * (f[x - 1] - f[x + 1]) / (f[x - 1] - 2 * f[x] + f[x + 1]) + x
    yv = f[x] - 1 / 4. * (f[x - 1] - f[x + 1]) * (xv - x)

    return (xv, yv)