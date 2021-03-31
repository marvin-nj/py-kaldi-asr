#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# very basic example client for our example speech asr server
#


import os
import sys
import logging
import traceback
import json
import wave
import struct
import requests

from time import time
from optparse import OptionParser

DEFAULT_HOST      = 'localhost'
DEFAULT_PORT      = 8301
#
# commandline
#

parser = OptionParser("usage: %prog [options] foo.wav")

parser.add_option ("-v", "--verbose", action="store_true", dest="verbose",
                   help="verbose output")

parser.add_option ("-H", "--host", dest="host", type = "string", default=DEFAULT_HOST,
                   help="host, default: %s" % DEFAULT_HOST)

parser.add_option ("-p", "--port", dest="port", type = "int", default=DEFAULT_PORT,
                   help="port, default: %d" % DEFAULT_PORT)


(options, args) = parser.parse_args()

if options.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)

if len(args) != 1:
    parser.print_help()
    sys.exit(1)

wavfn = args[0]

url = 'http://%s:%d/decode' % (options.host, options.port)

#
# read samples from wave file, hand them over to asr server incrementally to simulate online decoding
#

time_start = time()

wavf = wave.open(wavfn, 'rb')

# check format
assert wavf.getnchannels()==1
assert wavf.getsampwidth()==2

# process file in 250ms chunks

chunk_frames =int( 250 * wavf.getframerate() / 1000)
tot_frames   = wavf.getnframes()
num_frames = 0
while num_frames < tot_frames:

    finalize = False
    if (num_frames + chunk_frames) < tot_frames:
        nframes = chunk_frames
    else:
        nframes = tot_frames - num_frames
        finalize = True

    frames = wavf.readframes(nframes)
    num_frames += nframes
    print(nframes)
    samples = struct.unpack_from('<%dh' % nframes, frames)     #h->short,16b

    data = {'audio'      : samples, 
            'do_record'  : False, 
            'do_asr'     : True, 
            'do_finalize': finalize}

    response = requests.post(url, data=json.dumps(data))

    logging.info("%6.3fs: %5d frames (%6.3fs) decoded, status=%d." % (time()-time_start, 
                                                                      num_frames, 
                                                                      float(num_frames) / float(wavf.getframerate()),
                                                                      response.status_code))
    assert response.status_code == 200


wavf.close()

data = response.json()

logging.debug("raw response data: %s" % repr(data))

logging.info ( "*****************************************************************")
logging.info ( "** waveName         : %s" % wavfn)
logging.info ( "** asrResult          : %s" % data['hstr'])
logging.info ( "** confidence    : %f" % data['confidence'])
logging.info ( "** decoding time : %8.2fs" % ( time() - time_start ))
logging.info ( "** duration      : %f" % (wavf.getnframes()/wavf.getframerate()))
logging.info ( "*****************************************************************")
