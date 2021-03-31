#基于vad的asr服务端，主要功能：
#1、socket连接后，从客户端接收不间断的数据流
#2、用vad检测数据流的断点
#3、识别完成后返回带有"EOS"标识符结尾的识别结果，EOS表示服务端已断开本次连接
#4、识别结束后会继续保持监听状态

import socket
import numpy as np
import sys
import signal
import logging
import datetime 
#from threading import Thread 
from nltools.vad           import VAD, BUFFER_DURATION
sys.path.append(r'/wmh/py-kaldi-asr/kaldiasr')
from nnet3 import KaldiNNet3OnlineModel, KaldiNNet3OnlineDecoder

ADDRESS = ('0.0.0.0', 8301)
SAMPLE_RATE  = 8000 
DEBUG=1     #日志级别

frames=30    #webRTC vad 计算单位，只支持: 10,20,30
CHUNK=int(frames * SAMPLE_RATE /1000   * 2 )  #480      #必须为客户端chunk的两倍，因为数据是16位精度
DEFAULT_MODEL_DIR  = 'data/models/kaldi-dianhua-cn-8k-2700h-tdnnf-baseline'

#vad
MAX_UTT_LENGTH=10   #允许最大语音长度，单位秒
vad_level=2     #0: Normal，1：low Bitrate， 2：Aggressive；3：Very Aggressive 


#ctrl+C退出
def CtrlC():
    os._exit(0)

#处理单次连接
def oneConnection(client_socket, decoder,vad):
    do_finalize=0
    hstr=""
    #单个连接开始
    cnt=0
    samples=np.array(bytes(0))
    while not do_finalize   :
        
        try:
            samples = client_socket.recv(CHUNK)
        except Exception as e:
            logging.debug("recv error detail: %s" % e)
            pass
        buff=np.frombuffer(samples, dtype=np.int16)
       
        try:
            audio, do_finalize = vad.process_audio(buff)
        except Exception as e:
            logging.debug("vad error detail: %s" % e)
            break

        if not audio:
            continue
        decoder.decode(SAMPLE_RATE, np.float32(audio), do_finalize)
        hstr, confidence = decoder.get_decoded_string()
        if not hstr :
            hstr=" "
        else:
            logging.debug ( "result: %s" % hstr)  

        if do_finalize:
            #final result
            hstr=hstr.replace(" ", "").replace("<NOISE>", " ")
            hstr=hstr+"EOS"
            client_socket.send(hstr.encode("utf-8"))
            now_time = datetime.datetime.now().strftime('%F %T')
            logging.info("recv  %.2f seconds audio , at  time %s  "  %  (cnt*CHUNK/8000/2 , now_time))
            logging.info ( "** confidence:  %9.5f , final result: %s" % (confidence, hstr))  
            break
        
        try:
            client_socket.send(hstr.encode("utf-8"))
        except Exception as e:
            logging.debug("send error detail %s" % e)
            pass
        
        cnt=cnt+1
        logging.debug ("audio length: %d,  recv count : %d " %  (len(audio),cnt))
    #end  while


def server_start(decoder):
    tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      #TCP
    tcpServer.bind(ADDRESS)
    # 自动恢复监听
    while True:
        try:
            tcpServer.listen(1)     # 排队数
            # tcpServer.accept()返回一个元组, 元素1为客户端的socket对象, 元素2为客户端的地址(ip地址，端口号)
            client_socket, client_address= tcpServer.accept()
            logging.info("listen from %s : %s"  %  (client_address[0], client_address[1]))
        except (BlockingIOError, ConnectionResetError):
            pass
        vad = VAD(aggressiveness=vad_level,sample_rate=SAMPLE_RATE,max_utt_length=MAX_UTT_LENGTH)
        oneConnection(client_socket,  decoder , vad)
        #Thread(target=oneThread, args=(client_socket, client_address, decoder)).start()
    tcpServer.close()


def main():
    #INFO or DEBUG
    logfile="log.asr_server"
    if DEBUG:
        logging.basicConfig( filename = "", level=logging.DEBUG)
    else:
        logging.basicConfig( filename = "", level=logging.INFO)
    logging.info("loading asr model, please wait......")
    nnet3_model = KaldiNNet3OnlineModel (DEFAULT_MODEL_DIR, "model")
    decoder = KaldiNNet3OnlineDecoder (nnet3_model)
    logging.info("load model ok,  run your socket client  now")
    server_start(decoder)



if __name__ == '__main__':
    signal.signal(signal.SIGINT, CtrlC)
    signal.signal(signal.SIGTERM, CtrlC)
    main()