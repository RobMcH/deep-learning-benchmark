import argparse
from collections import OrderedDict
from importlib import import_module
import pickle

import numpy as np

frameworks = [
    'tensorflow'
]

models = [
    'resnet152'
]

precisions = [
    'fp32',
    'fp16'
]

class Benchmark():

    def get_framework_model(self, framework, model):
        framework_model = import_module('.'.join(['frameworks', framework, 'models']))
        return getattr(framework_model, model)

    def benchmark_model(self, mode, framework, model, precision, image_shape=(224, 224), batch_size=16, num_iterations=20, num_warmups=20):
        framework_model = self.get_framework_model(framework, model)(precision, image_shape, batch_size)
        durations = framework_model.eval(num_iterations, num_warmups) if mode == 'eval' else framework_model.train(num_iterations, num_warmups)
        durations = np.array(durations)
        fps = 1000.0 / ((durations.mean() * 1000) / batch_size)
        return fps

    def benchmark_all(self):
        results = OrderedDict()
        for framework in frameworks:
            results[framework] = self.benchmark_framework(framework)
        return results

    def benchmark_framework(self, framework):
        results = OrderedDict()
        for precision in precisions:
            results[precision] = []
            for model in models:
                if model == 'densenet161' and framework != 'pytorch':
                    eval_duration = 0
                    train_duration = 0
                else:
                    eval_duration = self.benchmark_model('eval', framework, model, precision)
                    train_duration = self.benchmark_model('train', framework, model, precision)
                print("{}'s {} eval at {}: {} fps avg".format(framework, model, precision, round(eval_duration, 1)))
                print("{}'s {} train at {}: {} fps avg".format(framework, model, precision, round(train_duration, 1)))
                results[precision].append(eval_duration)
                results[precision].append(train_duration)
        return results

if __name__ == '__main__':
    results = Benchmark().benchmark_framework("tensorflow")
    pickle.dump(results, open('{}_results.pkl'.format("tensorflow"), 'wb'))
