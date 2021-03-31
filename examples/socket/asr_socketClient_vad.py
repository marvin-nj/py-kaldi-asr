# -*- coding: UTF-8 -*-
import socket
import pyaudio
import numpy as np
import time  
import logging

address = ('127.0.0.1', 8301)
DEBUG=1
SAMPLE_RATE = 8000
RECORD_SECONDS = 30  #录制时长，单位秒

frames = 30    #10,20,30， 单位毫秒
CHUNK=int(frames * SAMPLE_RATE /1000)    #240
FORMAT = pyaudio.paInt16
CHANNELS = 1

def start_client ():
    #socket init
    tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    tcpClient.connect(address)
    logging.info(" connect to  %s:%s OK"  %   (address[0], address[1]))

    #pyaudio init
    p = pyaudio.PyAudio()	
    stream = p.open(format=FORMAT,  channels=CHANNELS,  rate=SAMPLE_RATE, input=True, frames_per_buffer=CHUNK)  
    logging.info("Please speak.")

    #用最大录音时长控制循环，开始发送，收到结束标志后会自动跳出
    cnt=0
    msg=""
    for i in range(0, int(SAMPLE_RATE / CHUNK * RECORD_SECONDS)):
        samples = stream.read(CHUNK)
        try:
            tcpClient.send(samples)        #发送数据流
        except:
            break
        try:
            msg=tcpClient.recv(1024,0x40).decode("utf-8")         #接收返回结果
            if msg:
                logging.debug("result: %s " % msg)
        except Exception as e:
            logging.debug("No recv  warring : %s" % e)
            pass
        if len(msg) > 3 and msg[-3:] == "EOS":    #判断结束标志
            break
        cnt=cnt+1
        logging.debug ("audio length: %d,  send count : %d " %  (len(samples),cnt))
        #end  for
       
    #remove EOS symbol
    logging.info("final result:  %s "  % (msg[:-3]) )

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