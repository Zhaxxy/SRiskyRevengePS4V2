from collections import namedtuple

CoordsLayerAndArea = namedtuple('CoordsLayerAndArea',('x_coord','y_coord','area_id','current_layer'))

FIRST_BOSS = CoordsLayerAndArea(2367487, 2949119, 213, 0)
FINAL_CHECKPOINT = CoordsLayerAndArea(21381120, 18415615, 188, 2)
RISKY_SHIP_PRE_FINAL_BOSS = CoordsLayerAndArea(1867776, 3145727, 190, 0)
FINAL_BOSS = CoordsLayerAndArea(2277376, 2031615, 191, 0)

FINAL_BOSS_BEATEN = CoordsLayerAndArea(1474560, 3145727, 192, 0)
FINAL_CUTSCENE = CoordsLayerAndArea(3342336, 18677759, 215, 1)