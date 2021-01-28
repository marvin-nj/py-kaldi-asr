一、基本依赖安装和解决(基于python3安装)
1.sudo apt-get update

2.sudo apt-get install pkg-config

3.sudo apt install libatlas-dev & sudo apt install libatlas3-base

二、py-kaldi-asr 安装
1.git clone https://github.com/gooofy/py-kaldi-asr.git

2.将kaldi-asr.pc(需要修改里面自己kaldi环境的绝对路径) 和atlas.pc 放入 /usr/lib/pkgconfig下，如没有pkgconfig文件夹新建一个

3.make -j8（修改Makefile里的python为python3）

4.编译的过程中可能会遇到/usr/bin/ld: cannot find -latlas解决方法：
将/usr/lib/libatlas.so.3 软链接到/usr/lib/libatlas.so上
ln -s libatlas.so.3 libatlas.so

三、添加kaldi环境
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/wmh/kaldi/src/lib:/wmh/kaldi/tools/openfst/lib
export LD_PRELOAD=/opt/intel/mkl/lib/intel64/libmkl_def.so:/opt/intel/mkl/lib/intel64/libmkl_avx2.so:/opt/intel/mkl/lib/intel64/libmkl_core.so:/opt/intel/mkl/lib/intel64/libmkl_intel_lp64.so:/opt/intel/mkl/lib/intel64/libmkl_intel_thread.so:/opt/intel/lib/intel64_lin/libiomp5.so

四、运行时错误
1、找不到kaldiasr时，在python的开始部分加入sys.path.append(r'/wmh/py-kaldi-asr/kaldiasr'), 主要是要把.so库的路径加载到python模块中
2、在chain_live.py中， 默认只能16k实时解码，需要8k支持的话，修改vad.py、 kaldi.py和PulseRecorder.py中的采样率即可，路径参考 ：/home/wangmanhong/.local/lib/python3.6/site-packages/nltools
