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
import pyaudio
import numpy as np

#socket
DEFAULT_HOST      = 'localhost'
DEFAULT_PORT      = 8301

#recording
CHUNK = 360
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000
RECORD_SECONDS = 5  #录制时长 s


def test():
    url = 'http://%s:%d/decode' % (DEFAULT_HOST, DEFAULT_PORT)
    time_start = time()
    total,buff_size,finalize=0,0,0
    p = pyaudio.PyAudio()	#初始化
    stream = p.open(format=FORMAT,  channels=CHANNELS,  rate=RATE, input=True, frames_per_buffer=CHUNK)  #创建录音文件
    print("Please speak.")

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        samples = stream.read(CHUNK)
        buff=np.float64(np.frombuffer(samples, dtype=np.int16))     #16为bytes转int
        #buff = struct.unpack_from('<%dh' % buff_size, samples)
        buff=tuple(buff)
        buff_size=len(buff)

        if (i+2) > int(RATE / CHUNK * RECORD_SECONDS):
            finalize = 1

        data = {'audio'      : buff,  'do_record'  : False,  'do_asr'     : True,  'do_finalize': finalize}
        
        response = requests.post(url, data=json.dumps(data))
        logging.debug("%6.3fs: %5d frames (%6.3fs) decoded, status=%d." % (time()-time_start,  buff_size, float(buff_size) / float(RATE),  response.status_code))
    
        assert response.status_code == 200
        data = response.json()
        logging.info ( "** result          : %s" % data['hstr'])
    
    #end for

    stream.stop_stream()
    stream.close()
    p.terminate()
    
    data = response.json()
    logging.debug("raw response data: %s" % repr(data))
    logging.info ( "*****************************************************************")
    logging.info ( "** result          : %s" % data['hstr'])
    logging.info ( "** confidence    : %f" % data['confidence'])
    logging.info ( "** decoding time : %8.2fs" % ( time() - time_start ))
    logging.info ( "*****************************************************************")



if __name__ == '__main__':
    parser = OptionParser("usage: %prog [options]")
    #logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    test()