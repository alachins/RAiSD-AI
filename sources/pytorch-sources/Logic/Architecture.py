import os, time, sys, math
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

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


def SE_block1D(x_0, r = 16):
    channels = x_0.shape[-1]
    x = layers.GlobalAvgPool1D()(x_0)
   
    x = x[:, None, :]
    
    x = layers.Conv1D(filters=channels//r, kernel_size=1, strides=1)(x)
    x = layers.Activation('relu')(x)
    x = layers.Conv1D(filters=channels, kernel_size=1, strides=1)(x)
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


def SweepNetV2(image_height, image_width):
    width = image_width
    ksize = 4
    conv_stride = 1
    pool = 2
    pool_stride = 2
    shape = (width,2)    
    inputs = layers.Input(shape)
    
    sweepcnn = layers.Conv1D(filters=48, kernel_size=ksize, padding='valid', strides=conv_stride, 
                            activation='relu') (inputs)
    sweepcnn = layers.MaxPooling1D(pool_size=pool, strides=pool_stride, padding='valid')(sweepcnn)    
    sweepcnn = layers.Conv1D(filters=48, kernel_size=ksize, padding='valid', strides=conv_stride, 
                            activation='relu') (inputs)
    sweepcnn = layers.MaxPooling1D(pool_size=pool, strides=pool_stride, padding='valid')(sweepcnn) 
    sweepcnn = layers.Conv1D(filters=48, kernel_size=ksize, padding='valid', strides=conv_stride, 
                            activation='relu') (inputs)
    sweepcnn = layers.MaxPooling1D(pool_size=pool, strides=pool_stride, padding='valid')(sweepcnn) 
    sweepcnn = layers.Conv1D(filters=48, kernel_size=ksize, padding='valid', strides=conv_stride, 
                            activation='relu') (inputs)
    sweepcnn = layers.MaxPooling1D(pool_size=pool, strides=pool_stride, padding='valid')(sweepcnn) 
    sweepcnn = SE_block1D(sweepcnn, r=16)

    sweepcnn = layers.Dense(32, activation='relu')(sweepcnn)
    sweepcnn = layers.GlobalAveragePooling1D()(sweepcnn)
    prediction = layers.Dense(2, activation='softmax')(sweepcnn)
    
    model = models.Model(inputs=inputs, outputs=prediction)

    optimizer = keras.optimizers.Adam(lr=0.5e-3)
    model.compile(
            optimizer=optimizer,
            loss="categorical_crossentropy",
            metrics=[tf.keras.metrics.TopKCategoricalAccuracy(k=1)]
        )
    return model
    
def VGG16(image_height, image_width):
    width = image_width
    height = image_height
    in_shape = tf.keras.layers.Input([None, None, 1], dtype = tf.uint8)
    
    x = tf.cast(in_shape, tf.float32)
#    x = tf.keras.applications.vgg16.preprocess_input(x)
    core = tf.keras.applications.VGG16(input_shape=(height, width, 1), weights=None, classes=2)
    x = core(x)
    model = tf.keras.Model(inputs=in_shape, outputs=[x])
    
    model.compile(loss="categorical_crossentropy", optimizer='adam',
	              metrics=[tf.keras.metrics.TopKCategoricalAccuracy(k=1)])
    return model
    
def MobileNet(image_height, image_width):
    width = image_width
    height = image_height
    in_shape = tf.keras.layers.Input([None, None, 1], dtype = tf.uint8)
    
    x = tf.cast(in_shape, tf.float32)
    x = tf.keras.applications.mobilenet.preprocess_input(x)
    core = tf.keras.applications.MobileNet(input_shape=(height, width, 1), weights=None, classes=2)
    x = core(x)
    model = tf.keras.Model(inputs=in_shape, outputs=[x])
    
    model.compile(loss="categorical_crossentropy", optimizer='adam',
	              metrics=[tf.keras.metrics.TopKCategoricalAccuracy(k=1)])
    return model
    
def MobileNetV2(image_height, image_width):
    width = image_width
    height = image_height
    in_shape = tf.keras.layers.Input([None, None, 1], dtype = tf.uint8)
    
    x = tf.cast(in_shape, tf.float32)
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
    core = tf.keras.applications.MobileNetV2(input_shape=(height, width, 1), weights=None, classes=2)
    x = core(x)
    model = tf.keras.Model(inputs=in_shape, outputs=[x])
    
    model.compile(loss="categorical_crossentropy", optimizer='adam',
	              metrics=[tf.keras.metrics.TopKCategoricalAccuracy(k=1)])
    return model
    
def EfficientNetV2L(image_height, image_width):
    width = image_width
    height = image_height
    in_shape = tf.keras.layers.Input([None, None, 1], dtype = tf.uint8)
    
    x = tf.cast(in_shape, tf.float32)
    x = tf.keras.applications.efficientnet_v2.preprocess_input(x)
    core = tf.keras.applications.EfficientNetV2L(input_shape=(height, width, 1), weights=None, classes=2)
    x = core(x)
    model = tf.keras.Model(inputs=in_shape, outputs=[x])
    
    model.compile(loss="categorical_crossentropy", optimizer='adam',
	              metrics=[tf.keras.metrics.TopKCategoricalAccuracy(k=1)])
    return model
    
def ImaGeneNet(image_height, image_width):
    width = image_width
    height = image_height
    in_shape = (height, width, 1)
    model = Sequential([
                    layers.Conv2D(filters=32, kernel_size=(5,5), strides=(1,1), activation='relu', kernel_regularizer=regularizers.l1_l2(l1=0.005, l2=0.005), padding='valid', input_shape=in_shape),
                    layers.MaxPooling2D(pool_size=(2,2)),
                    layers.Conv2D(filters=32, kernel_size=(5,5), strides=(1,1), activation='relu', kernel_regularizer=regularizers.l1_l2(l1=0.005, l2=0.005), padding='valid'),
                    layers.MaxPooling2D(pool_size=(2,2)),
                    layers.Conv2D(filters=32, kernel_size=(5,5), strides=(1,1), activation='relu', kernel_regularizer=regularizers.l1_l2(l1=0.005, l2=0.005), padding='valid'),
                    layers.MaxPooling2D(pool_size=(2,2)),
                    layers.Flatten(),
                    layers.Dense(2, activation='sigmoid')])
    model.compile(optimizer='adam',
                    loss='categorical_crossentropy',
                    metrics=[tf.keras.metrics.TopKCategoricalAccuracy(k=1)])
    return model
    
def INSNet(image_height, image_width):
    width = image_width
    height = image_height
    in_shape = (height, width, 1)
    
    model = Sequential()
    model.add(layers.Conv2D(
        4,
        [10, 10], 
        strides=(2,2),
        padding='valid',
        activation='relu',
        input_shape=in_shape 
    ))
    model.add(layers.MaxPooling2D(
        pool_size=(2, 2),
        strides=2
    ))
    model.add(layers.Conv2D(
        64,
        [5, 5],
        padding='same',
        activation='relu'
    ))
    model.add(layers.MaxPooling2D(
        pool_size=(2, 2),
        strides=2
    ))
    
    model.add(layers.Dropout(
        0.4, 
    ))
  
    model.add(layers.Flatten())
    model.add(layers.Dense(
        1024, 
        activation='relu'
    ))

    model.add(layers.Dense(
        2, 
        activation='sigmoid'
    ))
    
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=[tf.keras.metrics.TopKCategoricalAccuracy(k=1)])
    return model
    
