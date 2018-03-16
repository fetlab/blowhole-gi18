from glob import glob
from sklearn.decomposition import PCA
from math import sqrt
from os.path import basename as base_name
from os.path import splitext as split_text
from time import sleep

import matplotlib.pyplot as plt
import numpy as np
import sklearn
from scipy.io import wavfile
from sklearn import svm
from sklearn.datasets.base import Bunch

import pyaudio
from EAC import eac
from ml_utils import cross_predict, fit_model
from plt_utils import plot_confusion
from python_speech_features import mfcc as mfcc_gen


class Wave(object):
	def __init__(self, filenames, classname):
		waves = []
		self.classname = classname

		if isinstance(filenames, str):
			names = glob(filenames)
			if not names:
				raise ValueError('No files in %s' % filenames)
		for fn in names:
			print fn
			r, w = wavfile.read(fn)

			# If the recording is mono, make it the right shape
			if w.ndim == 1:
				w = w[:, np.newaxis]
			waves.append(w)
		self.rate = r

		self.data = np.vstack(waves)
		if self.data.dtype == np.int16:
			self.data = self.data.astype(np.int64)

	
	def __repr__(self):
		return '<%s: %s>' % (self.__class__.__name__, self.classname)



class Blow(Wave):
	def __init__(self, filenames, classname, w_size=.1, thresh=0):
		super(Blow, self).__init__(filenames, classname)

		self.thresh   = thresh
		self.w_size   = w_size
		self.blows    = []
		self.get_blows()

	
	def get_blows(self):
		blow = []
		for window in self._window(self.data):
			if self._rms(window) > self.thresh:
				blow.extend(window.T[0].tolist())
			elif blow and self._rms(window) < self.thresh:
				self.blows.append(np.array(blow))
				blow = []

		if blow:
			self.blows.append(blow)
		self.blows = np.array(self.blows)


	def _window(self, blow):
		w_size    = int(self.w_size * self.rate)
		n_windows = len(blow) / w_size

		for i in xrange(n_windows):
			yield blow[i * w_size: (i + 1) * w_size]
	

	def _rms(self, signal):
		x = 0
		for sample in signal:
			x += sample ** 2
		return 3



class Features(object):
	def __init__(self, chunks=None, rate=None):
		self.feature_generators = (
			self.mfcc,
		)
		if chunks is not None:
			self.chunks = chunks
		if rate is not None:
			self.rate = rate
		else:
			self.rate = 44100

		self.gen_features()

	
	def eac(self, data=None):
		eacs = []
		from numpy.fft.helper import rfftfreq
		from scipy.signal     import find_peaks_cwt
		for blow in self.blows:
			tmp_eac = eac(blow)[0]
			times   = np.arange(1, len(tmp_eac)) / float(self.rate)
			freqs   = 1.0 / times
			tmp_indexes = find_peaks_cwt(tmp_eac, range(1, 5))
			max_val = list(reversed(sorted(tmp_eac[tmp_indexes])))[:1]
			indexes = []
			for i in max_val:
				indexes.append(np.where(tmp_eac == i)[0][0])
			eacs.append(freqs[indexes])
		return eacs


	def gen_features(self):
		self.all_features = np.hstack(f() for f in self.feature_generators)

	
	def fft(self, data=None):
		from numpy.fft.fftpack import rfft
		fft = []
		for chunk in self.chunks:
			fft.append(np.abs(rfft(chunk, axis=0)))
		return np.array(fft)

	
	def reduced_fft(self, data=None):
		from numpy.fft.fftpack import rfft
		fft = []
		for chunk in self.chunks:
			chunk_fft = np.abs(rfft(chunk, axis=0))
			max = chunk_fft.max()
			fft.append(chunk_fft / max)
		fft = np.array(fft)
		pca = PCA(n_components=500)
		fit =  pca.fit_transform(fft)
		print fit.shape
		return fit

	def norm_fft(self, data=None):
		from numpy.fft.fftpack import rfft
		fft = []
		for chunk in self.chunks:
			chunk_fft = np.abs(rfft(chunk, axis=0))
			max = chunk_fft.max()
			fft.append(chunk_fft / max)
		fft = np.array(fft)
		return fft


	def _fft_freqs(self):
		from numpy.fft.helper import rfftfreq
		return rfftfreq(len(self.chunks[0]), 1.0/self.rate)


	def mfcc(self):
		mfcc = []
		for chunk in self.chunks:
			mfcc_chunk = mfcc_gen(chunk)
			mfcc_chunk = mfcc_chunk.reshape(mfcc_chunk.shape[0] *
				mfcc_chunk.shape[1], )
			mfcc.append(mfcc_chunk)

		mfcc = np.array(mfcc)
		return mfcc

	
	def raw(self):
		mean, std = [], []
		for chunk in self.chunks:
			mean.append(chunk.mean())
			std.append(chunk.std())

		return np.vstack((mean, std)).T

	

