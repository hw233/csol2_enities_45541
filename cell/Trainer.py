# -*- coding: gb18030 -*-
# $Id: Trainer.py,v 1.14 2008-06-21 01:33:46 zhangyuxing Exp $

import BigWorld
import NPC
from bwdebug import *
import csstatus

class Trainer( NPC.NPC ):
	"""An Trainer class for cell.
	训练师NPC

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
			srcEntity.statusMessage( csstatus.LEARN_SKILL_FAIL )		# hyw
			return

		state = self.spellTarget( skillID, srcEntityId )
		if state != csstatus.SKILL_GO_ON:
			INFO_MSG( "%i: skill %i use state = %i." % ( self.id, skillID, state ) )
			
	def sendTrainInfoToPlayer( self, srcEntityId, researchType ):
		"""
		"""
		srcEntity = BigWorld.entities[srcEntityId]

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		srcEntity.clientEntity( self.id ).receiveTrainInfos( list( self.getScript().attrTrainInfo )	)	# attrTrainInfo declare in srcClass()



# Trainer.py
