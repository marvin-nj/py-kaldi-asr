#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2018 Guenter Bartsch
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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
import traceback
import logging
import datetime

from time                  import time
from nltools               import misc
from nltools.pulserecorder import PulseRecorder
from nltools.vad           import VAD, BUFFER_DURATION
from nltools.asr           import ASR, ASR_ENGINE_NNET3
from optparse              import OptionParser

PROC_TITLE                       = 'kaldi_live_demo'

DEFAULT_VOLUME                   = 150
DEFAULT_AGGRESSIVENESS           = 2

DEFAULT_MODEL_DIR                = 'data/models/kaldi-dianhua-cn-8k-2700h-tdnnf-baseline'
#DEFAULT_MODEL_DIR                = 'data/models/kaldi-generic-cn-16k-1wh-tdnnf-fun9_v1'
#DEFAULT_MODEL_DIR                = 'data/models/kaldi-generic-en-16k-1200h-tdnnf-r20190609'
DEFAULT_ACOUSTIC_SCALE           = 1.0
DEFAULT_BEAM                     = 7.0
DEFAULT_FRAME_SUBSAMPLING_FACTOR = 3

#vad
MAX_UTT_LENGTH=20      #12 s

STREAM_ID                        = 'mic'

#
# init
#

misc.init_app(PROC_TITLE)
logging.basicConfig(level=logging.INFO)

print("Kaldi live demo V0.3")

#
# cmdline, logging
#

parser = OptionParser("usage: %prog [options]")

parser.add_option ("-a", "--aggressiveness", dest="aggressiveness", type = "int", default=DEFAULT_AGGRESSIVENESS,
                   help="VAD aggressiveness, default: %d" % DEFAULT_AGGRESSIVENESS)

parser.add_option ("-m", "--model-dir", dest="model_dir", type = "string", default=DEFAULT_MODEL_DIR,
                   help="kaldi model directory, default: %s" % DEFAULT_MODEL_DIR)

parser.add_option ("-v", "--verbose", action="store_true", dest="verbose",
                   help="verbose output")

parser.add_option ("-s", "--source", dest="source", type = "string", default=None,
                   help="pulseaudio source, default: auto-detect")

parser.add_option ("-V", "--volume", dest="volume", type = "int", default=DEFAULT_VOLUME,
                   help="broker port, default: %d" % DEFAULT_VOLUME)

(options, args) = parser.parse_args()

if options.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

source         = options.source
volume         = options.volume
aggressiveness = options.aggressiveness
model_dir      = options.model_dir

#
# pulseaudio recorder
#

rec = PulseRecorder(source_name=source, volume=volume)

#
# VAD
#

vad = VAD(aggressiveness=aggressiveness,max_utt_length=MAX_UTT_LENGTH)

#
# ASR
#

print("Loading model from %s ...", model_dir)

asr = ASR(engine = ASR_ENGINE_NNET3, model_dir = model_dir,
          kaldi_beam = DEFAULT_BEAM, kaldi_acoustic_scale = DEFAULT_ACOUSTIC_SCALE,
          kaldi_frame_subsampling_factor = DEFAULT_FRAME_SUBSAMPLING_FACTOR)


#
# main
#

rec.start_recording()

print("Please speak.")
c=0
finalize=0
while True:

    samples = rec.get_samples()
    c=c+1

    #audio, finalize = vad.process_audio(samples)
    #if not audio:
    #    continue
    #logging.debug ('decoding audio len=%d finalize=%s audio=%s'% (len(audio), repr(finalize), audio[0].__class__))
    # decoding stop while  finalize is true, max_length 12s 
    user_utt, confidence = asr.decode(samples, finalize, stream_id=STREAM_ID)

    print(user_utt,c)
    if finalize:
        rec.stop_recording()
        print("")
        break



