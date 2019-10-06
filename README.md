# Music-synced-RGB-Lights
Sync your RGB lights with sound: allotting any frequency range to each colour

https://youtu.be/r-f_4nSMtbU  

Hey all..

I've synced my RGB LED strip with sound frequencies..  
Red for low range (bass)  
Green for mid range (vocals)  
Blue for high range (instruments)  

The colour at any time is the addition of all the three components, hence resulting in lots of colour combinations. 

The aggregate intensity over a particular range controls the intensity of the corresponding color.  

## Stuff required:  

RGB Lights (I've used a non programmable RGB LED (5050) strip.  
3 MOSFETS  (I've used AP70T03 as it has cutoff (Gate Source threshold) voltage less than 3.3V)  
A system to run the audio processing code and a system to drive the MOSFETS by PWM.  
I've used a Raspberry Pi which does both. You can also run the audio processing code on any system and send final values to the driving microcontroller.  
External mic and sound card (in case of using Raspberry Pi).  
Try to prefer an external mic as there is usually some interference in laptop internal microphones.  
Jumpers / Berg strips / Header pins for necessary connections.  
12VDC power supply  

## About code
This python code has been tested on Ubuntu and Raspbian, hopefully will work on others too...  
Dependencies: pyaudio, numpy, struct (Optional: pygame, RPi.GPIO)

if pip install pyaudio doesn't work, try apt-get install python-pyaudio  

The code gets audio data with pyaudio and then uses numpy for fft operations & struct to get amplitudes for frequency ranges in array format. Then we get aggregated intensity over a range by adding the corresponding consecutive array elements (explained in code comments).  
You can then use the final values for either giving PWM on the same system or send to another system.  
There is also an option of using pygame for visualization. 
Setting the corresponding boolean variable as true will create a pygame window with three circles: Red, Green and Blue.  
The size of the circles is proportional to the aggregated intensity over the corresponding frequency ranges.
However using pygame might slow down performance a little thus decreasing responsiveness. So preferably use it for testing purposes.

PS:
This might have some bugs, Do let me know (hemanshu.kale@gmail.com) in case of any random problems / bugs

Enjoy :)



