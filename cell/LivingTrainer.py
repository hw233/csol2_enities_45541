# -*- coding: gb18030 -*-
# $Id: livingTrainer.py, jiangyi Exp $

import BigWorld
import NPC
from bwdebug import *
import csstatus

class LivingTrainer( NPC.NPC ):
	"""
	An Trainer class for cell.
	生活技能NPC
	"""
	def __init__( self ):
		NPC.NPC.__init__( self )
		# 初始化自身特有的属性

	def trainPlayer( self, srcEntityId, skillID ):
		"""
		训练玩家
		@param srcEntityId: 由于使用了<Expose/>，这个是由系统自动传递进来的，表示是哪个client上的调用
		@type  srcEntityId: int
		@param     skillID: 要训练的技能
		@type      skillID: INT
		@return: 			无
		"""
		srcEntity = BigWorld.entities[srcEntityId]

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		#if not self.validLearn( srcEntity, skillID ):
		if not self.getScript().validLearn( srcEntity, skillID ):
			srcEntity.statusMessage( csstatus.LEARN_SKILL_FAIL )
			return
			
		srcEntity.liv_learnSkill( skillID )
		srcEntity.statusMessage( csstatus.LIVING_LEARN_NEW_SKILL_SUCESS )
			
	def oblive( self, srcEntityId, skillID ):
		"""
		Exposed Method
		遗忘一个生活技能
		"""
		srcEntity = BigWorld.entities[srcEntityId]

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return
			
		if srcEntity.liv_obliveSkill( skillID ):
			srcEntity.statusMessage( csstatus.LIVING_OBLIVE_SKILL_SUCCESS )
		
	def skillLevelUp( self, srcEntityId, skillID ):
		"""
		Exposed Method
		升级一个生活技能
		"""
		srcEntity = BigWorld.entities[srcEntityId]

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return
			
		if not self.getScript().validLevelUp( srcEntity, skillID ):
			srcEntity.statusMessage( csstatus.LIVING_CANT_LEVEL_UP_SKILL )
			return
			
		if not self.getScript().payMoney( srcEntity, skillID ):
			srcEntity.statusMessage( csstatus.SKILL_NOT_ENOUGH_MONEY )
			return
			
		srcEntity.liv_skillLevelUp( skillID )
		#srcEntity.statusMessage( csstatus.LIVING_LEVEL_UP_SKILL_SUCCESS )

# livingTrainer.py
