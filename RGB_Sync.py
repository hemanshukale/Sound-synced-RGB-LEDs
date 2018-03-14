# For Syncing RGB LEDs with input sound from mic

# This might have some bugs, Do let me know (hemanshu.kale@gmail.com) in case of any random problems / bugs
# Enjoy :)


# Intensity of red : proportional to intensity of low frequecy (bass) 
# Intensity of green : proportional to intensity of mid frequecy (vocals) 
# Intensity of blue : proportional to intensity of high frequecy (instruments) 
# ^ can be changed according to feels

import numpy
import struct
import sys
import pyaudio
import time

PWM = True # set True if you're planning give pwm on the same device you're running this code
PYG = False

if PWM:
  import RPi.GPIO as IO
if PYG:
  import pygame

CHANNELS = 2
RATE     = 44100
FORMAT = pyaudio.paInt16

nFFT = 512
BUF_SIZE = 4 * nFFT

ofr, ofg, ofb = 0,0,0 # offsets (noise calibration)
sv1,sv2,sv3 = 0,0,0

cyan  = (0,255,255)
green = (0,255,0)
blue  = (0,0,255)
red   = (255,0,0)
black = (0,0,0)
sx,sy = 400,400
pri = False

if PWM:
  prr, pgg, pbb = 9, 10, 11 # pins number r,g,b respectvely
  IO.setmode(IO.BCM)
  IO.setup(prr, IO.OUT)
  IO.setup(pgg, IO.OUT)
  IO.setup(pbb, IO.OUT)

  pr=IO.PWM(prr, 100)
  pg=IO.PWM(pgg, 100)
  pb=IO.PWM(pbb, 100)

  pr.start(sv1)
  pg.start(sv2)
  pb.start(sv3)

if PYG:
    pygame.init()
    #pygame.display.set_caption(Title)
    screen = pygame.display.set_mode((sx,sy),pygame.RESIZABLE)
    pygame.mouse.set_visible(1)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250,250,250))
    background.fill((0,0,0))
    screen.blit(background, (0,0))

    rcir = pygame.draw.circle(screen, red, (200,100),50)
    gcir = pygame.draw.circle(screen, green, (100,300),50)
    bcir = pygame.draw.circle(screen, blue, (300,300),50)

    pygame.display.flip()



p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=BUF_SIZE)

def restartP(): # restart pyaudio in case of errors / exceptions
    global p, stream, CHANNELS, RATE, FORMAT, nFFT, BUF_SIZE
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=BUF_SIZE)


def scale(va, fromin, fromax, tomin, tomax):
    return numpy.interp(va, [fromin,fromax,],[tomin,tomax])

def constrain(val, i,j):
    if val < i:
        return i
    if val > j:
        return j
    return int(val)

def getF(MAX_y, ret): 
	# when ret is true, returns values for noise calibration

