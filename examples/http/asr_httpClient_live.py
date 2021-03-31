#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# example program for kaldi live nnet3 chain online decoding
#
# configured for embedded systems (e.g. an rpi3) with models
# installed in /opt/kaldi/model/
#
#####
#Note
#this can support both 16k and 8k 
# modify the sampleRate of vad.py, PulseRecorder.py and asr.py  if you need
#path in /home/wangmanhong/.local/lib/python3.6/site-packages/nltools
####

import os
import sys
import logging
import traceback
import json
import struct
import requests
import datetime
from time import time
from optparse import OptionParser
from nltools               import misc
from nltools.pulserecorder import PulseRecorder
from nltools.vad           import VAD, BUFFER_DURATION


#recording
STREAM_ID                        = 'mic'
DEFAULT_VOLUME                   = 150
DEFAULT_AGGRESSIVENESS           = 2
MAX_UTT_LENGTH=8     #12 s
sampleRate = 8000     #8000

#socket
DEFAULT_HOST      = '192.168.7.59'
DEFAULT_PORT      = 8301

misc.init_app("kaldi_live_demo")
logging.basicConfig(level=logging.INFO)
#options
parser = OptionParser("usage: %prog [options]")

parser.add_option ("-a", "--aggressiveness", dest="aggressiveness", type = "int", default=DEFAULT_AGGRESSIVENESS,
                   help="VAD aggressiveness, default: %d" % DEFAULT_AGGRESSIVENESS)


parser.add_option ("-v", "--verbose", action="store_true", dest="verbose",
                   help="verbose output")

parser.add_option ("-s", "--source", dest="source", type = "string", default=None,
                   help="pulseaudio source, default: auto-detect")

parser.add_option ("-V", "--volume", dest="volume", type = "int", default=DEFAULT_VOLUME,
                   help="broker port, default: %d" % DEFAULT_VOLUME)

parser.add_option ("-H", "--host", dest="host", type = "string", default=DEFAULT_HOST,
                   help="host, default: %s" % DEFAULT_HOST)

parser.add_option ("-p", "--port", dest="port", type = "int", default=DEFAULT_PORT,
                   help="port, default: %d" % DEFAULT_PORT)

(options, args) = parser.parse_args()
url = 'http://%s:%d/decode' % (options.host, options.port)

if options.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)


source         = options.source
volume         = options.volume
aggressiveness = options.aggressiveness

 
rec = PulseRecorder(source_name=source, volume=volume,rate=sampleRate)
vad = VAD(aggressiveness=aggressiveness,sample_rate=sampleRate,max_utt_length=MAX_UTT_LENGTH)

#main 
frames=int(sampleRate * BUFFER_DURATION / 1000)      #BUFFER_DURATION 30
rec.start_recording(frames_per_buffer=frames)

time_start = time()
print("Please speak.")
total,buff_size,finalize=0,0,0
while True:

    samples = rec.get_samples()
    audio, finalize = vad.process_audio(samples)
    #print(len(samples),total,audio)
    if not audio:
        continue
    #logging.debug ('decoding audio len=%d finalize=%s audio=%s'% (len(audio), repr(finalize), audio[0].__class__))
    # decoding stop while  finalize is true, max_length 12s 
    buff_size=len(samples)
    #buff = struct.unpack_from('<%dh' % buff_size, audio)
    buff=tuple(audio)
    #print(len(buff))
    data = {'audio'      : buff, 
            'do_record'  : False, 
            'do_asr'     : True, 
            'do_finalize': finalize}

    response = requests.post(url, data=json.dumps(data))
    
    logging.debug("%6.3fs: %5d frames (%6.3fs) decoded, status=%d." % (time()-time_start, 
                                                                      buff_size, 
                                                                      float(buff_size) / float(sampleRate),
                                                                      response.status_code))
    

    assert response.status_code == 200
    data = response.json()
    logging.info ( "** result          : %s" % data['hstr'])

    if finalize:
        rec.stop_recording()
        print("")
        break
    total=total+1
    #end while

data = response.json()

logging.debug("raw response data: %s" % repr(data))

logging.info ( "*****************************************************************")
logging.info ( "** result          : %s" % data['hstr'])
logging.info ( "** confidence    : %f" % data['confidence'])
logging.info ( "** decoding time : %8.2fs" % ( time() - time_start ))
logging.info ( "*****************************************************************")



