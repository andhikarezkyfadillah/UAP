import os
from keras.preprocessing.image import ImageDataGenerator
from keras.applications import MobileNetV2
from keras.layers import Input, Dense, Flatten, Dropout
from keras.models import Model
from keras.optimizers import Adam
import splitfolders
import zipfile

# Load datasets
local_zip = 'rps.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('tmp')
zip_ref.close()

# Split the dataset into training, validation, and test sets
splitfolders.ratio('tmp\\rps', output="tmp\\rps\\rockpaperscissors", seed=1337, ratio=(0.7, 0.25, 0.05))

# Define the directory paths
data_dir = 'tmp\\rps\\rockpaperscissors'
training_dir = os.path.join(data_dir, 'train')
validation_dir = os.path.join(data_dir, 'val')
test_dir = os.path.join(data_dir, 'test')

training_paper_dir = os.path.join(training_dir, 'paper')
training_rock_dir = os.path.join(training_dir, 'rock')
training_scissors_dir = os.path.join(training_dir, 'scissors')

validation_paper_dir = os.path.join(validation_dir, 'paper')
validation_rock_dir = os.path.join(validation_dir, 'rock')
validation_scissors_dir = os.path.join(validation_dir, 'scissors')

test_paper_dir = os.path.join(test_dir, 'paper')
test_rock_dir = os.path.join(test_dir, 'rock')
test_scissors_dir = os.path.join(test_dir, 'scissors')

train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.5,
    zoom_range=0.2,
    rotation_range=20,
    horizontal_flip=True
)
validation_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.5)

test_datagen = ImageDataGenerator(rescale=1/255.0)

train_generator = train_datagen.flow_from_directory(
    training_dir,
    target_size=(150,150),
    classes=['paper', 'rock', 'scissors'],
    batch_size = 32,
    class_mode='categorical',
    shuffle=False
)

valid_generator= validation_datagen.flow_from_directory(
    validation_dir,
    target_size=(150,150),
    classes=['paper', 'rock', 'scissors'],
    batch_size=32,
    class_mode='categorical',
    shuffle=False,
    subset='validation'
)

test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size=(150,150),
    batch_size=32,
    class_mode='categorical',
    classes=['paper','rock', 'scissors'],
    shuffle=False
)

# Ganti ResNet101 dengan MobileNetV2
baseModel = MobileNetV2(
    weights="imagenet",
    input_tensor=Input(shape=(150, 150, 3)),
    include_top=False,
)

# Freeze the baseModel karena sudah dilakukan training
baseModel.trainable = False

# Creating Fully Connected
x = baseModel.output
x = Flatten()(x)
x = Dense(256, activation='relu')(x)
x = Dropout(0.2)(x)  # Regularize with dropout
outputs = Dense(3, activation='softmax')(x)  # Menggunakan softmax untuk output kelas yang lebih dari dua
model = Model(inputs=baseModel.input, outputs=outputs)

# Compile Model
model.compile(Adam(lr=.001), loss='binary_crossentropy', metrics=['accuracy'])

# Training Transfer Learning Model MobileNetV2
history = model.fit(
    train_generator,
    epochs=10,
    validation_data=valid_generator,
)

model.save('modelmodul6.h5')
