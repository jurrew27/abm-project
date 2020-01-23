from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter

from nice_bison.agents import Bison, GrassPatch
from nice_bison.model import NiceBison


def bison_portrayal(agent):
    if agent is None:
        return

    portrayal = {}
    bison_colors = ['#000000', '#110000', '#220000', '#330000', '#440000', '#550000', '#660000', '#770000', '#880000',
                    '#990000', '#AA0000', '#BB0000', '#CC0000', '#DD0000', '#EE0000', '#FF0000']

    if type(agent) is Bison:
        # portrayal["Shape"] = "nice_bison/resources/bison.jpg"
        # portrayal["scale"] = 0.9
        # portrayal["Layer"] = 1
        portrayal["Color"] = bison_colors[min(round(agent.energy), 15)]
        portrayal["Shape"] = "circle"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = round(agent.energy)
        portrayal["r"] = 1

    elif type(agent) is GrassPatch:
        portrayal["Color"] = ["#00FF00", "#00CC00", "#009900"]
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal


canvas_element = CanvasGrid(bison_portrayal, 10, 10, 500, 500)
chart_element_altruism = ChartModule([{"Label": "Altruism (avg)", "Color": "#000088"},
                             {"Label": "Altruism (std)", "Color": "#333333"}])
chart_element_agents = ChartModule([{"Label": "Grass", "Color": "#008800"},
                                    {"Label": "Bison", "Color": "#704c22"}])
chart_element_battles = ChartModule([{"Label": "Battles", "Color": "#888888"}])

model_params = {"number_grass_growth": UserSettableParameter('slider', 'Number grass patches growth', 5, 1, 50),
                "amount_grass_growth": UserSettableParameter('slider', 'Amount grass per patch', 4, 1, 20),
                "initial_bison": UserSettableParameter('slider', 'Initial bison population', 10, 1, 100),
                "initial_bison_food": UserSettableParameter('slider', 'Initial bison food', 4, 1, 10),
                "bison_reproduce_threshold": UserSettableParameter('slider', 'Bison reproduction energy threshold', 10, 1, 20),
                "mutation_prob": UserSettableParameter('slider', 'Bison mutation probability', 0.5, 0.0, 1.0, step=0.05),
                "mutation_std": UserSettableParameter('slider', 'Bison mutation standard deviation', 0.1, 0.0, 1.0, step=0.05),
                "one_grass_per_step": UserSettableParameter('checkbox', 'Bison can eat only one grass per step', value=False),
                "battle_cost": UserSettableParameter('slider', 'Cost of doing battle', 0.5, 0.0, 4.0, step=0.1)}

server = ModularServer(NiceBison, [canvas_element, chart_element_agents, chart_element_altruism, chart_element_battles], "Bison", model_params)
server.port = 8521