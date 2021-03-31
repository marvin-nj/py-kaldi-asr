# -*- coding: UTF-8 -*-
import socket
import pyaudio
import numpy as np
import time  
import logging
address = ('127.0.0.1', 8301)
RATE = 8000
RECORD_SECONDS = 10  #录制时长，单位秒

FORMAT = pyaudio.paInt16
CHANNELS = 1
CHUNK=256
DEBUG=1

def start_client ():
    #socket init
    tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    tcpClient.connect(address)
    logging.info(" connect to %s:%s OK" % ( address[0],address[1]))

    #pyaudio init
    p = pyaudio.PyAudio()	
    stream = p.open(format=FORMAT,  channels=CHANNELS,  rate=RATE, input=True, frames_per_buffer=CHUNK)  #创建录音文件
    logging.info("Please speak.")

    #控制录音时长，开始发送
    cnt=0
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        samples = stream.read(CHUNK)
        #buff=np.float32(np.frombuffer(samples, dtype=np.int16))     #16为bytes转int
        tcpClient.send(samples)
        msg=tcpClient.recv(1024).decode("utf-8")
        if msg  != " ":
            logging.debug("result: %s " % msg)
        cnt=cnt+1
        logging.debug ("audio length: %d,  recv count : %d " %  (len(samples),cnt))
        #end  for

    #发送结束符号，长度为1值为0的数组,暂不支持其它
    eos=np.zeros(1)
    tcpClient.send(bytes(eos))
    msg=tcpClient.recv(1024).decode("utf-8")
    logging.info("final result:  %s "  % msg )

    #close socket and recording
    stream.stop_stream()
    stream.close()
    p.terminate()
    tcpClient.close()



if __name__ == '__main__':
    logfile="log.asr_server"
    if DEBUG:
        logging.basicConfig( filename = "", level=logging.DEBUG)
    else:
        logging.basicConfig( filename = "", level=logging.INFO)
    time_start = time.time()
    start_client()
    logging.info ( "** total time : %8.2fs" % ( time.time() - time_start ))