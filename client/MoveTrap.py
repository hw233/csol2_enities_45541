# -*- coding: gb18030 -*-

import BigWorld
import Define
from gbref import rds
from SkillTrap import SkillTrap
from Function import Functor

class MoveTrap( SkillTrap ):
	"""
	可移动的陷阱
	"""
	def __init__( self ):
		"""
		"""
		SkillTrap.__init__( self )

	def filterCreator( self ):
		"""
		template method.
		创建entity的filter模块
		"""
		return BigWorld.PlayerAvatarFilter()

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		创建模型
		继承 NPCObject.createModel
		"""
		# 因为一些摆摊限制也用到这个entity.且该entity是不可见的,所以应该屏蔽此种entity的模型
		if len( self.modelNumber ) == 0: return
		# 模型可以绑定相应的光效
		rds.npcModel.createDynamicModelBG( self.modelNumber,  Functor( self.__onModelLoad, event ) )
	
	def __onModelLoad( self, event, pyModel ):
		if not self.inWorld : return  # 如果已不在视野则过滤
		if pyModel is None:
			return
		self.setModel( pyModel, event )
		am = BigWorld.ActionMatcher( self )    #设置模型am
		self.model.motors = ( am, )
		self.model.scale = ( self.modelScale, self.modelScale, self.modelScale )
		self.setVisibility( False )

	def moveToPosFC( self, pos, speed, dir ):
		"""
		define method
		服务器通知移动到某点
		"""
		self.setVisibility( True )
		SkillTrap.moveToPosFC( self, pos, speed, dir )

	def onDestroy( self ):
		"""
		define method.
		销毁特效，类似怪物死亡特效
		"""
		model = self.getModel()
		if model:
			infos = rds.npcModel._datas[self.modelNumber]
			effectID = infos.get( "blast_effect", "" )
			type = self.getParticleType()
			effect = rds.skillEffect.createEffectByID( effectID, model, model, type, type )
			if effect:
				effect.start()
			self.setVisibility( False )

	def fadeInModel( self ):
		"""
		渐入模型，MoveTrap有特殊的处理
		"""
		pass

	def refreshVisible( self ):
		"""
		"""
		pass