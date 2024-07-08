import os, time, sys, math
import tensorflow as tf
import numpy as np

from tensorflow.keras.models import Sequential
from contextlib import redirect_stdout
from tensorflow import keras
from keras.callbacks import ModelCheckpoint
from tensorflow.keras import (utils, layers, models, activations, optimizers, regularizers, Model)

def SE_block(x_0, r = 16):
    channels = x_0.shape[-1]
    x = layers.GlobalAvgPool2D()(x_0)
   
    x = x[:, None, None, :]
    
    x = layers.Conv2D(filters=channels//r, kernel_size=1, strides=1)(x)
    x = layers.Activation('relu')(x)
    x = layers.Conv2D(filters=channels, kernel_size=1, strides=1)(x)
    x = layers.Activation('sigmoid')(x)
    x = layers.Multiply()([x_0, x])
    
    return x
    
def SweepNet(image_height, image_width):
    width = image_width
    height = image_height
    ksize = (2,2)
    stride = (1,1)
    l2_lambda = 0.0001
    pool = (2,2)
    shape = (height,width,1)    
    inputs = layers.Input(shape)
    
    sweepcnn = layers.Conv2D(filters=32, kernel_size=ksize, padding='valid', strides=stride, 
        activation='relu') (inputs)
    sweepcnn = layers.MaxPooling2D(pool_size=pool, strides=stride, padding='valid')(sweepcnn)    
    sweepcnn = layers.Conv2D(filters=32, kernel_size=ksize, padding='valid', strides=stride, 
        activation='relu') (sweepcnn)
    sweepcnn = layers.MaxPooling2D(pool_size=pool, strides=stride, padding='valid')(sweepcnn)   
    sweepcnn = layers.Conv2D(filters=32, kernel_size=ksize, padding='valid', strides=stride, 
        activation='relu') (sweepcnn)
    sweepcnn = layers.MaxPooling2D(pool_size=pool, strides=stride, padding='valid')(sweepcnn)
    sweepcnn = SE_block(sweepcnn, r=16)

    sweepcnn = layers.Dense(32, activation='relu')(sweepcnn)
    sweepcnn = layers.GlobalAveragePooling2D()(sweepcnn)
    prediction = layers.Dense(2, activation='softmax')(sweepcnn)
    
    model = models.Model(inputs=inputs, outputs=prediction)

    model.compile(
            optimizer='adam',
            loss="categorical_crossentropy",
            metrics=[tf.keras.metrics.TopKCategoricalAccuracy(k=1)]
        )
    return model
 
class Training:
   
    def __init__(self, directory, image_height, image_width, epochs, model_Name, out):
    
        tf.config.threading.set_inter_op_parallelism_threads(8) 
        self.batch_size = 1
        self.epochs = epochs
        self.directory = directory
        self.imageheight = image_height
        self.imagewidth = image_width
        self.modelN = model_Name
        self.model_Name = eval(self.modelN + '(' + str(self.imageheight) + ', ' + str(self.imagewidth) + ')')
        self.modelName = out
        self.__setDataTrain()
        self.__setDataVal()


    def traingModel(self):
        normalization_layer = layers.experimental.preprocessing.Rescaling(scale=1./255)
        self.train_ds = self.train_ds.map(lambda x, y: (normalization_layer(x), y))
        self.val_ds = self.val_ds.map(lambda x, y: (normalization_layer(x), y))
        AUTOTUNE = tf.data.experimental.AUTOTUNE
        self.train_ds = self.train_ds.cache().shuffle(1000).\
            prefetch(buffer_size=AUTOTUNE)
        self.val_ds = self.val_ds.cache().prefetch(buffer_size=AUTOTUNE)
        

        start = time.time()
        tensorboard_callback = tf.keras.callbacks.TensorBoard(self.modelName + "/tensorBoard")
        
        self.modelpath = os.path.join(self.modelName, "/weights.best.hdf5")
        if self.modelN == 'inception_net':
            checkpoint = ModelCheckpoint(self.modelName + "/weights.best.hdf5", monitor='val_dense_2_accuracy', verbose=1, save_best_only=True, mode='auto')
        else:
            checkpoint = ModelCheckpoint(self.modelName + "/weights.best.hdf5", monitor='val_top_k_categorical_accuracy', verbose=1, save_best_only=True, mode='auto')
        callback_list = [checkpoint]
        # call the model present in a different python file
        # This step includes the compiling and fitting of the model design
        self.useDevice = '/CPU:0'
        with tf.device(self.useDevice):
            self.model = self.model_Name
               
            self.history = self.model.fit(
                self.train_ds,
                validation_data=self.val_ds,
                verbose=1,
                epochs=self.epochs,
                callbacks=[callback_list]
                )
        end = time.time()
        self.exe_time = end-start
        
        self.__summary()
    # endregion

    ########################################################################
    # private methods
    ########################################################################
    # region
    def __setDataTrain(self):
        self.train_ds = tf.keras.preprocessing.image_dataset_from_directory(
            self.directory,
            label_mode='categorical',
            validation_split=0.2,
            subset="training",
            color_mode="grayscale",
            image_size=(self.imageheight, self.imagewidth),
            seed=123,
            batch_size=self.batch_size)

    def __setDataVal(self):
        self.val_ds = tf.keras.preprocessing.image_dataset_from_directory(
            self.directory,
            label_mode='categorical',
            validation_split=0.2,
            subset="validation",
            color_mode="grayscale",
            image_size=(self.imageheight, self.imagewidth),
            seed=123,
            batch_size=self.batch_size)
    
    def __summary(self):
        # evaluation data of the trained model
        if self.modelN == 'inception_net':
            acc = self.history.history['dense_2_accuracy']
            val_acc = self.history.history['val_dense_2_accuracy']
            loss = self.history.history['loss']
            val_loss = self.history.history['val_loss']
        else:
            acc = self.history.history['top_k_categorical_accuracy']
            val_acc = self.history.history['val_top_k_categorical_accuracy']
            loss = self.history.history['loss']
            val_loss = self.history.history['val_loss']
        epochs_range = range(self.epochs)
        # save data into the model folder
        np.savetxt(self.modelName + "/TrainResultsAcc.txt",
                   np.column_stack((epochs_range, acc, val_acc))[:, :],
                   fmt="%s")
        np.savetxt(self.modelName + "/TrainResultsLoss.txt",
                   np.column_stack((epochs_range, loss, val_loss))[:, :],
                   fmt="%s")
        with open((self.modelName + "/TrainExecutionTime.txt"), 'w') as f:
            with redirect_stdout(f):
                print("The execution time of training is: " + str(self.exe_time))
                
        # save the model summary and the amount of data used to
        # create the model
        with open((self.modelName + "/TrainResultsModel.txt"), 'w') as f:
            with redirect_stdout(f):
                for image_batch, labels_batch in self.train_ds:
                    sizeImage = image_batch.shape
                    print(sizeImage)
                    print(labels_batch.shape)
                    break
                self.model.summary()
                
        with open(self.modelName + "/classLabels.txt", "w") as f:
            directory_list = []
            for root, dirs, files in os.walk(self.directory):
            # Add the directory names to the list
                for directory in dirs:
                    directory_list.append(directory)
            class_names = sorted(directory_list)
            f.write("***DO_NOT_REMOVE_OR_EDIT_THIS_FILE***\n")
            num_directories = sum(os.path.isdir(os.path.join(self.directory, name)) for name in os.listdir(self.directory))
            f.write(str(num_directories) + "\n")
            for i, class_name in enumerate(class_names):
                f.write(f"{class_name} ({i})\n")
            f.write("***DO_NOT_REMOVE_OR_EDIT_THIS_FILE***\n")

class Load:
    ########################################################################
    # class constructor
    ########################################################################
    # region
    def __init__(self, modelName, directory, image_height, image_width, outDirectory, threads):
        self.modelName = modelName
        self.directory = directory
        self.imageheight = image_height
        self.imagewidth = image_width
        self.modelpath = os.path.join(self.modelName, "/weights.best.hdf5")
        self.loadedModel = keras.models.load_model(self.modelName + "/weights.best.hdf5")
        self.outDirectory = outDirectory
        self.resultsData = np.empty((0, 4), float)
    # endregion

    ########################################################################
    # public methods
    ########################################################################
    # region
    def imageSingle(self, imageName):
        self.resultsData = np.empty((0, 4), float)
        self.__performPrediction(self.directory + '/' + imageName)
        

    def imageFolder(self):
        totalAmountOfImages = str(len(os.listdir(self.directory)))
        self.resultsData = np.empty((0, 4), float)
        start = time.time()
        with os.scandir(self.directory) as i:
            for image in i:
                if image.is_file():
                    self.__performPrediction(image.name)
        end = time.time()
        self.exe_time = end-start
        with open((self.outDirectory + "/TrainExecutionTime.txt"), 'w') as f:
            with redirect_stdout(f):
                print("The execution time of training is: " + str(self.exe_time))
        return totalAmountOfImages

    def generateReport(self):
        self.resultsData = self.resultsData[self.resultsData[:, 0].
                                            argsort()]
        np.savetxt(self.outDirectory + '/PredResults.txt', self.resultsData[:][:], fmt="%s")
         

    # endregion

    ########################################################################
    # private methods
    ########################################################################
    # region
    def __performPrediction(self, imageName):
        img = tf.keras.preprocessing.image.load_img(
            self.directory + '/' + imageName,
            color_mode="grayscale",
            target_size=(int(self.imageheight), int(self.imagewidth))
        )
        # create an image array from the image
        img_array = keras.preprocessing.image.img_to_array(img)
        # perform the pre-processing
        img_array = (img_array * (1./255))
        # add the dimension
        img_array = tf.expand_dims(img_array, 0)
        self.useDevice = '/CPU:0'
        with tf.device(self.useDevice):
            predictions = self.loadedModel.predict(img_array)
        if 'inception_net' in self.modelName:
            score = predictions[0][0]
        else:
            score = predictions[0]
        scoreNeutral = score[0]
        scoreSelected = score[1]

        score_copy = score.tolist()
        classname = score_copy.index(max(score_copy))
        endPos = imageName.rfind(".png")
        window = str(imageName[:])
        self.resultsData = np.append(self.resultsData,
                                     np.array([[str(window),
                                     		  int(classname),
                                                float(scoreNeutral),
                                                float(scoreSelected)
                                                ]]),
                                     axis=0)