def UENet(image_height, image_width):
    width = image_width
    height = image_height
    in_shape = (height, width)
    
    model = Sequential()
    model.add(layers.Conv1D(64, kernel_size=2,
                     activation='relu',
                     input_shape=in_shape))
    model.add(layers.Conv1D(64, kernel_size=2, activation='relu'))
    model.add(layers.AveragePooling1D(pool_size=2))
    model.add(layers.Dropout(0.25))
    model.add(layers.Flatten())
    model.add(layers.Dense(64, activation='relu', kernel_initializer='normal'))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(64, activation='relu', kernel_initializer='normal'))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(2, kernel_initializer='normal'))
    
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=[tf.keras.metrics.TopKCategoricalAccuracy(k=1)])
    return model

 
class Training:
   
    def __init__(self, directory, image_height, image_width, epochs, model_Name, out):
    
        print("start training")
        tf.config.threading.set_inter_op_parallelism_threads(8)
        self.batch_size = 1
        self.epochs = epochs
        self.directory = directory
        self.imageheight = image_height
        self.imagewidth = image_width
        self.modelN = model_Name
        self.model_Name = eval(self.modelN + '(' + str(self.imageheight) + ', ' + str(self.imagewidth) + ')')
        self.modelName = out
        if self.modelN == "SweepNetV2":
            self.__setDataTrain(color_mode="rgb")
            self.__setDataVal(color_mode="rgb")
        else:
            self.__setDataTrain()
            self.__setDataVal()


    def traingModel(self):
        normalization_layer = layers.experimental.preprocessing.Rescaling(scale=1./255)
        if self.modelN == "SweepNetV2":        
            self.train_ds = self.train_ds.map(lambda x, y: (tf.reduce_mean(x, axis=1)[:, :, :2], y))
            self.val_ds = self.val_ds.map(lambda x, y: (tf.reduce_mean(x, axis=1)[:, :, :2], y))
        self.train_ds = self.train_ds.map(lambda x, y: (normalization_layer(x), y))
        self.val_ds = self.val_ds.map(lambda x, y: (normalization_layer(x), y))
        AUTOTUNE = tf.data.experimental.AUTOTUNE
        self.train_ds = self.train_ds.cache().shuffle(1000).\
            prefetch(buffer_size=AUTOTUNE)
        self.val_ds = self.val_ds.cache().prefetch(buffer_size=AUTOTUNE)
        for image_batch, labels_batch in self.train_ds:
            sizeImage = image_batch.shape
            print(sizeImage)
            print(labels_batch.shape)
            break

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
       
