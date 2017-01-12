#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
netbuilder.py
(c) Will Roberts  11 January, 2017

Declarative description language for producing persistent neural
network models.
'''

from __future__ import absolute_import
import itertools
import json
import os
import time
from cribbage.utils import grouped, mkdir_p, open_atomic
import lasagne
import numpy as np
import theano
import theano.tensor as T

class ModelStore(object):
    '''
    An object representing a directory where Model objects are saved to
    disk.
    '''

    def __init__(self, path):
        '''
        Constructor.

        Arguments:
        - `path`:
        '''
        self.path = path

    def ensure_exists(self):
        '''Ensure the directory used by this ModelStore exists.'''
        mkdir_p(self.abs_path)

    @property
    def abs_path(self):
        '''Get this ModelStore's absolute path.'''
        return os.path.abspath(self.path)

NONLINEARITY_NAMES = {
    'LeakyRectify': lasagne.nonlinearities.LeakyRectify,
    'ScaledTanH': lasagne.nonlinearities.ScaledTanH,
    'ScaledTanh': lasagne.nonlinearities.ScaledTanh,
    'identity': lasagne.nonlinearities.identity,
    'leaky_rectify': lasagne.nonlinearities.leaky_rectify,
    'linear': lasagne.nonlinearities.linear,
    'rectify': lasagne.nonlinearities.rectify,
    'sigmoid': lasagne.nonlinearities.sigmoid,
    'softmax': lasagne.nonlinearities.softmax,
    'tanh': lasagne.nonlinearities.tanh,
    'theano': lasagne.nonlinearities.theano,
    'very_leaky_rectify': lasagne.nonlinearities.very_leaky_rectify,
}

OBJECTIVE_NAMES = {
    'categorical_crossentropy': lasagne.objectives.categorical_crossentropy,
    'squared_error': lasagne.objectives.squared_error,
    }

UPDATE_NAMES = {
    'adadelta': lasagne.updates.adadelta,
    'adagrad': lasagne.updates.adagrad,
    'adam': lasagne.updates.adam,
    'momentum': lasagne.updates.momentum,
    'nesterov_momentum': lasagne.updates.nesterov_momentum,
    'rmsprop': lasagne.updates.rmsprop,
    'sgd': lasagne.updates.sgd,
}

class NetworkWrapper(object):
    '''An object which wraps a Lasagne feedforward neural network.'''

    def __init__(self):
        '''Constructor.'''
        self.objective_name = 'squared_error'
        self.update_name = 'adadelta'
        # this variable holds the actual neural network
        self._network = None

    def _build_network(self, network_arch):
        '''
        Builds the Lasagne network for this Model from the description in
        `network_arch`.
        '''
        assert len(network_arch) > 1
        assert network_arch[0]['layer'] == 'input'
        assert network_arch[-1]['layer'] == 'output'
        if self._network is None:
            num_hidden_layers = 0
            for layer in network_arch:
                if layer['layer'] == 'input':
                    assert self._network is None
                    self._network = lasagne.layers.InputLayer(
                        shape=(None, layer['size']), name='input')
                else:
                    assert self._network is not None
                    nonlinearity = NONLINEARITY_NAMES[layer['activation']]
                    if layer['layer'] == 'hidden':
                        num_hidden_layers += 1
                        name = 'hidden{}'.format(num_hidden_layers)
                    else:
                        name = 'output'
                    self._network = lasagne.layers.DenseLayer(
                        self._network, num_units=layer['size'],
                        name=name,
                        nonlinearity=nonlinearity)
                if 'dropout' in layer and layer['dropout'] is not None:
                    self._network = lasagne.layers.DropoutLayer(self._network, p=layer['dropout'])

    @property
    def network_layers(self):
        '''
        Returns a dictionary mapping layer names to lasagne Layer objects.
        '''
        return dict((layer.name, layer) for layer in
                    lasagne.layers.get_all_layers(self._network)
                    if layer.name is not None)

    def get_layer(self, layer_name):
        '''
        Returns the lasagne Layer from this Model's neural network with
        the given name.

        Arguments:
        - `layer_name`:
        '''
        return self.network_layers[layer_name]

    def set_weights(self, layer_name, values):
        '''
        Sets the weight parameters (weight matrix and bias) on the given
        layer of this network to the values given.

        Arguments:
        - `layer_name`:
        - `values`: a list of weight parameter matrices
        '''
        params = self.get_layer(layer_name).get_params()
        assert len(values) == len(params)
        for (value, param) in zip(values, params):
            assert value.shape == param.get_value().shape
            param.set_value(value)

    def get_weights(self, layer_name):
        '''
        Returns the weight parameters (weight matrix and bias) for the
        given layer of this network.

        Arguments:
        - `layer_name`:
        '''
        return [param.get_value() for param in self.get_layer(layer_name).get_params()]

    def objective(self, objective_fn):
        '''
        Sets the objective function used for training.  This defaults to
        'squared_error'.

        Arguments:
        - `objective_fn`:
        '''
        self.objective_name = objective_fn

    def update(self, update_fn):
        '''
        Sets the update method used for training.  This defaults to
        'adadelta'.

        Arguments:
        - `update_fn`:
        '''
        self.update_name = update_fn


