import os
import random
import xml.etree.ElementTree as ET

from utils.utils import get_classes

# --------------------------------------------------------------------------------------------------------------------------------#
#   annotation_mode用于指定该文件运行时计算的内容
#   annotation_mode为0代表整个标签处理过程，包括下面 1 and 2
#   annotation_mode为1代表获得  数据集 划分好的 训练集 验证集的  图片索引  train_index.txt、val_index.txt
#   annotation_mode为2代表  根据1获得的索引文件, 生成对应的每张图片的内容 训练用的   train.txt、val.txt
# --------------------------------------------------------------------------------------------------------------------------------#
annotation_mode = 0

# -------------------------------------------------------------------#
#   必须要修改，用于生成train.txt、val.txt的目标信息
#   与训练和预测所用的classes_path一致即可
#   如果生成的2007_train.txt里面没有目标信息
#   那么就是因为classes没有设定正确
# -------------------------------------------------------------------#
classes_path = 'model_data/cap_classes.txt'

# --------------------------------------------------------------------------------------------------------------------------------#
#   train_percent用于指定训练集与验证集的比例，默认情况下 训练集:验证集 = 9:1
# --------------------------------------------------------------------------------------------------------------------------------#

train_percent = 0.9

# -------------------------------------------------------#
#   指向当前要处理的数据集所在的文件夹
#   默认指向根目录下的当前要处理的数据集文件名
# -------------------------------------------------------#
devkit_path = 'CapData'

devkit_sets = ['train', 'val']
classes, _ = get_classes(classes_path)


def convert_annotation(image_id, list_file):
    in_file = open(os.path.join(devkit_path, 'Annotations/%s.xml' % image_id), encoding='utf-8')
    tree = ET.parse(in_file)
    root = tree.getroot()
    for obj in root.iter('object'):
        difficult = 0
        if obj.find('difficult') != None:
            difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult) == 1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (int(float(xmlbox.find('xmin').text)), int(float(xmlbox.find('ymin').text)),
             int(float(xmlbox.find('xmax').text)), int(float(xmlbox.find('ymax').text)))
        list_file.write(" " + ",".join([str(a) for a in b]) + ',' + str(cls_id))


if __name__ == "__main__":
    random.seed(0)
    if annotation_mode == 0 or annotation_mode == 1:
        print("Generate Index_txt.")
        xmlfilepath = os.path.join(devkit_path, 'Annotations')
        saveBasePath = os.path.join(devkit_path, 'Main')
        temp_xml = os.listdir(xmlfilepath)
        total_xml = []
        for xml in temp_xml:
            if xml.endswith(".xml"):
                total_xml.append(xml)

        num = len(total_xml)
        list = range(num)

        tr = int(num * train_percent)
        train = random.sample(list, tr)

        print("train size", tr)

        ftrain = open(os.path.join(saveBasePath, 'train_index.txt'), 'w')
        fval = open(os.path.join(saveBasePath, 'val_index.txt'), 'w')

        for i in list:
            name = total_xml[i][:-4] + '\n'
            if i in train:
                ftrain.write(name)
            else:
                fval.write(name)

        ftrain.close()
        fval.close()
        print("Generate Index_txt in %s/Main done." %devkit_path)

    if annotation_mode == 0 or annotation_mode == 2:
        print("Generate train.txt and val.txt for train.")
        for image_set in devkit_sets:
            image_ids = open(os.path.join(devkit_path, 'Main/%s_index.txt' %image_set),
                             encoding='utf-8').read().strip().split()
            list_file = open(os.path.join(devkit_path, 'Main/%s.txt' %image_set), 'w', encoding='utf-8')
            for image_id in image_ids:
                list_file.write('%s/JPEGImages/%s.jpg' % (os.path.abspath(devkit_path), image_id))

                convert_annotation(image_id, list_file)
                list_file.write('\n')
            list_file.close()
        print("Generate train.txt and val.txt in %s/Main done." %devkit_path)
