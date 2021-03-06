# -*- coding: utf-8 -*-
"""japan.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FZa04wA-DZ0jKrAsc3K9gxcOKjbq8DKX
"""

#kobler opp min drive til colab
from google.colab import drive
import os
drive.mount('/content/drive')
WORKING_DIRECTORY= '/content/drive/My Drive/workingDir_2020/'
os.chdir(WORKING_DIRECTORY)
os.getcwd()
!ls

# Commented out IPython magic to ensure Python compatibility.
import shutil
import os, sys, random
import xml.etree.ElementTree as ET
from glob import glob
import pandas as pd
from shutil import copyfile
import pandas as pd
from sklearn import preprocessing, model_selection
import matplotlib.pyplot as plt
# %matplotlib inline
from matplotlib import patches
import numpy as np
import os

# Commented out IPython magic to ensure Python compatibility.
 %%time
 #xml til csv
 annotations = sorted(glob(WORKING_DIRECTORY+'train/Japan/annotations/xmls/*.xml'))
 df = []
 cnt = 0
 for file in annotations:
   prev_filename = file.split('/')[-1].split('.')[0] + '.jpg'
   filename = str(cnt) + '.jpg'
   row = []
   parsedXML = ET.parse(file)
   for node in parsedXML.getroot().iter('object'):
     #blood_cells = node.find('name').text
     road_damage = node.find('name').text
     xmin = int(node.find('bndbox/xmin').text)
     xmax = int(node.find('bndbox/xmax').text)
     ymin = int(node.find('bndbox/ymin').text)
     ymax = int(node.find('bndbox/ymax').text)
 
     row = [prev_filename, filename, road_damage, xmin, xmax, ymin, ymax]
     df.append(row)
   cnt += 1
# 
 data = pd.DataFrame(df, columns=['prev_filename', 'filename', 'class', 'xmin', 'xmax', 'ymin', 'ymax'])
 #Gjør om til hva vi har over og under
 data[['prev_filename','filename', 'class', 'xmin', 'xmax', 'ymin', 'ymax']].to_csv(WORKING_DIRECTORY+'roadDetection_japan.csv', index=False)
 data.head(10)

#Sjekker hvor mange klasser vi har
classes=pd.read_csv(WORKING_DIRECTORY+'roadDetection_japan.csv', usecols=['class'])
y_max=pd.read_csv(WORKING_DIRECTORY+'roadDetection_japan.csv', usecols=['ymax'])
x_max=pd.read_csv(WORKING_DIRECTORY+'roadDetection_japan.csv', usecols=['xmax'])

#gjør om kolonnen til en string
y_max_list=y_max.to_string(header=None, index=False).strip('\n').split('\n')
x_max_list=x_max.to_string(header=None, index=False).strip('\n').split('\n')
labels=classes.to_string(header=None, index=False).strip('\n').split('\n')

#samler verdiene og sorterer.
x_max_list=','.join(set(x_max_list))
y_max_list=','.join(set(y_max_list))
labels=','.join(set(labels))
print('Labels: ',labels)
print('ymax values: ',y_max_list)
print('xmax values: ',x_max_list)

def extractMaximum(ss): 
    num, res = 0, 0
      
    # start traversing the given string  
    for i in range(len(ss)): 
          
        if ss[i] >= "0" and ss[i] <= "9": 
            num = num * 10 + int(int(ss[i]) - 0) 
        else: 
            res = max(res, num) 
            num = 0
          
    return max(res, num) 
  
#finner maximum verdien av listen, listen er en string
y_max_list=extractMaximum(y_max_list)
x_max_list=extractMaximum(x_max_list)

print('y_max_list= ', y_max_list)
print('x_max_list= ', x_max_list)

img_width = 1080  
img_height = 1080 

def width(df):
  return abs(int(df.xmax - df.xmin))
def height(df):
  return abs(int(df.ymax - df.ymin))
def x_center(df):
  return abs(int(df.xmin + (df.width/2)))
def y_center(df):
  return abs(int(df.ymin + (df.height/2)))
