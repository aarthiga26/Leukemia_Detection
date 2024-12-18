# -*- coding: utf-8 -*-
"""Final_Xcep.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1zgkFd8giEIw0ilk0EELUgqGnGQ2uituD
"""

import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import random
import cv2
import re
import numpy as np

import tensorflow as tf
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from tensorflow.keras.preprocessing.image import ImageDataGenerator

labels=[]
images = []
Luk_name = []
images_path=[]
images_pixels=[]

i=0
dataset_path = r'/content/drive/MyDrive/project/cancer/test'

for directory in os.listdir(dataset_path):
    Luk_name.append(directory)
    for img in os.listdir(os.path.join(dataset_path, directory)):
        if len(re.findall('.png',img.lower())) !=0 or len(re.findall('.jpg',img.lower())) !=0 or len(re.findall('.jpeg',img.lower())) !=0:
            img_path= os.path.join(os.path.join(dataset_path,directory),img)
            images.append(img)
            images_path.append(img_path)
            img_pix = cv2.imread(img_path,1)
            images_pixels.append(cv2.resize(img_pix,(100,100)))
            labels.append(i)

    i=i+1

print("Total labels: ", len(labels))
print("Total images:", len(images))
print("Total images path:", len(images_path))
print("Total types:", len(Luk_name))
print("Total images pixels:", len(images_pixels))

Luk_name

fig=plt.gcf()
fig.set_size_inches (16, 16)

next_pix = images_path
random.shuffle(next_pix)

for i, img_path in enumerate(next_pix[0:12]):

  sp =plt.subplot(4, 4, i+1)
  sp.axis('Off')
  img = mpimg.imread(img_path)
  plt.imshow(img)
plt.show()

shuf=list(zip(images_pixels, labels))
random.shuffle(shuf)

train_data, labels_data = zip(*shuf)

X_data=np.array(train_data)/255
Y_data= to_categorical(labels_data, num_classes =4)

Y_data[0]

print("X date shape:", X_data.shape)
print("Y data shape:", Y_data.shape)

X_train, X_val, Y_train, Y_val= train_test_split(X_data, Y_data, test_size= 0.4, random_state=101)

print("X train data", len(X_train))
print("X label data", len(X_val))
print("Y train data", len(Y_train))
print("V label data", len(Y_val))

from sklearn.decomposition import PCA

# Reshape images_pixels to 2D array for PCA
X_flat = np.array(images_pixels).reshape(len(images_pixels), -1)

# Normalize pixel values
X_flat_normalized = X_flat / 255.0

# Apply PCA
n_components = 50  # You can adjust the number of components as per your requirement
pca = PCA(n_components=n_components)
X_pca = pca.fit_transform(X_flat_normalized)

# Split the data
X_train_pca, X_val_pca, Y_train, Y_val = train_test_split(X_pca, Y_data, test_size=0.4, random_state=101)
print(len(X_train_pca))
print(len(X_val_pca))
# Now X_train_pca and X_val_pca contain the transformed features after PCA

datagen = ImageDataGenerator(horizontal_flip=False,
                             vertical_flip= False,
                             rotation_range=0,
                             zoom_range=0.2,
                             width_shift_range=0,
                             height_shift_range=0,
                             shear_range=0,
                             fill_mode="nearest")

pretrained_model =tf.keras.applications.Xception(input_shape=(100,100,3),
                                                           include_top=False,
                                                           weights ='imagenet',
                                                           pooling='avg')
pretrained_model.trainable= False

inputs= pretrained_model.input
drop_layer= tf.keras.layers.Dropout(0.25)(pretrained_model.output)

x_layer =tf.keras.layers.Dense(512, activation= 'relu') (drop_layer)
x_layer1 =tf.keras.layers.Dense(128, activation= 'relu') (x_layer)
drop_layer1=tf.keras.layers.Dropout(0.20)(x_layer1)
outputs= tf.keras.layers.Dense(4, activation='softmax')(drop_layer1)

model=tf.keras.Model(inputs=inputs, outputs= outputs)

optimizer= tf.keras.optimizers.Adam(learning_rate=0.001)
model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['acc'])
history= model.fit(datagen.flow(X_train, Y_train, batch_size=32), validation_data=(X_val,Y_val),epochs=20)

from sklearn.metrics import precision_score, recall_score, f1_score
import numpy as np
predictions = model.predict(X_val)
predicted_labels = np.argmax(predictions, axis=1)

# Convert one-hot encoded labels to single labels
true_labels = np.argmax(Y_val, axis=1)

# Calculate precision, recall, and F1 score
precision = precision_score(true_labels, predicted_labels, average='weighted')
recall = recall_score(true_labels, predicted_labels, average='weighted')
f1 = f1_score(true_labels, predicted_labels, average='weighted')

print("Precision:", precision)
print("Recall:", recall)
print("F1 Score:", f1)

import matplotlib.pyplot as plt

acc= history.history['acc']
val_acc=history.history['val_acc']
loss =history.history['loss']
val_loss =history.history['val_loss']

epochs =range(len(acc))

plt.plot(epochs, acc,'r', label='Training accuracy')
plt.plot(epochs, val_acc, 'b',label= 'Validation accuracy')
plt.title("Training and validation accuracy")
plt.legend(loc=0)
plt.figure()

plt.show()

import matplotlib.pyplot as plt
plt.plot(epochs, loss,'r', label='Training loss')
plt.plot(epochs, val_loss, 'b',label= 'Validation loss')
plt.title("Training and validation loss")
plt.legend(loc=0)
plt.figure()

plt.show()

from sklearn.metrics import confusion_matrix

# Get predictions for the validation set
Y_pred = model.predict(X_val)
# Convert predictions to class labels
Y_pred_classes = np.argmax(Y_pred, axis=1)
# Convert true labels to class labels
Y_true_classes = np.argmax(Y_val, axis=1)

# Compute confusion matrix
conf_matrix = confusion_matrix(Y_true_classes, Y_pred_classes)
print("Confusion Matrix:")
print(conf_matrix)

