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

        self.move()
        self.energy -= 1

        neighborhood = self.model.grid.get_neighbors(self.pos, 1, True)
        patches = [obj for obj in neighborhood if isinstance(obj, GrassPatch)]

        if self.model.one_grass_per_step:
            if len(patches) > 0:
                patch = self.random.choice(patches)
                patch.claimants.append(self)
        else:
            for patch in patches:
                patch.claimants.append(self)

        if self.energy < 0:
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)

            if self.model.verbose:
                print(f'bison {self.unique_id}: dies')

            return

        if self.energy > self.model.bison_reproduce_threshold:
            self.energy /= 2
            altruism_offspring = self.random.gauss(self.altruism, self.model.mutation_std)
            if not (self.model.altruism_bound[0] < altruism_offspring < self.model.altruism_bound[1]):
                altruism_offspring = self.altruism
            child = Bison(self.model.next_id(), self.pos, self.model,
                          self.moore, self.energy, altruism_offspring)
            self.model.grid.place_agent(child, self.pos)
            self.model.schedule.add(child)

            if self.model.verbose:
                print(f'bison {self.unique_id}: has child {child.unique_id} with energy {child.energy}')

    def move(self):
        n_fights = self.get_fights_in_direction() # up, down, left, right
        chance_fights = [direction / sum(n_fights) for direction in n_fights]
        adjusted_chance_fights = chance_fights.copy()
        for i in range(4):
            adjusted_chance_fights[i] = chance_fights[i] * self.altruism + chance_fights[(i + 2) % 4] * (1 - self.altruism)

        n_grass = self.get_grass_in_direction() # up, down, left, right
        chance_grass = [direction / sum(n_grass) for direction in n_grass]

        chance_in_direction = [((fights * self.model.movement_weight_fights) + patches * (1 - self.model.movement_weight_fights)) \
                               for fights, patches in zip(adjusted_chance_fights, chance_grass)]

        rv = self.random.random()
        x, y = self.pos
        if rv < chance_in_direction[0]:
            y += 1
        elif rv < chance_in_direction[0] + chance_in_direction[1]:
            y -= 1
        elif rv < chance_in_direction[0] + chance_in_direction[1] + chance_in_direction[2]:
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
                left += 1
            else:
                right += 1

        for y in ys:
            if y < self.pos[1]:
                down += 1
            else:
                up += 1

        return [up, down, left, right]

    def get_grass_in_direction(self):
        patches = self.model.schedule.agents_by_breed[GrassPatch].values()
        xs = [patch.pos[0] for patch in patches]
        ys = [patch.pos[1] for patch in patches]

        up, down, left, right = 0.01, 0.01, 0.01, 0.01
        for x in xs:
            if x < self.pos[0]:
                left += 1
            else:
                right += 1

        for y in ys:
            if y < self.pos[1]:
                down += 1
            else:
                up += 1

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



            