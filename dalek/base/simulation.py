import logging
import time

import numpy as np
import pandas as pd

from astropy import units as u

from tardis.simulation import Simulation

logger = logging.getLogger(__name__)

class TinnerSimulation(Simulation):

    def __init__(self, tardis_config, convergence_threshold=0.05):
        super(TinnerSimulation, self).__init__(tardis_config)
        self.convergence_threshold = convergence_threshold

    def log_plasma_state(self, t_rad, w, t_inner, next_t_rad, next_w,
                         next_t_inner, log_sampling=5):
        """
        Logging the change of the plasma state

        Parameters
        ----------
        t_rad: ~astropy.units.Quanity
            current t_rad
        w: ~astropy.units.Quanity
            current w
        next_t_rad: ~astropy.units.Quanity
            next t_rad
        next_w: ~astropy.units.Quanity
            next_w
        log_sampling: ~int
            the n-th shells to be plotted

        Returns
        -------

        """

        plasma_state_log = pd.DataFrame(index=np.arange(len(t_rad)),
                                           columns=['t_rad', 'next_t_rad',
                                                    't_rad_convergence'
                                                    'w', 'next_w', 'w_convergence'])
        plasma_state_log['t_rad'] = t_rad
        plasma_state_log['next_t_rad'] = next_t_rad
        plasma_state_log['t_rad_convergence'] = (t_rad - next_t_rad) / t_rad
        plasma_state_log['w'] = w
        plasma_state_log['next_w'] = next_w
        plasma_state_log['w_convergence'] = (w - next_w) / w
        plasma_state_log.index.name = 'Shell'

        plasma_state_log = str(plasma_state_log[::log_sampling])

        plasma_state_log = ''.join(['\t%s\n' % item for item in
                                    plasma_state_log.split('\n')])

        logger.info('Plasma stratification:\n%s\n', plasma_state_log)
        logger.info('t_inner {0:.3f} -- next t_inner {1:.3f}'.format(
            t_inner, next_t_inner))


    def get_convergence_status(self, t_rad, w, estimated_t_rad, estimated_w):

        t_rad_converged = (np.median(np.abs(t_rad - estimated_t_rad) / t_rad)
                           < self.convergence_threshold)

        w_converged = (np.median(np.abs(w - estimated_w) / w)
                           < self.convergence_threshold)


        return t_rad_converged and w_converged

    def run_simulation(self, model, t_inner):
        start_time = time.time()

        iterations_remaining = self.tardis_config.montecarlo.iterations
        iterations_executed = 0

        model.t_inner = t_inner

        model.t_rads = np.linspace(t_inner, 0.5 * t_inner, len(model.t_rads))

        while iterations_remaining > 1:
            logger.info('Remaining run %d', iterations_remaining)
            self.run_single_montecarlo(
                model, self.tardis_config.montecarlo.no_of_packets)
            self.log_run_results(self.calculate_emitted_luminosity(),
                                 self.calculate_reabsorbed_luminosity())
            iterations_executed += 1
            iterations_remaining -= 1

            estimated_t_rad, estimated_w = (
                self.runner.calculate_radiationfield_properties())

            converged = self.get_convergence_status(
                model.t_rads, model.ws, estimated_t_rad,
                estimated_w)


            if converged:
                break

            self.log_plasma_state(model.t_rads, model.ws, np.nan,
                                  estimated_t_rad, estimated_w, np.nan)
            model.t_rads = model.t_rads + 0.5 * (estimated_t_rad - model.t_rads)
            model.ws = model.ws + 1.0 * (estimated_w - model.ws)



            model.calculate_j_blues(init_detailed_j_blues=False)
            model.update_plasmas(initialize_nlte=False)


            # if switching into the hold iterations mode or out back to the normal one
            # if it is in either of these modes already it will just stay there

        #Finished second to last loop running one more time
        logger.info('Doing last run')
        if self.tardis_config.montecarlo.last_no_of_packets is not None:
            no_of_packets = self.tardis_config.montecarlo.last_no_of_packets
        else:
            no_of_packets = self.tardis_config.montecarlo.no_of_packets

        no_of_virtual_packets = (
            self.tardis_config.montecarlo.no_of_virtual_packets)

        self.run_single_montecarlo(model, no_of_packets, no_of_virtual_packets)

        self.legacy_update_spectrum(model, no_of_virtual_packets)

        logger.info("Finished in {0:d} iterations and took {1:.2f} s".format(
            iterations_executed, time.time()-start_time))

