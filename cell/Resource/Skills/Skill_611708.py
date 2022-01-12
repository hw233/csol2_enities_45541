# -*- coding: gb18030 -*-
#

import BigWorld
import csconst
import csdefine
import csstatus
from Function import newUID
import random
from SpellBase import *
from Skill_Normal import Skill_Normal
from bwdebug import *


class Skill_611708( Skill_Normal ):
	"""
	宠物技能,福泽:有一定机率使得主人杀死怪物时获得2倍经验.
	"""
	def __init__( self ):
		"""
		"""
		Skill_Normal.__init__( self )
		self._param1 = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Skill_Normal.init( self, dict )
		self._param1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )

	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		执行与attach()的反向操作

		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		if ownerEntity.__class__.__name__ == "Pet":
			petOwner = ownerEntity.getOwner()
			entity = petOwner.entity
			if petOwner.etype == "REAL":
				entity.appendReceiverMonsterExp( self.getNewObj() )
			else:
				entity.attachSkillOnReal( self )
		else:
			ownerEntity.appendReceiverMonsterExp( self.getNewObj() )

	def detach( self, ownerEntity ):
		"""
		virtual method = 0;
		执行与attach()的反向操作

		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		if ownerEntity.__class__.__name__ == "Pet":
			petOwner = ownerEntity.getOwner()
			entity = petOwner.entity
			if petOwner.etype == "REAL":
				entity.removeReceiverMonsterExp( self.getUID() )
			else:
				entity.detachSkillOnReal( self )
		else:
			ownerEntity.removeReceiverMonsterExp( self.getUID() )

	def addExpTrigger( self, entity, exp ):
		"""
		获得经验时的触发
		"""
		if self._param1 >= random.randint( 0, 100 ):
			entity.addExp( exp, csdefine.CHANGE_EXP_KILLMONSTER )
