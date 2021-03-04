# -*- coding: utf-8 -*-
"""Evaluation for DeepSpeech2 model."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os, re
import codecs
# import soundfile
import json

exts = ["wav"]


def rm_flags_only_mandaran(sentence):
    if sentence is not None:
        out_str = ""
        xx = u"([\u4e00-\u9fff]+)"
        pattern = re.compile(xx)
        results = pattern.findall(sentence.decode("utf-8"))
        for result in results:
            out_str += result
        return out_str.encode("utf-8")
    else:
        return ""


def rm_flags(sentence, keep_blank=False):
    if sentence is not None:
        if keep_blank:
            sentence = re.sub(r'\s+', "__I_AM_BLANK__", sentence)

        # 分词时候去除特殊符号 解决 讯飞识别出结果 "|我需要钱"，分词错误问题
        specific_symbol = u'\W'  # \W	匹配非字符、非汉字、非下划线和非数字
        sentence1 = re.sub(specific_symbol, "", sentence)  # 去除特殊符号，保留下划线

        if keep_blank:
            sentence1 = sentence1.replace('__I_AM_BLANK__', ' ')
            sentence1 = re.sub(r'\s+', ' ', sentence1)

        sentence1 = sentence1.replace("_", "")  # 去除下划线

        if keep_blank:
            sentence1 = re.sub(r'\s+', ' ', sentence1)

        return sentence1
    else:
        return ""


# 测试匹配中文信息
def TestReChinese():
    temp = u"数据结构模版----单链表SimpleLinkList[带头结点&&面向对象设计思想](C语言实现)"
    # temp = source.decode('utf8')
    print("同时匹配中文英文")

    xx = u"([\w\W\u4e00-\u9fff]+)"
    pattern = re.compile(xx)
    results = pattern.findall(temp)
    for result in results:
        print(result)
    print("只匹配中文")
    xx = u"([\u4e00-\u9fff]+)"
    pattern = re.compile(xx)
    results = pattern.findall(temp)
    for result in results:
        print(result)


def get_label_true_mark_sys(txt_file):
    if os.path.exists(txt_file):
        label_true = ''
        line_cnt = 0
        with open(txt_file, 'r') as fr:
            for line in fr:
                line_cnt += 1
                if line_cnt == 1:
                    label_true = line.strip()
                else:
                    break
    else:
        label_true = os.path.basename(txt_file.replace(".txt", ""))

    label_true = label_true.lower()
    return label_true


def get_label_true_mark_sys_many(txt_file):
    r = []

    with open(txt_file, 'r') as fr:
        for line in fr:
            ss = line.split('\t')
            fn = ss[0].strip()
            if len(ss) > 1:
                # print('line:', line)
                # print('ss:      ', ss)
                tt = ' '.join(ss[1:]) # chinese format
                # tt = ' '.join(ss[1:])
                label_true = tt.strip().lower()
            else:
                label_true = ''
            r.append((fn, label_true))

    return dict(r)


def create_manifest(data_dir, manifest_path):
    """Create a manifest json file summarizing the data set, with each line
    containing the meta data (i.e. audio filepath, transcription text, audio
    duration) of each audio file within the data set.
    """
    # print("Creating manifest %s ..." % manifest_path)
    json_lines = []
    if os.path.isdir(data_dir):
        for file in os.listdir(data_dir):
            wav_file_path = os.path.join(data_dir, file)
            if any(wav_file_path.lower().endswith("." + ext) for ext in exts):
                labels_file_path = wav_file_path.replace('.wav', '.txt')
                label_true = get_label_true_mark_sys(labels_file_path)
                audio_data, samplerate = soundfile.read(wav_file_path)
                duration = float(len(audio_data)) / samplerate
                json_lines.append(
                    json.dumps({
                        'audio_filepath': wav_file_path,
                        'duration': duration,
                        'text': label_true
                    }))
    elif os.path.isfile(data_dir):
        wav_file_path = data_dir
        labels_file_path = data_dir.replace('.wav', '.txt')
        label_true = get_label_true_mark_sys(labels_file_path)
        audio_data, samplerate = soundfile.read(wav_file_path)
        duration = float(len(audio_data)) / samplerate
        json_lines.append(
            json.dumps({
                'audio_filepath': wav_file_path,
                'duration': duration,
                'text': label_true
            }))
    with codecs.open(manifest_path, 'w', 'utf-8') as out_file:
        for line in json_lines:
            out_file.write(line + '\n')


def file_2_mainfest(input_string):
    input_str = os.path.abspath(input_string)
    manifest_path = ""
    if os.path.isfile(input_str):
        if input_str.endswith(".wav"):
            manifest_path = input_str.replace(".wav", ".manifest")
            create_manifest(input_str, manifest_path)
    elif os.path.isdir(input_str):
        manifest_path = input_str + ".manifest"
        create_manifest(input_str, manifest_path)
    else:
        pass
    return manifest_path


def test_rm_flags():
    s = 'mrs. jason is on       the     p__hone'
    r = rm_flags(s, keep_blank=False)
    print('result:', r)


def main():
    test_rm_flags()


if __name__ == '__main__':
    main()
