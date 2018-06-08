# -*- coding: utf-8 -*-
import pcap
import numpy
from keras.layers import Input, Dense, Flatten, Reshape
from keras.models import Model


def create_neural():
    encoding_dim = 10
    input_dim = 19
    input = Input(shape=(input_dim,))
    # encoded is a encoded representation of the input
    encoded = Dense(encoding_dim, activation='relu')(input)
    # decoded is the lossy reconstruction of the input
    decoded = Dense(input_dim, activation='sigmoid')(encoded)
    # this model maps an input to its reconstruction
    autoencoder = Model(input, decoded)
    # this model maps an input to  its encoded representation
    encoder = Model(input, encoded)
    # create a placeholder for a encoded (32-dimension) input
    encoded_input = Input(shape=(encoding_dim,))
    # retrieve the last layer of the autoencoder model
    decoder_layer = autoencoder.layers[-1]
    # create the  decoder model
    decoder = Model(encoded_input, decoder_layer(encoded_input))
    return encoder, decoder, autoencoder


encoder, decoder, autoencoder = create_neural()

autoencoder.compile(optimizer='SGD', loss='mean_squared_error', metrics=['accuracy'])

p = pcap.PcapParser("/home/duhoslav/Documents/iot_firewall/dump1000.pcap")
digitized = p.parse()
np_set = numpy.array(digitized)


p = pcap.PcapParser("/home/duhoslav/Documents/iot_firewall/dump.pcap")
x_test = p.parse()
x_test = numpy.array(x_test)

autoencoder.fit(np_set, np_set,
                epochs=10,
                batch_size=32,
                validation_data=(x_test, x_test))

# check illegal; example: "/home/.../illegal10.pcap"
while True:
    filename = raw_input("Please, enter path to file with illegal traffic (pcap, cap) or 'q' to quit \n")
    if filename == 'q':
        print "terminating...ok"
        exit(0)
    elif len(filename) < 1:
        print "empty input detected!"
        continue
    elif filename[0] in ("'", '"') or filename[-1] in ("'", '"'):
        filename=filename[1:-1]
    try:
        p = pcap.PcapParser(filename)
    except:
        print "file is incorrect!"
        continue

    illegal_digitized = p.parse()
    illegal_packets_idx = p.illegal_packets

    total = len(illegal_digitized)
    illegal_digitized = numpy.array(illegal_digitized)
    dropped = 0
    illegal_detected = 0

    for i in xrange(0, len(illegal_digitized), 5):
        tst = illegal_digitized[i:i + 5]
        encoded_data = encoder.predict(tst)
        decoded_data = decoder.predict(encoded_data)
        for j, decoded in enumerate(decoded_data):
            # print tst[i]
            really_illegal = (i+j) in illegal_packets_idx
            # print decoded
            int_decoded = numpy.rint(decoded).astype(int)
            # print int_decoded
            flag = numpy.equal(int_decoded, tst[j])
            if False in flag:
                dropped += 1
                if really_illegal:
                    illegal_detected+=1

    print "total: " + str(total)
    print "dropped: " + str(dropped)
    print "percent: " + str((dropped * 100) / total) + "%"
    print "really illegal detected: " + str(illegal_detected)
    print "error II:" + str((dropped-illegal_detected)*100 / total) + "%"
