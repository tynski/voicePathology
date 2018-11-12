import os 
from scipy.io import wavfile
import numpy as np
import pandas as pd

def ParametersFromFile(dataDirectory, patientStatus):
	df2Csv = input('Enter file name:')
	df2Csv += '.csv'
	filePath = os.path.join('/home/barti/Documents/voicePathology/voiceDataset/', dataDirectory)
	Files = os.listdir(filePath)
	columns = ['RMS', 'mean', 'energy', 'power', 'min', 'max']
	cases = pd.DataFrame(columns = columns)
	for fileName in Files:
		data = returnParameters(filePath, fileName)
		data = np.reshape(data, (1,len(columns)))
		df = pd.DataFrame(data = data, columns = columns)
		cases = cases.append(df)
	cases['Status'] = patientStatus
	cases.to_csv(df2Csv, index = False)

def returnParameters(filePath, fileName):
	audio = wavfile.read(os.path.join(filePath, fileName))[1]
	audio = audio[~np.isnan(audio)]
	return voiceParameters(audio.tolist())

def voiceParameters(signal):
	N = len(signal)
	return [RMS(signal), mean(signal), energy(signal), power(signal, N), min(signal), max(signal)]

def RMS(signal):
	return np.sqrt(np.mean(np.power(signal, 2)))

def mean(signal):
	return np.mean(signal)

def energy(signal):
	return np.sum(np.power(signal, 2))

def power(signal, N):
	return np.sum(np.power(signal, 2)/(2*N + 1))