from mesa import Agent
from nice_bison.walker import RandomWalker


class Bison(RandomWalker):
    energy = None

    def __init__(self, unique_id, pos, model, moore, energy=None, altruism=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy
        self.opinion_opponents = {}
        self.altruism = altruism

    def choose_strategy(self):
        return 0 if self.random.random() > self.altruism else 1

    def step(self):
        if self.model.verbose:
            print(f'bison {self.unique_id}: {self.energy} energy')

        neighborhood = self.model.grid.get_neighbors(self.pos, 1, True)
        patches = [obj for obj in neighborhood if isinstance(obj, GrassPatch)]

        if self.model.one_grass_per_step:
            if len(patches) > 0:
                patch = self.random.choice(patches)
                patch.claimants.append(self)
        else:
            for patch in patches:
                patch.claimants.append(self)

        self.move()
        self.energy -= 1

        if self.energy < 0:
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)

            if self.model.verbose:
                print(f'bison {self.unique_id}: dies')

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

            if self.model.verbose:
                print(f'bison {self.unique_id}: has child {child.unique_id} with energy {child.energy}')


    def move(self):
        fights_in_directions = self.get_fights_in_direction() # up, down, left, right
        wants_fights_factor = (self.altruism - 0.5) * -self.model.avoid_fights_factor
        adjusted_fights_in_directions = [direction**wants_fights_factor for direction in fights_in_directions]
        chance_in_directions = [direction/sum(adjusted_fights_in_directions) for direction in adjusted_fights_in_directions]

        rv = self.random.random()
        x, y = self.pos
        if rv < chance_in_directions[0]:
            y += 1
        elif rv < chance_in_directions[0] + chance_in_directions[1]:
            y -= 1
        elif rv < chance_in_directions[0] + chance_in_directions[1] + chance_in_directions[2]:
            x -= 1
        else:
            x += 1

        if self.model.verbose:
            print(f'bison moves from {self.pos} to ({x},{y})')
        self.model.grid.move_agent(self, (x, y))

    def get_fights_in_direction(self):
        xs = [pos[0] for pos in self.model.old_battle_locations]
        ys = [pos[1] for pos in self.model.old_battle_locations]

        up, down, left, right = 0.01, 0.01, 0.01, 0.01
        for x in xs:
            if x < self.pos[0]:
                down += 1
            else:
                up += 1

        for y in ys:
            if y < self.pos[1]:
                left += 1
            else:
                right += 1

        return [up, down, left, right]


class GrassPatch(Agent):
    def __init__(self, unique_id, pos, model, amount):
        super().__init__(unique_id, model)
        self.amount = amount
        self.pos = pos
        self.claimants = []

    def step(self):
        if len(self.claimants) == 0:
            return
        elif len(self.claimants) == 1:
            self.claimants[0].energy += self.amount
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)

            if self.model.verbose:
                print(f'grass {self.unique_id} eaten by bison {self.claimants[0].unique_id}')
        else:
            lucky_claimant_one, lucky_claimant_two = self.random.sample(self.claimants, 2)
            self.model.bison_battle(self, lucky_claimant_one, lucky_claimant_two)
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)



            