from collections import defaultdict
from statistics import pstdev, mean

from mesa.time import RandomActivation


class RandomActivationByBreed(RandomActivation):
    '''
    A scheduler which activates each type of agent once per step, in random
    order, with the order reshuffled every step.
    This is equivalent to the NetLogo 'ask breed...' and is generally the
    default behavior for an ABM.
    Assumes that all agents have a step() method.
    '''

    def __init__(self, model):
        super().__init__(model)
        self.agents_by_breed = defaultdict(dict)

    def add(self, agent):
        '''
        Add an Agent object to the schedule
        Args:
            agent: An Agent to be added to the schedule.
        '''

        self._agents[agent.unique_id] = agent
        agent_class = type(agent)
        self.agents_by_breed[agent_class][agent.unique_id] = agent

    def remove(self, agent):
        '''
        Remove all instances of a given agent from the schedule.
        '''

        del self._agents[agent.unique_id]

        agent_class = type(agent)
        del self.agents_by_breed[agent_class][agent.unique_id]

    def step(self, by_breed=True):
        '''
        Executes the step of each agent breed, one at a time, in random order.
        Args:
            by_breed: If True, run all agents of a single breed before running
                      the next one.
        '''
        if by_breed:
            for agent_class in self.agents_by_breed:
                self.step_breed(agent_class)
            self.steps += 1
            self.time += 1
        else:
            super().step()

    def step_breed(self, breed):
        '''
        Shuffle order and run all agents of a given breed.
        Args:
            breed: Class object of the breed to run.
        '''
        agent_keys = list(self.agents_by_breed[breed].keys())
        self.model.random.shuffle(agent_keys)
        for agent_key in agent_keys:
            self.agents_by_breed[breed][agent_key].step()

    def get_breed_count(self, breed_class):
        '''
        Returns the current number of agents of certain breed in the queue.
        '''
        return len(self.agents_by_breed[breed_class].values())
    
    def get_average_attribute(self, breed_class, attribute):
        '''
        Returns the current average of a property of an agent class
        '''
        agents = self.agents_by_breed[breed_class].values()
        if len(agents) > 0:
            attribute_values = [getattr(agent, attribute) for agent in agents]
            return mean(attribute_values)
        else:
            return 0

    def get_std_attribute(self, breed_class, attribute):
        '''
        Returns the current standard deviation of a property of an agent class
        '''
        agents = self.agents_by_breed[breed_class].values()
        if len(agents) > 0:
            attribute_values = [getattr(agent, attribute) for agent in agents]
            return pstdev(attribute_values)
        else:
            return 0

    def get_average_cooperation_of_run(self):
        if len(self.model.cooperation_values) > 1:
            return mean(self.model.cooperation_values)
        else:
            return -1

    def get_std_cooperation_of_run(self):
        if len(self.model.cooperation_values) > 1:
            return pstdev(self.model.cooperation_values)
        else:
            return -1