from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter

from nice_bison.agents import Bison, GrassPatch
from nice_bison.model import NiceBison


def bison_portrayal(agent):
    if agent is None:
        return

    portrayal = {}
    bison_colors = ['#ff1100', '#ff4133', '#ff6c61', '#ff9e96', '#ffccc7', '#b5b5b5', '#d1ddff', '#a6d1ff', '#70b5ff', '#429dff', '#007bff']

    if type(agent) is Bison:
        # portrayal["Shape"] = "nice_bison/resources/bison.jpg"
        # portrayal["scale"] = 0.9
        # portrayal["Layer"] = 1
        portrayal["Color"] = bison_colors[int(round(agent.cooperation * 10))]
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


canvas_element = CanvasGrid(bison_portrayal, 15, 15, 500, 500)
chart_element_cooperation = ChartModule([{"Label": "Cooperation (avg)", "Color": "#000088"},
                             {"Label": "Cooperation (std)", "Color": "#333333"}])
chart_element_agents = ChartModule([{"Label": "Grass", "Color": "#008800"},
                                    {"Label": "Bison", "Color": "#704c22"}])
chart_element_battles = ChartModule([{"Label": "Battles", "Color": "#888888"}])

model_params = {"number_grass_growth": UserSettableParameter('slider', 'Number grass patches growth', 5, 1, 50),
                "amount_grass_growth": UserSettableParameter('slider', 'Amount grass per patch', 4, 1, 20),
                "initial_bison": UserSettableParameter('slider', 'Initial bison population', 10, 1, 100),
                "initial_bison_food": UserSettableParameter('slider', 'Initial bison food', 4, 1, 10),
                "initial_bison_cooperation_std": UserSettableParameter('slider', 'Initial bison cooperation std', 0.25, 0.0, 1.0, step=0.05),
                "bison_reproduce_threshold": UserSettableParameter('slider', 'Bison reproduction energy threshold', 10, 1, 20),
                "mutation_std": UserSettableParameter('slider', 'Bison mutation standard deviation', 0.1, 0.0, 1.0, step=0.05),
                "one_grass_per_step": UserSettableParameter('checkbox', 'Bison can eat only one grass per step', value=False),
                "movement_weight_fights": UserSettableParameter('slider', 'Weight of fights in movement', 0.5, 0.0, 1.0, step=0.1),
                "sight": UserSettableParameter('slider', 'How far can an agent see', 3, 0, 10),
                "battle_cost": UserSettableParameter('slider', 'Cost of doing battle', 0.5, 0.0, 4.0, step=0.1),
                "grass_spread": UserSettableParameter('slider', 'Grass clustering std', 5, 0.0, 10.0, step=0.1)}

server = ModularServer(NiceBison, [canvas_element, chart_element_agents, chart_element_cooperation, chart_element_battles], "Bison", model_params)
server.port = 8521