#            self.history = self.model.fit(
#                self.train_ds,
#                validation_data=self.val_ds,
#                verbose=1,
#                epochs=self.epochs,
#                callbacks=[tensorboard_callback]
 #               )
               
            self.history = self.model.fit(
                self.train_ds,
                validation_data=self.val_ds,
                verbose=1,
                epochs=self.epochs,
                callbacks=[callback_list]
                )
        end = time.time()
        self.exe_time = end-start
		        
        # give a summary of the model in the terminal
        self.model.summary()
        
        # save the model
#        self.model.save(self.modelName)
        print("Model is saved")
        
        self.__summary()
    # endregion

    ########################################################################
    # private methods
    ########################################################################
    # region
    def __setDataTrain(self, color_mode="grayscale"):
        self.train_ds = tf.keras.preprocessing.image_dataset_from_directory(
            self.directory,
            label_mode='categorical',
            validation_split=0.2,
            subset="training",
            color_mode=color_mode,
            image_size=(self.imageheight, self.imagewidth),
            seed=123,
            batch_size=self.batch_size)

    def __setDataVal(self, color_mode="grayscale"):
        self.val_ds = tf.keras.preprocessing.image_dataset_from_directory(
            self.directory,
            label_mode='categorical',
            validation_split=0.2,
            subset="validation",
            color_mode=color_mode,
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
                print("amount of files used")
                print("validation split is set to 0.2\n")
                for i in range(2):
                    DIR = self.directory + str(i)
#                    amount = str(len([name for name in os.listdir(DIR) if
#                                      os.path.isfile(os.path.join(DIR, name))
#                                      ]))
#                    print("class " + str(i))
#                    print("amount " + amount)
                print("\nmodel summary\n")
                self.model.summary()

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
        self.__performPrediction(self.directory + '/' + imageName, color_mode="rgb")
        

    def imageFolder(self):
        totalAmountOfImages = str(len(os.listdir(self.directory)))
       # print("total amount of Images " + totalAmountOfImages)
        self.resultsData = np.empty((0, 4), float)
        start = time.time()
        with os.scandir(self.directory) as i:
            for k, image in enumerate(i):
                print(k)
                f_root, f_ext = os.path.splitext(image)
                if f_ext != ".png":
                    continue
                if image.is_file():
                    self.__performPrediction(image.name, color_mode="rgb")
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
        
    def plotPredictions(self):
        print(self.resultsData)
        plt.close()
        print(np.arange(len(self.resultsData)))
        data = np.array((self.resultsData[:, 3]), dtype=float)
        print(data)
        plt.plot(np.arange(len(self.resultsData)), data)
        plt.savefig("test_detection_sweepnet.pdf")
        
         

    # endregion

    ########################################################################
    # private methods
    ########################################################################
    # region
    def __performPrediction(self, imageName, color_mode="grayscale"):
        img = tf.keras.preprocessing.image.load_img(
            self.directory + '/' + imageName,
            color_mode=color_mode,
            target_size=(int(self.imageheight), int(self.imagewidth))
        )
        # create an image array from the image
        img_array = keras.preprocessing.image.img_to_array(img)
        # perform the pre-processing
        img_array = (img_array * (1./255))
        # add the dimension
        img_array = tf.expand_dims(img_array, 0)
        img_array = img_array[:, :, :, :2]
        img_array = tf.reduce_mean(img_array, axis=1)
        self.useDevice = '/CPU:0'
        with tf.device(self.useDevice):
            predictions = self.loadedModel.predict(img_array)
#            print(predictions)
        if 'inception_net' in self.modelName:
            score = predictions[0][0]
        else:
            score = predictions[0]
        scoreNeutral = score[0]
        scoreSelected = score[1]

#        scoreRecombination = score[2]
        score_copy = score.tolist()
        classname = score_copy.index(max(score_copy))
#        window = imageName.rfind(".txt")
#        midPos = imageName.rfind("win_")
#        midPos2 = imageName.rfind(".txt")
        endPos = imageName.rfind(".png")
        window = str(imageName[:])
#        lastSNP = float(imageName[midPos2 + len(".w_end_"):endPos])
#        middleSNP = (firstSNP + lastSNP) / 2
        self.resultsData = np.append(self.resultsData,
                                     np.array([[str(window),
                                     		  int(classname),
                                                float(scoreNeutral),
                                                float(scoreSelected)
                                                ]]),
                                     axis=0)