class Model(NetworkWrapper):
    '''An object wrapping a Lasagne feedforward neural network.'''

    MAX_VALIDATION_SET_SIZE = 10000

    def __init__(self, store, model_name):
        '''
        Constructor

        Arguments:
        - `store`:
        - `model_name`:
        '''
        super(Model, self).__init__()
        self.store = store
        self.model_name = model_name
        # validation is computed after this many minibatches have been
        # trained
        self.validation_interval = 50
        # this is a tuple of (np.array, np.array) representing inputs
        # and outputs; if it is not None, it is used between
        # minibatches to compute validation
        self.validation_set = None
        # if not None, this function is passed this object to compute
        # a validation statistic
        self.use_validation_fn = None
        # these are iterables of np.array values representing inputs
        # and outputs; if not None, they are used for training
        self.training_inputs = None
        self.training_outputs = None
        # update parameters, e.g., learning rate, for training
        self.update_params_value = {}
        # minibatch size; if this is not None, training (input,
        # output) pairs are grouped into blocks of this size during
        # training
        self.minibatch_size_value = None
        # training length
        # number of minibatches to train; if this is not None,
        # training stops after this many minibatches have been seen
        self.use_num_minibatches = None
        # number of epochs to train; if this is not None, training
        # stops after this many loops through the training set.  only
        # use if training set is of finite size.
        self.use_num_epochs = None
        # metadata dictionary for this Model
        self.metadata = None
        # is the network architecture specified by the metadata file?
        self.arch_frozen = False
        # if the architecture is loaded from metadata, the input(),
        # hidden() and output() methods are used to check; this
        # variable stores which layer we're currently checking
        self.arch_check_stage = 0
        # this flag indicates if the network architecture has been
        # fully specified (for new Models) or has been fully checked
        # (for Models loaded from disk)
        self.arch_desc_complete = False
        # load metadata if possible
        self.ensure_exists()
        try:
            self.load_metadata()
            if 'architecture' in self.metadata:
                self.arch_frozen = True
        except IOError:
            # no metadata file present, initialise metadata
            self.metadata = {
                'num_training_samples': 0,
                'num_epochs': 0,
                'num_minibatches': 0,
                'snapshots': [],
            }
            self.save_metadata()

    @property
    def model_path(self):
        '''Get the path where this Model's files are stored.'''
        return os.path.join(self.store.abs_path, self.model_name)

    def ensure_exists(self):
        '''Ensure the directory used by this Model exists.'''
        mkdir_p(self.model_path)

    @property
    def metadata_filename(self):
        '''Get this Model's metadata filename.'''
        return os.path.join(self.model_path, 'metadata.json')

    def load_metadata(self):
        '''Loads metadata for this Model from disk.'''
        with open(self.metadata_filename, 'rb') as input_file:
            self.metadata = json.loads(input_file.read().decode('utf-8'))

    def save_metadata(self):
        '''Saves metadata for this Model to disk.'''
        with open_atomic(self.metadata_filename, 'wb') as output_file:
            output_file.write(json.dumps(self.metadata, indent=4))

    @property
    def best_validation_error(self):
        pass # TODO

    def input(self, input_size, dropout=None):
        '''
        Creates an input layer of the given size.

        Arguments:
        - `input_size`:
        '''
        assert not self.arch_desc_complete
        if self.arch_frozen:
            # we're checking the network architecture against the
            # metadata now
            assert 'architecture' in self.metadata
            assert len(self.metadata['architecture']) > 1
            input_layer = self.metadata['architecture'][0]
            assert input_layer['layer'] == 'input'
            assert input_layer['size'] == input_size
            assert input_layer['dropout'] == dropout
            self.arch_check_stage = 1
        else:
            # we're specifying the network architecture now
            assert 'architecture' not in self.metadata
            self.metadata['architecture'] = []
            self.metadata['architecture'].append({'layer': 'input',
                                                  'size': input_size,
                                                  'dropout': dropout})

    def hidden(self, hidden_size, activation='sigmoid', dropout=None):
        '''
        Creates a hidden layer of the given size.

        Arguments:
        - `hidden_size`:
        - `activation`:
        - `dropout`: if not None, the probability that a node's output
          will be dropped
        '''
        assert 'architecture' in self.metadata
        assert not self.arch_desc_complete
        if self.arch_frozen:
            # we're checking the network architecture against the
            # metadata now
            assert len(self.metadata['architecture']) > 1
            assert self.arch_check_stage > 0
            current_layer = self.metadata['architecture'][self.arch_check_stage]
            assert current_layer['layer'] == 'hidden'
            assert current_layer['size'] == hidden_size
            assert current_layer['activation'] == activation
            assert current_layer['dropout'] == dropout
            self.arch_check_stage += 1
        else:
            # we're specifying the network architecture now
            self.metadata['architecture'].append({'layer': 'hidden',
                                                  'size': hidden_size,
                                                  'activation': activation,
                                                  'dropout': dropout})

    def output(self, output_size, activation='sigmoid'):
        '''
        Creates an output layer of the given size.

        Arguments:
        - `output_size`:
        - `activation`:
        '''
        assert 'architecture' in self.metadata
        assert not self.arch_desc_complete
        if self.arch_frozen:
            # we're checking the network architecture against the
            # metadata now
            assert len(self.metadata['architecture']) > 1
            assert self.arch_check_stage > 0
            current_layer = self.metadata['architecture'][self.arch_check_stage]
            assert current_layer['layer'] == 'output'
            assert current_layer['size'] == output_size
            assert current_layer['activation'] == activation
            assert len(self.metadata['architecture']) == self.arch_check_stage + 1
        else:
            # we're specifying the network architecture now
            self.metadata['architecture'].append({'layer': 'output',
                                                  'size': output_size,
                                                  'activation': activation})
        self.arch_desc_complete = True

    @property
    def network(self):
        '''Returns this Model's neural network object.'''
        if not self._network:
            assert 'architecture' in self.metadata
            self._build_network(self.metadata['architecture'])
        return self._network

    @property
    def network_layers(self):
        '''
        Returns a dictionary mapping layer names to lasagne Layer objects.
        '''
        return dict((layer.name, layer) for layer in
                    lasagne.layers.get_all_layers(self.network)
                    if layer.name is not None)

    def save_snapshot(self, train_err, validation_err):
        '''
        Saves a snapshot of this Model's network to disk.  Also records
        metadata about the snapshot, such as training and validation
        error.

        Arguments:
        - `train_err`:
        - `validation_err`:
        '''
        snapshot_filename = os.path.join(self.model_path, '{:010d}.npz'.format(self.metadata['num_minibatches']))
        np.savez(snapshot_filename, *lasagne.layers.get_all_param_values(self.network))
        self.metadata['snapshots'].append({
            'num_minibatches': self.metadata['num_minibatches'],
            'train_err': train_err,
            'validation_err': validation_err,
        })
        self.save_metadata()

    def load_snapshot(self, snapshot_filename):
        # with np.load('model.npz') as f:
        #     param_values = [f['arr_%d' % i] for i in range(len(f.files))]
        # lasagne.layers.set_all_param_values(self.network, param_values)
        pass # TODO

    def validation(self, validation_set):
        '''
        Sets the validation set used for validation during training.

        `validation_set` can be an iterable, but it must be of finite
        length.

        Arguments:
        - `validation_set`:
        '''
        # validation set might be a tuple: (inputs, outputs)
        if isinstance(validation_set, tuple) and len(validation_set) == 2:
            inputs, outputs = validation_set
            inputs = np.array(list(itertools.islice(
                inputs, self.MAX_VALIDATION_SET_SIZE)))
            outputs = np.array(list(itertools.islice(
                outputs, self.MAX_VALIDATION_SET_SIZE)))
            assert len(inputs) == len(outputs)
            self.validation_set = (inputs, outputs)
        else:
            # otherwise, it might be an iterable
            #
            # the iterable is taken to consist of tuples of (input,
            # output) pairs
            #
            # truncate validation set to maximum allowed size
            validation_set = list(itertools.islice(
                validation_set, self.MAX_VALIDATION_SET_SIZE))
            inputs = np.array([i for (i,o) in validation_set])
            outputs = np.array([o for (i,o) in validation_set])
            self.validation_set = (inputs, outputs)

    def validation_fn(self, validation_fn):
        '''
        Sets the validation function used for validation during training.
        The argument should be a function which, when passed this
        object, returns a validation statistic.

        Arguments:
        - `validation_fn`:
        '''
        self.use_validation_fn = validation_fn

    def training(self, training_set):
        '''
        Sets the training set used for training.

        Arguments:
        - `training_set`:
        '''
        # training set might be a tuple: (inputs, outputs)
        if isinstance(training_set, tuple) and len(training_set) == 2:
            self.training_inputs, self.training_outputs = training_set
        else:
            # otherwise, it might be an iterable
            #
            # the iterable is taken to consist of tuples of (input,
            # output) pairs
            inputs, outputs = itertools.tee(training_set)
            self.training_inputs = (i for (i,o) in inputs)
            self.training_outputs = (o for (i,o) in outputs)

    def update_params(self, params):
        '''
        Sets update params (e.g., the learning rate) to use for training.

        Arguments:
        - `params`: a dictionary with keywords and values
        '''
        self.update_params_value = params

    def minibatch_size(self, minibatch_size):
        '''
        Sets the size of minibatches to use for training.

        Arguments:
        - `minibatch_size`:
        '''
        self.minibatch_size_value = minibatch_size

    def num_minibatches(self, num_minibatches):
        '''
        Configures how long training should run for.  Useful if the
        training set is infinitely long.

        Arguments:
        - `num_minibatches`:
        '''
        self.use_num_minibatches = num_minibatches

    def num_epochs(self, num_epochs):
        '''
        Configures how long training should run for, if the training set
        is of finite length.

        Arguments:
        - `num_epochs`:
        '''
        self.use_num_epochs = num_epochs

