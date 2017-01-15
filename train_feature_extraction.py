import pickle
import time
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from alexnet import AlexNet

nb_classes = 43
epochs = 10
batch_size = 128

# TODO: Load traffic signs data.
with open('train.p', mode='rb') as f:
    train = pickle.load(f)

train_images, train_labels = train['features'], train['labels']

print('Number of training images =', len(train_images))
print('Number of training labels =', len(train_labels))
print('train_images shape =', train_images.shape)
print('Image data shape =', train_images[0].shape)
print('Number of classes =', len(set(train_labels)))

# TODO: Split data into training and validation sets.
train_images, validation_images, train_labels, validation_labels = \
    train_test_split(train_images, train_labels, test_size=0.10, random_state=42)

# TODO: Define placeholders and resize operation.
features = tf.placeholder(tf.float32, (None, 32, 32, 3))
resized = tf.image.resize_images(features, (227, 227))
labels = tf.placeholder(tf.int64, None)

# TODO: pass placeholder as first argument to `AlexNet`.
fc7 = AlexNet(resized, feature_extract=True)
# NOTE: `tf.stop_gradient` prevents the gradient from flowing backwards
# past this point, keeping the weights before and up to `fc7` frozen.
# This also makes training faster, less work to do!
fc7 = tf.stop_gradient(fc7)

# TODO: Add the final layer for traffic sign classification.
shape = (fc7.get_shape().as_list()[-1], nb_classes)
fc8W = tf.Variable(tf.truncated_normal(shape, stddev=1e-2))
fc8b = tf.Variable(tf.zeros(nb_classes))
logits = tf.nn.xw_plus_b(fc7, fc8W, fc8b)

# TODO: Define loss, training, accuracy operations.
# HINT: Look back at your traffic signs project solution, you may
# be able to reuse some the code.
cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(logits, labels)
loss_op = tf.reduce_mean(cross_entropy)
opt = tf.train.AdamOptimizer()
train_op = opt.minimize(loss_op, var_list=[fc8W, fc8b])
init_op = tf.initialize_all_variables()

preds = tf.arg_max(logits, 1)
accuracy_op = tf.reduce_mean(tf.cast(tf.equal(preds, labels), tf.float32))

# TODO: Train and evaluate the feature extraction model.
def eval_on_data(X, y, sess):
    total_acc = 0
    total_loss = 0
    for offset in range(0, X.shape[0], batch_size):
        end = offset + batch_size
        X_batch = X[offset:end]
        y_batch = y[offset:end]

        loss, acc = sess.run([loss_op, accuracy_op], feed_dict={features: X_batch, labels: y_batch})
        total_loss += (loss * X_batch.shape[0])
        total_acc += (acc * X_batch.shape[0])

    return total_loss/X.shape[0], total_acc/X.shape[0]

with tf.Session() as sess:
    sess.run(init_op)

    for i in range(epochs):
        # training
        X_train, y_train = shuffle(train_images, train_labels)
        t0 = time.time()
        for offset in range(0, X_train.shape[0], batch_size):
            end = offset + batch_size
            sess.run(train_op, feed_dict={features: X_train[offset:end], labels: y_train[offset:end]})

        val_loss, val_acc = eval_on_data(validation_images, validation_labels, sess)
        print("Epoch", i+1)
        print("Time: %.3f seconds" % (time.time() - t0))
        print("Validation Loss =", val_loss)
        print("Validation Accuracy =", val_acc)
        print("")

