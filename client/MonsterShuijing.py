
# -*- coding: gb18030 -*-


from Monster import Monster
import csdefine
from gbref import rds
import Define
import Const
from Function import Functor

BAI_SHUIJING  = "20742021"	#白水晶
ZHI_SHUIJING  = "20712011"	#紫水晶
HONG_SHUIJING = "20752011"	#红水晶
SPECIAL_MONSTER_CLASSNAME = "20712015"	#紫水晶
BAI_SHUIJING_DIE_MODEL	= "gw1132"
ZHI_SHUIJING_DIE_MODEL	= "gw1139"
HONG_SHUIJING_DIE_MODEL	= "gw1140"
HIP_POINT = "HP_body"
PARTICLE_PATH1 = "particles/light_sui_a.xml"
PARTICLE_PATH2 = "particles/light_sui_b.xml"

class MonsterShuijing( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )


	def onDie( self ):
		"""
		"""
		modelNumber = ""
		path = ""
		if self.className == BAI_SHUIJING:
			modelNumber = BAI_SHUIJING_DIE_MODEL 
			path = PARTICLE_PATH1
		elif self.className == ZHI_SHUIJING or self.className == SPECIAL_MONSTER_CLASSNAME:
			modelNumber = ZHI_SHUIJING_DIE_MODEL 
			path = PARTICLE_PATH1
		elif self.className == HONG_SHUIJING:
			modelNumber = HONG_SHUIJING_DIE_MODEL 
			path = PARTICLE_PATH2

		rds.npcModel.createDynamicModelBG( modelNumber,  Functor( self.__onModelLoad, path ) )
	
	def __onModelLoad( self, path, model ):
		if not self.inWorld : return  # 如果已不在视野则过滤
		self.model = model
		rds.effectMgr.createParticleBG( self.model, HIP_POINT, path, type = Define.TYPE_PARTICLE_NPC )
		# 设置action match,确保模型改变不会影响 ActionMatch
		am = self.am
		if am.owner != None: am.owner.delMotor( am )
		self.model.motors = ( am, )

		# 动态模型的放大必须在置 action match 之后做，否则会被复原
		self.model.scale = ( self.modelScale, self.modelScale, self.modelScale )

		# 设置左右手模型
		self.set_lefthandNumber()
		self.set_righthandNumber()

		# 获取该模型的随即动作
		self.getRandomActions()

		rds.actionMgr.playActions( self.model, [Const.MODEL_ACTION_DIE,Const.MODEL_ACTION_DEAD], callbacks = [self.onFinishDieAction] )
		self.am.matchCaps = [Define.CAPS_DEAD]
		self.setSelectable( False )

	def playCallMonsterEffect( self ):
		"""
		define method
		"""
		rds.effectMgr.createParticleBG( self.model, "HP_body", "particles/light_zhua_ya.xml", type = Define.TYPE_PARTICLE_NPC )