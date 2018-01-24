#coding:utf-8
'''
Created by huxiaoman 2017.11.08
mnist_data.py: extracing mnist dataset and create reader_creator to convert data format to train and test.
more can see in the paddlepaddle source code : https://github.com/PaddlePaddle/Paddle/blob/develop/python/paddle/v2/dataset/mnist.py
'''
import paddle.v2.dataset.common
import subprocess
import numpy
import platform
__all__ = ['train', 'test', 'convert']

URL_PREFIX = 'http://yann.lecun.com/exdb/mnist/'
TEST_IMAGE_URL = URL_PREFIX + 't10k-images-idx3-ubyte.gz'
TEST_IMAGE_MD5 = '9fb629c4189551a2d022fa330f9573f3'
TEST_LABEL_URL = URL_PREFIX + 't10k-labels-idx1-ubyte.gz'
TEST_LABEL_MD5 = 'ec29112dd5afa0611ce80d1b7f02629c'
TRAIN_IMAGE_URL = URL_PREFIX + 'train-images-idx3-ubyte.gz'
TRAIN_IMAGE_MD5 = 'f68b3c2dcbeaaa9fbdd348bbdeb94873'
TRAIN_LABEL_URL = URL_PREFIX + 'train-labels-idx1-ubyte.gz'
TRAIN_LABEL_MD5 = 'd53e105ee54ea40749a09fcbcd1e9432'

def reader_creator(image_filename, label_filename, buffer_size):
    # 创建一个reader
    def reader():
        if platform.system() == 'Darwin':
            zcat_cmd = 'gzcat'
        elif platform.system() == 'Linux':
            zcat_cmd = 'zcat'
        else:
            raise NotImplementedError()

        m = subprocess.Popen([zcat_cmd, image_filename], stdout=subprocess.PIPE)
        m.stdout.read(16)  

        l = subprocess.Popen([zcat_cmd, label_filename], stdout=subprocess.PIPE)
        l.stdout.read(8)  

        try:  # reader could be break.
            while True:
                labels = numpy.fromfile(
                    l.stdout, 'ubyte', count=buffer_size).astype("int")

                if labels.size != buffer_size:
                    break  # numpy.fromfile returns empty slice after EOF.

                images = numpy.fromfile(
                    m.stdout, 'ubyte', count=buffer_size * 28 * 28).reshape(
                        (buffer_size, 28 * 28)).astype('float32')

                images = images / 255.0 * 2.0 - 1.0

                for i in xrange(buffer_size):
                    yield images[i, :], int(labels[i])
        finally:
            m.terminate()
            l.terminate()

    return reader

def train():
    """
    创建mnsit的训练集 reader creator
    返回一个reador creator，每个reader里的样本都是图片的像素值，在区间[0,1]内，label为0~9
    返回：training reader creator
    """
    return reader_creator(
        paddle.v2.dataset.common.download(TRAIN_IMAGE_URL, 'mnist',
                                          TRAIN_IMAGE_MD5),
        paddle.v2.dataset.common.download(TRAIN_LABEL_URL, 'mnist',
                                          TRAIN_LABEL_MD5), 100)


def test():
    """
    创建mnsit的测试集 reader creator
    返回一个reador creator，每个reader里的样本都是图片的像素值，在区间[0,1]内，label为0~9
    返回：testreader creator
    """
    return reader_creator(
        paddle.v2.dataset.common.download(TEST_IMAGE_URL, 'mnist',
                                          TEST_IMAGE_MD5),
        paddle.v2.dataset.common.download(TEST_LABEL_URL, 'mnist',
                                          TEST_LABEL_MD5), 100)

def fetch():
    paddle.v2.dataset.common.download(TRAIN_IMAGE_URL, 'mnist', TRAIN_IMAGE_MD5)
    paddle.v2.dataset.common.download(TRAIN_LABEL_URL, 'mnist', TRAIN_LABEL_MD5)
    paddle.v2.dataset.common.download(TEST_IMAGE_URL, 'mnist', TEST_IMAGE_MD5)
    paddle.v2.dataset.common.download(TEST_LABEL_URL, 'mnist', TRAIN_LABEL_MD5)


def convert(path):
    """
    将数据格式转换为 recordio format
    """
    paddle.v2.dataset.common.convert(path, train(), 1000, "minist_train")
    paddle.v2.dataset.common.convert(path, test(), 1000, "minist_test")


