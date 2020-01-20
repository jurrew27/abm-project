from mesa import Agent
from nice_bison.walker import RandomWalker


class Bison(RandomWalker):
    energy = None

    def __init__(self, unique_id, pos, model, moore, energy=None, altruism=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy
        self.opinion_opponents = {}
        self.altruism = altruism

    def choose_strategy(self, opponent_id):
        return 1 if self.random.random() > self.altruism else 0

    def step(self):
        print(f'bison {self.unique_id}: {self.energy} energy')
        self.random_move()

        self.energy -= 1

        neighborhood = self.model.grid.get_neighbors(self.pos, 1, True)

        for obj in neighborhood:
            if isinstance(obj, GrassPatch):
                obj.claimants.append(self)

        if self.energy < 0:
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)
            return

        if self.energy > self.model.bison_reproduce_threshold:
            self.energy /= 2
            altruism_offspring = self.altruism #Offspring copies behaviour of parents (gentically)
            if self.random.random() < self.model.mutation_prob: #With a certain probability there is a mutation
                after_mutation = altruism_offspring + self.random.gauss(0, self.model.mutation_std) #The size of mutation can be varied
                if self.model.altruism_bound[0] < after_mutation < self.model.altruism_bound[1]: #The altruism prob is bounded
                    altruism_offspring = after_mutation     
            child = Bison(self.model.next_id(), self.pos, self.model,
                          self.moore, self.energy, altruism_offspring)
            self.model.grid.place_agent(child, self.pos)
            self.model.schedule.add(child)


class GrassPatch(Agent):
    def __init__(self, unique_id, pos, model, amount):
        super().__init__(unique_id, model)
        self.amount = amount
        self.pos = pos
        self.claimants = []

    def step(self):
        print(f'grass {self.unique_id}: {len(self.claimants)} claimants')
        if len(self.claimants) == 0:
            return
        elif len(self.claimants) == 1:
            self.claimants[0].energy += self.amount
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)
        else:
            lucky_claimant_one, lucky_claimant_two = self.random.sample(self.claimants, 2)
            self.model.bison_battle(self.amount, lucky_claimant_one, lucky_claimant_two)
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)




            