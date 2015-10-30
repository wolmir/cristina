from material import MatSys
from vector2d import Vector2D

class KeysGuide:
	@staticmethod
	def Load():
		MatSys.AddMaterial("data/keys/w.png")
		MatSys.AddMaterial("data/keys/a.png")
		MatSys.AddMaterial("data/keys/s.png")
		MatSys.AddMaterial("data/keys/d.png")
		MatSys.AddMaterial("data/keys/lmb.png")
	@staticmethod
	def DrawGuide(engine):
		engine.DrawImage(MatSys.GetMaterial("data/keys/w.png"), Vector2D(engine.properties["screen"][0] - 152, engine.properties["screen"][1] - 80))
		engine.DrawImage(MatSys.GetMaterial("data/keys/a.png"), Vector2D(engine.properties["screen"][0] - 192, engine.properties["screen"][1] - 40))
		engine.DrawImage(MatSys.GetMaterial("data/keys/s.png"), Vector2D(engine.properties["screen"][0] - 152, engine.properties["screen"][1] - 40))
		engine.DrawImage(MatSys.GetMaterial("data/keys/d.png"), Vector2D(engine.properties["screen"][0] - 112, engine.properties["screen"][1] - 40))
		engine.DrawImage(MatSys.GetMaterial("data/keys/lmb.png"), Vector2D(engine.properties["screen"][0] - 72, engine.properties["screen"][1] - 124))