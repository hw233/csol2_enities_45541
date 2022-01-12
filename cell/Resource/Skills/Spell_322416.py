# -*- coding: gb18030 -*-
#
from Spell_BuffNormal import Spell_BuffNormal
import random
import csdefine
import csstatus
import BigWorld
from Domain_Fight import g_fightMgr

class Spell_322416( Spell_BuffNormal ):
	"""
	遁形技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_BuffNormal.__init__( self )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		self.receiveLinkBuff( caster, receiver )

		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			actPet = receiver.pcg_getActPet()
			petEntiy = None
			if actPet:
				petEntiy = actPet.entity
				if not petEntiy.isReal():
					petEntiy.receiveOnReal( caster.id, self )
				else:
					self.receiveLinkBuff( caster, petEntiy )

			# 通知所有战斗列表玩家遁形成功，确保客户端表现与服务器实际效果一致
			for entityID in receiver.enemyList.keys():
				entity = BigWorld.entities.get( entityID )
				if entity is None: continue
				state = entity.isRealLook( receiver.id )
				if state:
					# 表示被目标侦测到
					if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
						entity.clientEntity( receiver.id ).onSnakeStateChange( False )
				else:
					g_fightMgr.breakEnemyRelation( entity, receiver )
					
					# 通知客户端更新模型表现
					if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
						entity.clientEntity( receiver.id ).onSnakeStateChange( True )

