import kivy
import numpy as np

from kivy import platform

def speedx(snd_array, factor):
	""" Speeds up / down a sound, without shift preservation """
	indices = np.round( np.arange(0, len(snd_array), factor) )
	indices = indices[indices < len(snd_array)].astype(int)
	return snd_array[ indices ]

def stretch(snd_array, factor, window_size, h):
	""" Stretches/shortens a sound, by some factor. """
	phase  = np.zeros(window_size)
	hanning_window = np.hanning(window_size)
	result = np.zeros( len(snd_array) /factor + window_size)

	for i in np.arange(0, len(snd_array)-(window_size+h), h*factor):

	    # two potentially overlapping subarrays
	    a1 = snd_array[i: i + window_size]
	    a2 = snd_array[i + h: i + window_size + h]

	    # the spectra of these arrays
	    s1 =  np.fft.fft(hanning_window * a1)
	    s2 =  np.fft.fft(hanning_window * a2)

	    #  rephase all frequencies
	    phase = (phase + np.angle(s2/s1)) % 2*np.pi

	    a2_rephased = np.fft.ifft(np.abs(s2)*np.exp(1j*phase))
	    i2 = int(i/factor)
	    result[i2 : i2 + window_size] += hanning_window*a2_rephased

	result = ((2**(16-4)) * result/result.max()) # normalize (16bit)

	return result.astype('int16')

def pitchshift(snd_array, n, window_size=2**13, h=2**11):
	""" Changes the pitch of a sound by ``n`` semitones. """
	factor = 2**(1.0 * n / 12.0)
	stretched = stretch(snd_array, 1.0/factor, window_size, h)
	return speedx(stretched[window_size:], factor)
		
		
if platform == 'linux':
	
	from scipy.io import wavfile
	import pygame
	
	fps, soundLoaded = wavfile.read("bowl.wav") #read the sound file

	pygame.mixer.init(fps, -16, 1, 100) # init pygame mixer -> should check the parameters
	#pygame.mixer.init(44100,-16,2,4096)
	screen = pygame.display.set_mode((80,200)) # for the focus

	sound = pygame.sndarray.make_sound(soundLoaded)

	n = 0
	while True:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					n += 1
				elif event.key == pygame.K_DOWN:
					n -= 1	
				elif event.key == pygame.K_ESCAPE:
					pygame.quit()
					exit(0)
				sound.stop()
				sound = pygame.sndarray.make_sound(pitchshift(soundLoaded, ++n))
				sound.play(fade_ms=50)
			elif event.type == pygame.QUIT:
				pygame.quit()
	exit(0)
	
elif platform == 'android':
	from kivy.core.audio import Sound,SoundLoader
	import numpy as np
	import android.mixer as mixer
	
	soundLoaded = SoundLoader.load("bowl.wav") #read the sound file
	
else:
	print "Platform not handle for now"