def minibatcher(n, iterable):
    '''
    Wraps a `grouped` generator around `iterable` and then returns the
    result inside a numpy array.

    Arguments:
    - `n`:
    - `iterable`:
    '''
    for item in grouped(n, iterable):
        yield np.array(item)

def build(model):
    '''
    Builds a model and trains it up until its training criterion is
    satisfied.

    Arguments:
    - `model`:
    '''

    # theano variables for inputs and outputs
    inputs = T.matrix('inputs')
    outputs = T.matrix('outputs')

    # the raw output of the network
    predictions = lasagne.layers.get_output(model.network, inputs)

    # define the loss function between the network output and the
    # training output
    loss = lasagne.objectives.squared_error(predictions, outputs)
    loss = lasagne.objectives.aggregate(loss, mode='mean')

    # for validation, we use the network in deterministic mode (e.g.,
    # fix dropout)
    validation_predictions = lasagne.layers.get_output(model.network, inputs, deterministic=True)

    # validation loss is the same as training loss
    validation_loss = lasagne.objectives.squared_error(validation_predictions, outputs)
    validation_loss = lasagne.objectives.aggregate(validation_loss, mode='mean')

    # handle minibatching if specified by the model
    if model.minibatch_size_value is not None:
        minibatcher_fn = lambda xs: minibatcher(model.minibatch_size_value, xs)
    else:
        minibatcher_fn = lambda xs: xs

    # retrieve all trainable parameters from the model's neural network
    params = lasagne.layers.get_all_params(model.network, trainable=True)

    # define the update function
    update_fn = UPDATE_NAMES[model.update_name]
    updates = update_fn(loss, params, **model.update_params_value)

    # compile the training and validation functions in theano
    train_fn = theano.function([inputs, outputs], loss, updates=updates)
    validation_fn = theano.function([inputs, outputs], validation_loss)

    # training loop
    start_time = time.time()
    train_err = 0
    train_minibatches = 0
    for num_minibatches, (input_minibatch, output_minibatch) in enumerate(
            itertools.izip(minibatcher_fn(model.training_inputs),
                           minibatcher_fn(model.training_outputs))):

        train_err += train_fn(input_minibatch, output_minibatch)
        train_minibatches += 1
        model.metadata['num_minibatches'] += 1

        # TODO: stop when training criterion is reached

        if (num_minibatches + 1) % model.validation_interval == 0:
            # compute validation
            validation_err = 0
            for input_minibatch, output_minibatch in itertools.izip(*map(minibatcher_fn, model.validation_set)):
                validation_err += validation_fn(input_minibatch, output_minibatch)

            train_err /= model.validation_interval

            # model snapshot
            model.save_snapshot(train_err=train_err, validation_err=validation_err)

            # Then we print the results for this epoch:
            print('Training round {:.1f} secs; training loss {:.6f}; validation loss {:.6f}'.format(
                time.time() - start_time,
                train_err,
                validation_err))
            start_time = time.time()
            train_err = 0