def w_norm(df):
  return df/img_width
def h_norm(df):
  return df/img_height

#Sett inn riktig path
df = pd.read_csv(WORKING_DIRECTORY+'roadDetection_japan.csv')

#Skift cell_type med vårt.
le = preprocessing.LabelEncoder()
le.fit(df['class']) #HER
print(le.classes_)
labels = le.transform(df['class']) #HER
df['labels'] = labels

df['width'] = df.apply(width, axis=1)
df['height'] = df.apply(height, axis=1)

df['x_center'] = df.apply(x_center, axis=1)
df['y_center'] = df.apply(y_center, axis=1)

df['x_center_norm'] = df['x_center'].apply(w_norm)
df['width_norm'] = df['width'].apply(w_norm)

df['y_center_norm'] = df['y_center'].apply(h_norm)
df['height_norm'] = df['height'].apply(h_norm)

df.head(10)

#sjekker hva maximum verdien er til ulike rader, alle normaliserte verdier skal være mellom 0 og 1
df_x=df['x_center_norm']
df_y=df['y_center_norm']
df_w=df['width_norm']
df_h=df['height_norm']

print('maximum x_norm value = ',df_x.max())
print('maximum y_norm value = ',df_y.max())
print('maximum width_norm value = ',df_w.max())
print('maximum height_norm value = ',df_h.max())

df_train, df_valid = model_selection.train_test_split(df, test_size=0.2, random_state=13, shuffle=True)
print(df_train.shape, df_valid.shape)

#GJØR OM TIL VÅRE PATHS
os.mkdir(WORKING_DIRECTORY+'rdd/')
os.mkdir(WORKING_DIRECTORY+'rdd/images/')
os.mkdir(WORKING_DIRECTORY+'rdd/images/train/')
os.mkdir(WORKING_DIRECTORY+'rdd/images/valid/')

os.mkdir(WORKING_DIRECTORY+'rdd/labels/')
os.mkdir(WORKING_DIRECTORY+'rdd/labels/train/')
os.mkdir(WORKING_DIRECTORY+'rdd/labels/valid/')

def segregate_data(df, img_path, label_path, train_img_path, train_label_path):
  filenames = []
  for filename in df.filename:
    filenames.append(filename)
  filenames = set(filenames)
  
  for filename in filenames:
    yolo_list = []

    for _,row in df[df.filename == filename].iterrows():
      yolo_list.append([row.labels, row.x_center_norm, row.y_center_norm, row.width_norm, row.height_norm])

    yolo_list = np.array(yolo_list)
    txt_filename = os.path.join(train_label_path,str(row.prev_filename.split('.')[0])+".txt")
    # Save the .img & .txt files to the corresponding train and validation folders
    np.savetxt(txt_filename, yolo_list, fmt=["%d", "%f", "%f", "%f", "%f"])
    shutil.copyfile(os.path.join(img_path,row.prev_filename), os.path.join(train_img_path,row.prev_filename))

!pwd

# Commented out IPython magic to ensure Python compatibility.
# %%time
# # Sett inn riktig PATH
# src_img_path = WORKING_DIRECTORY+"train/Japan/images/"
# src_label_path = WORKING_DIRECTORY+"train/Japan/annotations/xmls/"
# 
# train_img_path = WORKING_DIRECTORY+ "rdd/images/train"
# train_label_path = WORKING_DIRECTORY+"rdd/labels/train"
# 
# valid_img_path = WORKING_DIRECTORY+"rdd/images/valid"
# valid_label_path = WORKING_DIRECTORY+"rdd/labels/valid"
# 
# segregate_data(df_train, src_img_path, src_label_path, train_img_path, train_label_path)
# segregate_data(df_valid, src_img_path, src_label_path, valid_img_path, valid_label_path)

# Sett inn riktig PATH
try:
  shutil.rmtree(WORKING_DIRECTORY+'rdd/images/train/.ipynb_checkpoints')
except FileNotFoundError:
  pass

