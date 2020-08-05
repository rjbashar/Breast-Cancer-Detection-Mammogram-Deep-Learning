import tensorflow as tf
import tensorflow_io as tfio

import config


def create_dataset(x, y):
    """
    Generates a TF dataset for feeding in the data.
    Originally written as a group for the common pipeline.
    :param x: X inputs - paths to images
    :param y: y values - labels for images
    :return: the dataset
    """
    dataset = tf.data.Dataset.from_tensor_slices((x, y))

    # Map values from dicom image path to array
    dataset = dataset.map(parse_function, num_parallel_calls=tf.data.experimental.AUTOTUNE)

    # Dataset to cache data and repeat until all samples have been run once in each epoch
    dataset = dataset.cache().repeat(1)
    dataset = dataset.batch(config.batch_size)
    dataset = dataset.prefetch(tf.data.experimental.AUTOTUNE)

    return dataset


def parse_function(filename, label):
    """
    Mapping function to convert filename to array of pixel values.
    Originally written as a group for the common pipeline. Later amended by Adam Jaamour.
    """
    image_bytes = tf.io.read_file(filename)
    image = tfio.image.decode_dicom_image(image_bytes, color_dim = True, dtype=tf.uint16)
    as_png = tf.image.encode_png(image[0])
    decoded_png = tf.io.decode_png(as_png, channels=1)
    if config.model == "VGG":
        height = config.MINI_MIAS_IMG_SIZE["HEIGHT"]
        width = config.MINI_MIAS_IMG_SIZE["WIDTH"]
    elif config.model == "VGG-common":
        #height = config.VGG_IMG_SIZE["HEIGHT"]
        #width = config.VGG_IMG_SIZE["WIDTH"]
        height = config.ROI_IMG_SIZE["HEIGHT"]
        width = config.ROI_IMG_SIZE["WIDTH"]
    elif config.model == "ResNet":
        pass
    elif config.model == "Inception":
        pass
    elif config.model == "Xception":
        pass
    elif config.model == "CNN":
        pass
    image = tf.image.resize_with_pad(decoded_png, height, width)
    image /= 255

    return image, label
