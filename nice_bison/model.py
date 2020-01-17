from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from nice_bison.agents import Bison, GrassPatch
from nice_bison.schedule import RandomActivationByBreed


class NiceBison(Model):
    height = 10
    width = 10

    initial_bison = 10
    initial_bison_food = 4
    bison_reproduce_threshold = 10

    number_grass_growth = 20
    amount_grass_growth = 4

    payoff_matrix = [[[0, 0], [1, 0]],
                     [[0, 1], [0.5, 0.5]]]

    verbose = False

    description = 'A model for simulating bison ecosystem modelling.'

    def __init__(self, height=10, width=10, initial_bison=10,
                 initial_bison_food=4, bison_reproduce_threshold=10,
                 amount_grass_growth=20, number_grass_growth=4, 
                 initial_bison_altruism=0.5, mutation_prob=0.5, mutation_SD=0.1):
        '''
        TODO: update this to bison
        Create a new Wolf-Sheep model with the given parameters.
        Args:
            initial_sheep: Number of sheep to start with
            initial_wolves: Number of wolves to start with
            sheep_reproduce: Probability of each sheep reproducing each step
            wolf_reproduce: Probability of each wolf reproducing each step
            wolf_gain_from_food: Energy a wolf gains from eating a sheep
            grass: Whether to have the sheep eat grass for energy
            grass_growth_time: How long it takes for a grass patch to regrow
                                 once it is eaten
            sheep_gain_from_food: Energy sheep gain from grass, if enabled.
        '''
        super().__init__()
        self.height = height
        self.width = width
        self.initial_bison = initial_bison
        self.initial_bison_food = initial_bison_food
        self.bison_reproduce_threshold = bison_reproduce_threshold
        self.number_grass_growth = number_grass_growth
        self.amount_grass_growth = amount_grass_growth
        self.initial_bison_altruism = initial_bison_altruism 
        self.mutation_prob = mutation_prob
        self.mutation_SD = mutation_SD
        self.altruism_bound = [0.05, 0.95]
        
        self.schedule = RandomActivationByBreed(self)
        self.grid = MultiGrid(self.height, self.width, torus=True)
        self.datacollector = DataCollector(
            {"Bison": lambda m: m.schedule.get_breed_count(Bison),
             "Altruism": lambda m: m.schedule.get_average_altruism(Bison)})

        for i in range(self.initial_bison):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            energy = self.initial_bison_food
            altruism = self.initial_bison_altruism
            bison = Bison(self.next_id(), (x, y), self, True, energy, altruism)
            self.grid.place_agent(bison, (x, y))
            self.schedule.add(bison)

        self.grow_grass()

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        print('-----')
        self.schedule.step(by_breed=True)
        self.datacollector.collect(self)
        self.grow_grass()
        if self.verbose:
            print([self.schedule.time, self.schedule.get_breed_count(Bison)])

    def bison_battle(self, grass_amount, bison_one, bison_two):
        print(f'battle between bison {bison_one.unique_id} and {bison_two.unique_id}')
        print(f'altruism factors: {bison_one.altruism}, {bison_two.altruism}')
        bison_one_strategy = bison_one.choose_strategy(bison_two.unique_id)
        bison_two_strategy = bison_two.choose_strategy(bison_one.unique_id)
        gain_one, gain_two = self.payoff_matrix[bison_one_strategy][bison_two_strategy]
        bison_one.update_opinion_opponent(bison_one_strategy, bison_two_strategy)
        bison_two.update_opinion_opponent(bison_two_strategy, bison_one_strategy)
        print(f'gains battle: {gain_one}, {gain_two}')
        bison_one.energy += gain_one * grass_amount
        bison_two.energy += gain_two * grass_amount

    def grow_grass(self):
        for i in range(self.number_grass_growth):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            patch = GrassPatch(self.next_id(), (x, y), self, self.amount_grass_growth)
            self.grid.place_agent(patch, (x, y))
            self.schedule.add(patch)

    def run_model(self, step_count=200):

        if self.verbose:
            print('Initial number bison: ',
                  self.schedule.get_breed_count(Bison))

        for i in range(step_count):
            self.step()

        if self.verbose:
            print('')
            print('Final number bison: ',
                  self.schedule.get_breed_count(Bison))
