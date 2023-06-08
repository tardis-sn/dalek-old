from __future__ import print_function
from copy import copy
import sys

def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)

class BreakChainException(Exception):
    pass

class Chainable(object):
    inputs = set()
    outputs = set()

    def __call__(self, data={}):
        if self._isvalid(data):
            data = self._apply(copy(data))
        else:
            raise ValueError(
                f"Inputs required are: {str(self.inputs)}\n Data provides only: {str(data)}"
            )
        return data

    def _isvalid(self, data):
        try:
            valid = self.inputs.issubset(data.keys())
        except AttributeError:
            valid = set(self.inputs).issubset(data.keys())
        finally:
            return valid

class Link(Chainable):

    def _apply(self, input_dict):
        inputs = self._prepare_input(input_dict)
        output = self.calculate(*inputs)
        # output_dict = copy(input_dict)
        output = self._prepare_output(output)
        input_dict.update(output)
        return input_dict

    def _prepare_input(self, input_dict):
        return [input_dict[i] for i in self.inputs]

    def _prepare_output(self, output):
        '''
        Possible inputs:
        - None : Link doesn't output
        - One element : Link has one output
        - Tuple
        '''
        if len(self.outputs) == 0:
            return {}
        if len(self.outputs) == 1:
            return { self.outputs[0]: output }
        if len(output) == len(self.outputs):
            return dict(zip(self.outputs, output))
        else:
            raise ValueError(
                f"{self.__class__.__name__} is expected to return {self.outputs} but actual value was {str(output)}"
            )


class Chain(Chainable):

    def __init__(self, *args, **kwargs):
        try:
            self.breakable = kwargs.pop('breakable')
        except KeyError:
            self.breakable = False
        self._links = []
        self.inputs = set()
        self.outputs = set()
        for arg in args:
            self._links.append(arg)
            self.inputs.update(set(arg.inputs).difference(self.outputs))
            self.outputs.update(arg.outputs)
        self.outputs.update(self.inputs)
        super(Chain, self).__init__()

    def _apply(self, input_dict):
        for link in self._links:
            try:
                input_dict = link(input_dict)
            except BreakChainException as e:
                if not self.breakable:
                    raise e
                input_dict = self.cleanup(input_dict)
                break
        return input_dict

    def cleanup(self, input_dict):
        output_dict = dict.fromkeys(self.outputs)
        output_dict.update(input_dict)
        return output_dict
