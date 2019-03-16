from baseline_aug import get_unet
from glob import glob
from PIL import Image
from skimage.transform import resize
import numpy as np
from matplotlib import pyplot as plt
from skimage.morphology import label
from pycocotools import mask as maskUtils
from tqdm import tqdm
import os
import cv2
from keras.layers import ReLU
from sklearn.metrics import roc_auc_score


batchsize = 4
input_shape = (576, 576)


def batch(iterable, n=batchsize):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def read_input(path):
    x = np.array(Image.open(path))/255.
    return x


def read_gt(path):
    x = np.array(Image.open(path))/255.
    return x[..., np.newaxis]

if __name__ == '__main__':
    model_name = "baseline_unet_aug_do_0.1_activation_ReLU_"


    val_data = list(zip(sorted(glob('../input/DRIVE/test/images/*.tif')),
                          sorted(glob('../input/DRIVE/test/1st_manual/*.gif'))))

    try:
        os.makedirs("../output/"+model_name+"test/", exist_ok=True)
    except:
        pass

    model = get_unet(do=0.1, activation=ReLU)

    file_path = model_name + "weights.best.hdf5"

    model.load_weights(file_path, by_name=True)

    gt_list = []
    pred_list = []

    for batch_files in tqdm(batch(val_data), total=len(val_data)//batchsize):

        imgs = [resize(read_input(image_path[0]), input_shape) for image_path in batch_files]
        masks = [read_gt(image_path[1]) for image_path in batch_files]

        imgs = np.array(imgs)

        pred = model.predict(imgs)

        pred_all = (pred)

        pred = np.clip(pred, 0, 1)

        for i, image_path in enumerate(batch_files):

            pred_ = pred[i, :, :, 0]
            pred_ = resize(pred_, (584, 565))

            gt_list += masks[i].ravel().tolist()
            pred_list += pred_.ravel().tolist()

            pred_ = 255.*(pred_ - np.min(pred_))/(np.max(pred_)-np.min(pred_))

            print(np.max(pred_), np.min(pred_))
            image_base = image_path[0].split("/")[-1]

            cv2.imwrite("../output/"+model_name+"test/"+image_base, pred_)

    print(len(gt_list), len(pred_list))
    print("AUC ROC : ", roc_auc_score(gt_list, pred_list))