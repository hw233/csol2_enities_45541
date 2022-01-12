# -*- coding: gb18030 -*-
#

"""
"""

import BigWorld
from bwdebug import *
from NPCObject import NPCObject
from ObjectScripts.GameObjectFactory import g_objFactory
import csdefine

class ChallengeTransducer( NPCObject ):
	"""
	用于挑战副本陷阱
	"""
	def __init__( self ):
		"""
		初始化
		"""
		NPCObject.__init__( self )
		self._spawnMonsterList = []

	def initEntity( self, selfEntity ):
		# 重载啥事都不做只是禁用底层的处理
		pass

	def remoteEnterTrap( self, selfEntityID, entityID, range, userData ):
		"""
		一个用于中转onEnterTrapExt()消息的函数，此方法会被远程调用（详见onEnterTrapExt()）。
		"""
		selfEntity = BigWorld.entities.get( selfEntityID )
		entity = BigWorld.entities.get( entityID )
		if selfEntity is None or entity is None:
			ERROR_MSG( "remote call fail. selfEntityID = %i(%s), entityID = %i(%s)." % (
					selfEntityID, ("found", "not found")[selfEntity is None], 
					entityID,     ("found", "not found")[entity is None] ) )
			return
		self.onEnterTrapExt( selfEntity, entity, range, userData )

	def onEnterTrapExt( self, selfEntity, entity, range, userData ):
		"""
		This method is associated with the Entity.addProximity method.
		It is called when an entity enters a proximity trap of this entity.
		@param selfEntity:	全局实例自身的entity实例
		@param entity:		The entity that has entered.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		if entity.getEntityType() != csdefine.ENTITY_TYPE_ROLE:
			return
				
		if not entity.isReal():
			INFO_MSG( "Dest entity(%i/%s) not a real entity, I will foreward the call." % ( entity.id, entity.getName() ) )
			# 远程脚本调用
			# 之所以不调用相同onEnterTrapExt()接口，是为了避免onEnterTrapExt()复杂化。
			# 因为如果使用同一个onEnterTrapExt()接口，将需要判断传进来的entity参数是一个entity还是mailbox。
			entity.forwardScriptCall( self.className, "remoteEnterTrap", ( selfEntity.id, entity.id, range, userData ) )
			return

		selfEntity.getCurrentSpaceBase().startTrapSpawnEntity( selfEntity.trapID )
		selfEntity.destroy()