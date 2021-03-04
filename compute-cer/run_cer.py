# from base.common import create_logger
# from base.timem import ts, te
from error_rate import char_errors, word_errors
from atc import n2c
import util_func
import datetime
import os
import shutil
import sys

if len(sys.argv) != 3:
    print("usage: sys.argv[0] textRef textHyp")
    sys.exit()


NUM2CH = True # 是否把阿拉伯数字转成中文数字
RM_NUM = False  # 删除数字
KEEP_BLANK = False


g_errors_sum, g_len_refs, g_file_cnt, g_time_total = 0.0, 0, 0, 0
realtime_errors_sum, realtime_len_refs, realtime_file_cnt, realtime_time_total = 0.0, 0, 0, 0
realtime_realtime_ratio, realtime_wav_length = 0, 0

def preprocess(s):
    s = s.strip()
    s = s.lower()
    if RM_NUM:
        s = re.sub(r'\d+', '', s)
    elif NUM2CH:
        s = n2c(s, twoalt=False)

    s = util_func.rm_flags(s, keep_blank=KEEP_BLANK)
    return s

txt_true_path = sys.argv[1]
txt_predict_path = sys.argv[2]
wav_folder = 'tongyong'
target_path = "/home/guiji/asr_test/360-liantong/"
source_path = "/media/guiji/edba908e-773a-4fa9-8170-8fa92fed0f93/haie/wav_dataset/通用keyword/all/"
# good_wav = open('good_wav.txt', 'w')
def do_iat_1order():
    global g_errors_sum, g_len_refs, g_file_cnt, g_time_total
    global realtime_errors_sum, realtime_len_refs, realtime_file_cnt, realtime_time_total
    global realtime_realtime_ratio, realtime_wav_length

    file_cnt, time_total = 0, 0
    errors_sum, len_refs = 0.0, 0
    errors_insert, errors_del,errors_sub=0.0, 0.0, 0.0
    # for file in os.listdir(wav_folder):
    #     wav_file_path = os.path.join(wav_folder, file)
    #     if any(wav_file_path.lower().endswith("." + ext) for ext in ["wav"]):
 
    # ----------------------------------------
    start_time = datetime.datetime.now()

    true_fn_labels_map = util_func.get_label_true_mark_sys_many(txt_true_path)
    pred_fn_labels_map = util_func.get_label_true_mark_sys_many(txt_predict_path)
    # for (x_true, x_predict) in zip (labels_true, labels_predict):
    for wav_file_path in true_fn_labels_map.keys():
    	x_true, x_predict = true_fn_labels_map.get(wav_file_path), pred_fn_labels_map.get(wav_file_path)
    	if x_true != None and x_predict != None:
        	print(wav_file_path)
        	file_cnt += 1
        	label_true = preprocess(x_true)
        	label_predict = preprocess(x_predict)
        	label_predict = label_predict.replace('noise', '')
        	label_predict = label_predict.replace('unk', '')

        	print("groundtruth label: %s\npredict     label: %s" % (label_true, label_predict))

        	# errors, len_ref = word_errors(label_true, label_predict)
        	#errors, len_ref = char_errors(label_true, label_predict)
        	err_insert, err_del, err_sub, len_ref = char_errors(label_true, label_predict)
        	errors=err_insert + err_del + err_sub
        	cer = errors / len_ref
        	print("insert: %d ; del %d ; sub %d ;  len: %d ; cer = %f\n" %(err_insert,err_del,err_sub, len_ref, cer))
        	# if cer < 0.02:
        	# # 	shutil.move((source_path+wav_file_path+'.wav'), target_path)
        	# 	with open(target_path + '360_liantong_good_new.txt', 'a') as f:
        	# 		f.write(wav_file_path + ' ' + label_true + '\n')
        	errors_insert += err_insert
        	errors_del    += err_del
        	errors_sub    += err_sub
        	errors_sum    += errors
        	len_refs      += len_ref
                # if cer < 0.03:
    	# 	good_wav.write(wav_file_path + '\n')

    print('{0} wavs,CER {1:.4%} [{2}/{3}, {4} ins, {5} del, {6} sub]'.format(file_cnt, errors_sum / len_refs , errors_sum, len_refs, errors_insert, errors_del, errors_sub))


def main():
	do_iat_1order()
	# good_wav.close()
    # base_dir = os.path.join(cur_dir, "test_wav")
    # dir_list = ["326", "dataTang", "SZJ", "hard"]
    # dir_list = ["2018062102_8k_9890"]
    # dir_list = ["err77"]
    # dir_list = ['data-en']
    # dir_list = ['mozilla-v1-test_16k']
    # dir_list = ['20180918']

    # for cur_dirname in dir_list:
    #     print('current  process  dirname:  ', cur_dirname)
    #     cur_folder = os.path.join(base_dir, cur_dirname)
    #     do_iat_1order(cur_folder)
    # print('==========================================')
    # print("Total error rate [cer] for all(%d wavs) = %f" % (g_file_cnt, g_errors_sum / g_len_refs))
    # print("Total avg time %d/%d = %f ms" % (g_time_total, g_file_cnt, g_time_total / float(g_file_cnt)))

if __name__ == '__main__':
    main()
