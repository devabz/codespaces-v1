from contextlib import contextmanager

from PyDSTool import *
import numpy as np

from src.time_base_seconds import TimeUnits
from src.heating_constants import *
from collections import OrderedDict
from box import ConfigBox
from tqdm import tqdm

@contextmanager
def timer():
    import time
    start = time.perf_counter()
    yield
    print(f'duration: {round(time.perf_counter() - start, 2)}s')


# Main Integrator using PyDStool's VODESystem
class Integrator:
    current_step = None

    def __init__(self,
                 expressions,
                 ics,
                 tdata=(0, TimeUnits.day),
                 max_step=10 * TimeUnits.minute,
                 min_step=0.001 * TimeUnits.minute,
                 init_step=TimeUnits.minute / 4,
                 atol=0.1,
                 rtol=0.1,
                 params=None,
                 events=None
                 ):
        self.tdata = tdata
        self.events = [] if events is None else events
        self.params = {} if params is None else params
        self.config = args(name='integrator')
        self.config.tdata = tdata
        self.config.varspecs = expressions
        self.config.ics = ics
        self.config.algparams = {
            'init_step': init_step, 'min_step': min_step, 'max_step': max_step, 'atol': atol, 'rtol': rtol
        }
        self.config.events = [event.event for event in events]
        self.config.pars = self.params
        self.solver = Generator.Vode_ODEsystem(self.config)
        self.verbose = 3

    # Updates the initial conditions and parameters for the solver
    def update(self, ics, pars, tdata):
        if self.verbose >= 3:
            print([tdata[0] / 3600, *tdata])

        self.solver.set(ics=ics, pars=pars, tdata=tdata)

    # Integrates until an event is triggered
    def step(self, name):
        results = self.solver.compute(name)
        return ConfigBox({'results': results, 'points': results.sample()})

    #  Main function
    def solve(self, name='run', debug=False):
        # Begin the integration
        dt = 0
        step = 0
        advance = lambda: self.step(name=f'{name}_{step}')
        self.current_step = advance()
        results = [self.current_step]


        with tqdm(total=int(self.tdata[-1])) as progress_bar:
            # Integrate until an event is triggered, update the system & continue the integration
            while self.current_step.points['t'][-1] != self.solver.tdata[-1]:
                step += 1
                dt = self.current_step.points['t'][-1] - dt
                variables = self.current_step.points.coordnames
                ics = {v: self.current_step.points[v][-1] for v in variables}

                # Executes the callback function associated with each event
                self.parse_events(
                    event_times=self.current_step.results.getEventTimes(),
                    variables=variables,
                    current_step=self.current_step,
                    ics=ics,
                    debug=debug
                )

                # Updates the solver with new information
                self.update(
                    ics=ics,
                    pars=self.solver.pars,
                    tdata=[self.current_step.points['t'][-1], self.solver.tdata[-1]]
                )

                self.current_step = advance()
                results.append(self.current_step)

                progress_bar.n = int(self.current_step.points['t'][-1])
                progress_bar.refresh() 

        # Process and return results
        points = ConfigBox({
            point: np.concatenate([temp.points[point] for temp in results]) for point in results[0].points.coordnames
        })

        points['t'] = np.concatenate([temp.points['t'] for temp in results])
        points['results'] = results
        points['events'] = self.events

        return points

    def parse_events(self, current_step, event_times, ics, variables, debug=False):
        for event in self.events:
            if event_times.get(event.event_args['name']):
                temp = current_step.results.getEvents()
                t = event_times.get(event.event_args['name'])
                feed_dict = {
                    **{'event': event, 't': t, 'vars': {v: temp.get(v) for v in variables}},
                    **{'c_step': current_step, 'ics': ics, 'var_names': variables, 'params': self.solver.pars}
                }
                for callback in event.callbacks:
                    if debug:
                        print(f'calling: {callback.__name__}')
                    callback(**feed_dict)


# Time based event, triggers at specified time and repeats at specified intervals
class Event:
    count = 0

    def __init__(self, name, term=True, active=True, direction=0, time=0, repeat=None):
        repeat = int(1e25) if repeat is None else repeat
        self.name = name
        self.repeat = repeat
        self.time = time
        self.event_args = {
            'name': name + f'_{Event.count}',
            'starttime': 0,
            'delaytime': 1,
            'term': term,
            'active': active
        }
        self.direction = direction
        self.event = Events.makeZeroCrossEvent(
            expr=self.expr,
            dircode=self.direction,
            argDict=self.event_args,
            targetlang='python'
        )
        self.callbacks = []
        Event.count += 1

    def __repr__(self):
        return f'Event(name={self.name}, time={self.time})'

    def attach_callback(self, func):
        self.callbacks.append(func)

    @property
    def expr(self):
        return f'sin((t - {self.time}) * pi/{self.repeat})'