#  if pyg:
#      pygame.display.flip()
  global PWM, PYG, pri,ofr,orb,orc, stream, sv1,sv2,sv3
  if PWM:
    global pr,pg,pb

  if PYG:
    global black, red, green, blue

  # Read n*nFFT frames from stream, n > 0
  try:
    N = max(stream.get_read_available() / nFFT, 1) * nFFT
    data = stream.read(N)
  except IOError as e:
    time.sleep(2)
    restartP()
    return ""

  # Unpack data, LRLRLR...
  # Thanks to lbgists for the data unpacking and fft part
  # https://github.com/lbgists/audio-spectrum-matplotlib
  # http://blog.yjl.im/2012/11/frequency-spectrum-of-sound-using.html

  y = numpy.array(struct.unpack("%dh" % (N * CHANNELS), data)) / MAX_y
  y_L = y[::2]
  y_R = y[1::2]

  Y_L = numpy.fft.fft(y_L, nFFT)
  Y_R = numpy.fft.fft(y_R, nFFT)

  # Sewing FFT of two channels together, DC part uses right channel's
  Y = abs(numpy.hstack((Y_L[-nFFT / 2:-1], Y_R[:nFFT / 2])))
  ma = numpy.argmax(Y)
  v1,v2,v3 = 0,0,0

  # 255 - 390 into 3 parts 
  # s0, s1, s2, s3 = 250, 260, 285, 390
  # The array Y created of length 512 for two channels where each element has amplitude values for a frequecy range
  # mapped from 0-20kHz : elements 256-511 and 20kHz-0 : elements 0-255
  # There is a chart at bottom showing which elements peaked for a particular frequecncy

  d1, d2, d3 = 4, 20, 120
  c01, c02 = 255-d1, 256+d1
  c11, c12 = c01-d2, c02+d2
  c21, c22 = 0, 511
  # c21, c22 = c11-d3, c12+d3

  for i in xrange(c01,c02):
    v1+=Y[i] # aggregates around   0 Hz  - 280  Hz (low range)
  for i in list(xrange(c11,c01)) + list(xrange(c02,c12)):
    v2+=Y[i] # aggregates around 280 Hz  - 1.8 kHz (mid range)
  for i in list(xrange(c21,c11)) + list(xrange(c12,c22)):
    v3+=Y[i] # aggregates around 1.8 kHz -  20 kHz (high range)

  if ret:
    return (v1,v2,v3) # return values for noise calibration
  else :
  	# subtract calibrated noise values from raw data
    v1 -= ofr
    v2 -= ofg
    v3 -= ofb


  constr = 1000
  # the values v1, v2, v3 usually go till a max few thousands,
  # here anything above 1000 will turn on lights at full intensity

  scl_fac = (6,4.5,7)
  # the scaling factors set the responsiveness of our system
  # usually in songs, much of sound is mid range so the scaling factor 
  # for mid range has been kept less
  # else it would've dominated the colour combination everytime
  # mics are usually less sensitve for higher frequency, so the factor 
  # for high range is higher 
  iv1, iv2, iv3 = constrain(int(scl_fac[0]*v1),0,constr), constrain(int(scl_fac[1]*v2),0,constr), constrain(int(scl_fac[2]*v3),0,constr)
  sv1, sv2, sv3 = scale(iv1,0,constr,0,100), scale(iv2,0,constr,0,100), scale(iv3,0,constr,0,100)

  # for setting up threshold 
  # higher value will make the corresponding light turn on less frequently 
  # as it will require higher volume to turn on
  # set as per feels
  thre = 5
  if sv1 < thre : sv1 = 0
  if sv2 < thre : sv2 = 0
  if sv3 < thre : sv3 = 0


  # Here are the final values: sv1,sv2,sv3 ; All yours,
  if PWM:
    pr.ChangeDutyCycle(sv1)
    pg.ChangeDutyCycle(sv2)
    pb.ChangeDutyCycle(sv3)

  if PYG:
    screen.fill(black)
    rcir = pygame.draw.circle(screen, red, (200,100),int(sv1))
    gcir = pygame.draw.circle(screen, green, (100,300),int(sv2))
    bcir = pygame.draw.circle(screen, blue, (300,300),int(sv3))
    pygame.display.flip()


  if pri:
      # print ma, "\t",  format(Y[ma], '.3f'), "\t", int(iv1),"\t",int(iv2),"\t",int(iv3) , "\t\t",
      if sv1 != 0 or sv2 != 0 or sv3 != 0:
          print sv1, "\t", sv2, "\t", sv3

def rgb():

  calib = 300

  global ofr,ofb,ofc,p,stream, sv1,sv2,sv3

  if PWM:
    global pr,pg,pb

  # Used for normalizing signal. If use paFloat32, then it's already -1..1.
  # Because of saving wave, paInt16 will be easier.
  MAX_y = 2.0 ** (p.get_sample_size(FORMAT) * 8 - 1)
  try:

    for ij in xrange(0,10):
      ofrr, ofgg, ofbb = getF(MAX_y, True)

    tofr, tofg, tofb = 0,0,0

    # calibrating values to noise levels (wait for a few seconds at boot)
    for ij in xrange(0,calib):
      ofrr, ofgg, ofbb = getF(MAX_y, True)
      tofr += ofrr
      tofg += ofgg
      tofb += ofbb

    ofr = (tofr/calib)*3
    ofg = (tofg/calib)*3
    ofb = (tofb/calib)*3
	
	# multiplying for better effect (threshold)

    if pri:
      print "done calib", ofr, ofg, ofb

    sv1,sv2,sv3 = 100,100,100
    # turning all LEDs full on for 300 ms to indicate calibration is done
    if PWM:
      pr.ChangeDutyCycle(sv1)
      pg.ChangeDutyCycle(sv2)
      pb.ChangeDutyCycle(sv3)

    time.sleep(0.3)
    sv1,sv2,sv3 = 0,0,0

    if PWM:
      pr.ChangeDutyCycle(sv1)
      pg.ChangeDutyCycle(sv2)
      pb.ChangeDutyCycle(sv3)

    while True:
      getF(MAX_y, False)

  except KeyboardInterrupt:
    print "exiting"
    sys.exit()
    stream.stop_stream()
    stream.close()
    p.terminate()


rgb()

# some array index -frequency mappings observed by me

# index  frequency
# 255 -  20   Hz
# 256 -  100  Hz
# 257 -  177  Hz
# 258 -  230  Hz
# 262 -  350  Hz
# 265 -  884  Hz
# 267 - 1.00 kHz
# 276 - 1.82 kHz
# 284 - 2.46 kHz
# 308 - 4.60 kHz
# 319 - 5.49 kHz
# 348 - 8.00 kHZ
# 390 - 11.5 kHz

