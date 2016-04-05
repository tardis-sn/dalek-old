from dalek.tools.base import Chain
from dalek.tools.providers import RunInfo
from dalek.tools.model import Tardis
from dalek.wrapper.tardis_wrapper import TardisWrapper


def test_tardis(config_path, log_path):
    wrapper = TardisWrapper(config_path, log_dir=log_path)

    parameters = {
            'model.abundances.o': 0,
            }

    chain = Chain(RunInfo(), Tardis(wrapper))
    output = chain(
            {
                'parameters': parameters
                }
            )
    print(output.keys())