class BlowFeatures(Blow, Features):
	def __init__(self, filenames, classname):
		
		super(BlowFeatures, self).__init__(filenames, classname)

		self.chunks = []
		for blow in self.blows:
			self.chunks.append(list(self._window(blow)))
		self.chunks = np.vstack(self.chunks)

		Features.__init__(self)



class Blowhole(Blow):
	def __init__(self, model_path, rate=44100, chunk_length=.1,
		thresh=200, min_length=.7):
		self.model        = self.set_model(model_path)
		self.rate         = rate
		self.chunk_length = chunk_length
		self.thresh       = thresh
		self.min_length   = min_length
		self.prds         = []
	

	def set_model(self, path):
		if 'pickle' in path:
			import cPickle as pickle
			return pickle.load(open(path, 'rb'))
		else:
			self.dataset = export(load_dir(path))
			return fit_model(self.dataset)

	
	def run_live(self):
		p = pyaudio.PyAudio()
		self.stream_handler = p.open(
			format            = p.get_format_from_width(2),
			channels          = 1,
			rate              = self.rate,
			input             = True,
			output            = False,
			stream_callback   = self.callback,
			frames_per_buffer = int(self.rate * self.chunk_length)
		)

		print 'Starting stream'
		self.stream_handler.start_stream()
		while self.stream_handler.is_active():
			sleep(.1)
	

	def run_wav(self, wav_file):
		pass


	def callback(self, in_data, frame_count, time_info, status):
		chunk = np.fromstring(in_data, dtype=np.int16)
		if self._rms(chunk) > self.thresh:
			# Features expects an array of chunks
			chunk = chunk[np.newaxis, :]

			data = Features(chunk).all_features
			self.prds.append(self.model.predict(data))
		elif self._rms(chunk) < self.thresh and self.prds:
			if len(self.prds) * self.chunk_length > self.min_length:
				from scipy import stats
				self.prds = np.vstack(self.prds)
				result = stats.mode(self.prds)[0][0][0]
				print "Result: %s" % result
				f = open('../quiz_ui/result.txt', 'w')
				f.write(str(result))
				f.close()
			self.prds = []

		return (in_data, pyaudio.paContinue)



def load_dir(expression):
	files = glob(expression)
	feats = []
	for fn in files:
		classname = split_text(base_name(fn))[0].split('-')[0]
		feats.append(BlowFeatures(fn, classname))

	return feats

def run_action(action):
	pass

def export(features):
	data   = np.vstack(i.all_features for i in features)
	target = np.hstack([i.classname] * i.chunks.shape[0] for i in
		features)
	classnames = np.unique([i.classname for i in features])
	
	return Bunch(data=data, target=target, classnames=classnames)

def main ():
	import sys, argparse
	parser = argparse.ArgumentParser(
		description='Blowhole: Interactive blow-activated tags for 3D\
			printed objects')
	parser.add_argument('--model', action='store',
		help='Pickle file or glob expression to use as model')
	parser.add_argument('--ws', action='store', type=int, nargs='?', const=8000, 
		help='Start a Web server for visualizations and actions. Optionally, specity port')
	parser.add_argument('--freq', action='store', type=int, nargs='?',
		const=44100, help='Sampling frequency')


	if not sys.argv[1:]:
		parser.print_help()
		sys.exit(0)

	args = parser.parse_args()

	bh = Blowhole(args.model)
	bh.run_live()
		

if __name__ == '__main__':
	main()
