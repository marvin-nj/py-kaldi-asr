#asr服务端，主要功能：
#1、接收一定长度的数据流，客户端发送流结束标志
#2、边识别，边返回结果，收到结束标志后返回最好的结果

import socket
import numpy as np
import sys
import signal
import logging
import datetime 
#from threading import Thread 

sys.path.append(r'/wmh/py-kaldi-asr/kaldiasr')
from nnet3 import KaldiNNet3OnlineModel, KaldiNNet3OnlineDecoder


ADDRESS = ('0.0.0.0', 8301)
DEFAULT_MODEL_DIR  = 'data/models/kaldi-dianhua-cn-8k-2700h-tdnnf-baseline'
CHUNK = 256 * 2       #必须为客户端chunk的两倍，因为数据是16位精度
SAMPLE_RATE  = 8000   
DEBUG=1     #日志级别

#ctrl+C退出
def CtrlC():
    os._exit(0)


#处理单次连接
def oneConnection(client_socket, decoder):
    do_finalize=0
    hstr=""
    audio = client_socket.recv(CHUNK)
    #单个连接开始
    cnt=1
    while len(audio) ==  CHUNK  :
        #logging(audio)
        decoder.decode(SAMPLE_RATE, np.float32(np.frombuffer(audio, dtype=np.int16)), do_finalize)
        hstr, confidence = decoder.get_decoded_string()
        if not hstr:
            hstr=" "
        else:
            logging.debug ( "result: %s" % hstr)  
        try:
            client_socket.send(hstr.encode("utf-8"))
        except Exception as e:
            logging.debug("send error detail %s" % e)
            pass
        try:
            audio = client_socket.recv(CHUNK)
        except Exception as e:
            logging.debug("recv error detail: %s" % e)
            pass
        cnt=cnt+1
        logging.debug ("audio length: %d,  recv count : %d " %  (len(audio),cnt))
    #end  while
    #final result
    decoder.decode(SAMPLE_RATE,np.float32(np.frombuffer(audio, dtype=np.int16)), 1)
    hstr, confidence = decoder.get_decoded_string()
    hstr=hstr.replace(" ", "").replace("<NOISE>", " ")
    client_socket.send(hstr.encode("utf-8"))
    now_time = datetime.datetime.now().strftime('%F %T')
    logging.info("recv  %.2f seconds audio , at  time %s  "  %  (cnt*CHUNK/8000/2 , now_time))
    logging.info ( "** confidence:  %9.5f , final result: %s" % (confidence, hstr))  


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
        oneConnection(client_socket,  decoder)
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