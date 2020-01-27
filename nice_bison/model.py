from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from scipy.stats import truncnorm

from nice_bison.agents import Bison, GrassPatch
from nice_bison.schedule import RandomActivationByBreed


class NiceBison(Model):
    height = 10
    width = 10

    initial_bison = 10
    initial_bison_food = 4
    bison_reproduce_threshold = 10

    number_grass_growth = 5
    amount_grass_growth = 4

    mutation_prob = 0.5
    mutation_std = 0.1

    one_grass_per_step = True

    verbose = False

    description = 'A model for simulating bison ecosystem modelling.'

    def __init__(self, height=10, width=10, initial_bison=10, initial_bison_food=4, bison_reproduce_threshold=10,
                 amount_grass_growth=4, number_grass_growth=5, initial_bison_altruism_std=0.25, mutation_std=0.1,
                 one_grass_per_step=True, battle_cost=0.5, clustering_std=10, movement_weight_fights=0.5,
                 sight=4, verbose=False):
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
        self.initial_bison_altruism_std = initial_bison_altruism_std
        self.movement_weight_fights = movement_weight_fights
        self.mutation_std = mutation_std
        self.altruism_bound = [0.0, 1.0]
        self.one_grass_per_step = one_grass_per_step
        self.battle_cost = battle_cost
        self.clustering_std = clustering_std
        self.sight = sight
        self.verbose = verbose
        
        self.schedule = RandomActivationByBreed(self)
        self.grid = MultiGrid(self.height, self.width, torus=True)
        self.datacollector = DataCollector(
            {"Bison": lambda m: m.schedule.get_breed_count(Bison),
             "Grass": lambda m: m.schedule.get_breed_count(GrassPatch),
             "Altruism (avg)": lambda m: m.schedule.get_average_attribute(Bison, 'altruism'),
             "Altruism (std)": lambda m: m.schedule.get_std_attribute(Bison, 'altruism'),
             "Battles": "n_battles"})

        a = (0 - 0.5) / self.initial_bison_altruism_std
        b = (1 - 0.5) / self.initial_bison_altruism_std
        rvs = truncnorm.rvs(a, b, loc=0.5, scale=self.initial_bison_altruism_std, size=self.initial_bison)
        for rv in rvs:
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            energy = self.initial_bison_food
            altruism = rv
            bison = Bison(self.next_id(), (x, y), self, True, energy, altruism)
            self.grid.place_agent(bison, (x, y))
            self.schedule.add(bison)

        self.grow_grass()

        self.n_battles = 0
        self.current_battle_locations = []
        self.old_battle_locations = []

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        if self.verbose:
            print(f'------------- time {self.schedule.time}')

        self.n_battles = 0
        self.old_battle_locations = self.current_battle_locations.copy()
        self.current_battle_locations = []

        self.schedule.step(by_breed=True)
        self.datacollector.collect(self)
        self.grow_grass()

    def bison_battle(self, grass, bison_one, bison_two):
        payoff_matrix = [[[0.5-self.battle_cost, 0.5-self.battle_cost], [1, 0]],
                         [[0, 1], [0.5, 0.5]]]

        bison_one_strategy = bison_one.choose_strategy()
        bison_two_strategy = bison_two.choose_strategy()
        gain_one, gain_two = payoff_matrix[bison_one_strategy][bison_two_strategy]
        bison_one.energy += gain_one * grass.amount
        bison_two.energy += gain_two * grass.amount

        self.n_battles += 1
        self.current_battle_locations.append(grass.pos)

        if self.verbose:
            print(f'battle between bison {bison_one.unique_id} and {bison_two.unique_id}')
            print(f'altruism factors: {bison_one.altruism}, {bison_two.altruism}')
            print(f'gains battle: {gain_one}, {gain_two}')

    def grow_grass(self):
        a = (0 - self.width / 2) / self.clustering_std
        b = (self.width - 1 - self.width / 2) / self.clustering_std
        rvs = truncnorm.rvs(a, b, loc=self.width/2, scale=self.clustering_std, size=2 * self.number_grass_growth)

        for i in range(0, len(rvs), 2):
            x = int(round(rvs[i]))
            y = int(round(rvs[i+1]))

            patch = GrassPatch(self.next_id(), (x, y), self, self.amount_grass_growth)
            self.grid.place_agent(patch, (x, y))
            self.schedule.add(patch)

            if self.verbose:
                print(f'Place grass at ({x},{y})')

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
