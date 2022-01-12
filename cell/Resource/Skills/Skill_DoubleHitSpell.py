# -*- coding: gb18030 -*-

import random
from SpellBase import *
from Skill_Normal import Skill_Normal
from Function import newUID

class Skill_DoubleHitSpell( Skill_Normal ):
	"""
	玩家暴击命中后有几率对自身/目标放技能
	例如，对自身释放一个不需要消耗魔法的标志
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Skill_Normal.__init__( self )
		self.triggerSkillID = 0		# 技能ID
		self.effectPercent = 0.0	# 触发几率
		self.isOwnerSpell = False	# 对自身还是对目标，默认是对目标

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Skill_Normal.init( self, dict )
		self.triggerSkillID = int( dict["param1"] if len( dict["param1"] ) > 0 else 0 )
		self.effectPercent = float( dict["param2"] if len( dict["param2"] ) > 0 else 0 ) / 100.0
		self.isOwnerSpell = bool( int( dict["param3"] if len( dict["param3"] ) > 0 else 0 ) )

	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		为目标附上一个效果，通常被附上的效果是实例自身，它可以通过detach()去掉这个效果。具体效果由各派生类自行决定。
		
		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.appendAttackerDoubleHit( self.getNewObj() )

	def detach( self, ownerEntity ):
		"""
		virtual method
		执行与attach()的反向操作

		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.removeAttackerDoubleHit( self.getUID() )

	def springOnDoubleHit( self, caster, receiver, damageType ):
		"""
		产生暴击后效果
		"""
		if random.random() > self.effectPercent:	# 没有触发
			return

		if self.isOwnerSpell:	# 对自身放技能
			caster.spellTarget( self.triggerSkillID, caster.id )
		else:					# 对目标放技能
			caster.spellTarget( self.triggerSkillID, receiver.id )

	def addToDict( self ):
		"""
		生成用于传输的数据
		"""
		return { "param":{"triggerSkillID":self.triggerSkillID, "effectPercent":self.effectPercent, "isOwnerSpell":self.isOwnerSpell} }

	def createFromDict( self, data ):
		"""
		创建技能实例
		"""
		obj = Skill_DoubleHitSpell()
		obj.__dict__.update( self.__dict__ )
		paramData = data["param"]
		obj.triggerSkillID = paramData["triggerSkillID"]
		obj.effectPercent = paramData["effectPercent"]
		obj.isOwnerSpell = paramData["isOwnerSpell"]
		try:
			uid = data["uid"]
		except KeyError:
			uid = 0
		if uid == 0:
			uid = newUID()
		obj.setUID( uid )
		return obj