try:
  shutil.rmtree(WORKING_DIRECTORY+'rdd/images/valid/.ipynb_checkpoints')
except FileNotFoundError:
  pass

try:
  shutil.rmtree(WORKING_DIRECTORY+'rdd/labels/train/.ipynb_checkpoints')
except FileNotFoundError:
  pass

try:
  shutil.rmtree(WORKING_DIRECTORY+'rdd/labels/valid/.ipynb_checkpoints')
except FileNotFoundError:
  pass

print("No. of Training images", len(os.listdir(WORKING_DIRECTORY+'rdd/images/train')))
print("No. of Training labels", len(os.listdir(WORKING_DIRECTORY+'rdd/labels/train')))

print("No. of valid images", len(os.listdir(WORKING_DIRECTORY+'rdd/images/valid')))
print("No. of valid labels", len(os.listdir(WORKING_DIRECTORY+'rdd/labels/valid')))

#Gjør om PATH
!mkdir -p '/content/drive/My Drive/Machine Learning Projects/YOLO/'
!cp -r '/content/drive/My Drive/workingDir_2020/rdd' '/content/drive/My Drive/Machine Learning Projects/YOLO/'

!git clone  'https://github.com/ultralytics/yolov5.git'

#os.mkdir(WORKING_DIRECTORY+'yolov5')
!pip install -qr '/content/drive/My Drive/workingDir_2020/yolov5/requirements.txt'  # install dependencies

# Gjør om PATH og legge in riktig klasse navn og nummer der det står 5 og gjøre om bcc til et eller annet
!echo -e 'train: /content/drive/My Drive/workingDir_2020/rdd/images/train\nval: /content/drive/My Drive/workingDir_2020/rdd/images/valid\n\nnc: 7\nnames: ['D10', 'D20', 'D00', 'D44', 'D50', 'D43','D40']' >> rdd.yaml
!cat 'rdd.yaml'

# Gjør om PATH
shutil.copyfile(WORKING_DIRECTORY+'rdd.yaml', WORKING_DIRECTORY+'yolov5/rdd.yaml')

#Her bytter vi antall klasser til våre egne, standard klasser som eksisterer i alle yolo versjonene er 80 klasser
#Endring av klassen fra 80 til f.eks. skjer som vist under:
!sed -i 's/nc: 80/nc: 7/g' ./yolov5/models/yolov5s.yaml

"""**Training Parameters**

!python 
- <'location of train.py file'> 
- --img <'width of image'>
- --batch <'batch size'>
- --epochs <'no of epochs'>
- --data <'location of the .yaml file'>
- --cfg <'Which yolo configuration you want'>(yolov5s/yolov5m/yolov5l/yolov5x).yaml | (small, medium, large, xlarge)
- --name <'Name of the best model after training'>

**METRICS FROM TRAINING PROCESS**

**No.of classes, No.of images, No.of targets, Precision (P), Recall (R), mean Average Precision (map)**
- Class | Images | Targets | P | R | mAP@.5 | mAP@.5:.95: |
- all   | 270    |     489 |    0.0899 |       0.827 |      0.0879 |      0.0551
"""

# Commented out IPython magic to ensure Python compatibility.
# %%time
# !python yolov5/train.py --img 1080 --batch 8 --epochs 15 --data rdd.yaml --cfg models/yolov5s.yaml --name RDDM

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard
# %tensorboard --logdir runs/

# Gjør om PATH til source og weights
!python yolov5/detect.py --source '/content/drive/My Drive/workingDir_2020/rdd/images/valid/' --weights '/content/drive/My Drive/workingDir_2020/runs/exp0_RDDM/weights/best.pt' --img 1080 --save-dir 'inference/output'

disp_images = glob('inference/output/*')
fig=plt.figure(figsize=(20, 28))
columns = 3
rows = 5
for i in range(1, columns*rows +1):
    img = np.random.choice(disp_images)
    img = plt.imread(img)
    fig.add_subplot(rows, columns, i)
    plt.imshow(img)
plt.show()

