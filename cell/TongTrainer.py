# -*- coding: gb18030 -*-
#
# $Id: Trainer.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
Trainer基类
"""

import BigWorld
from bwdebug import *
import csdefine
import csstatus
from Trainer import Trainer

class TongTrainer( Trainer ):
	"""
	根据CSOL-2116修改后，该NPC没有实际功能
	帮会领地Trainer基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		Trainer.__init__( self )
		
	def lock( self ):
		"""
		define method.
		Trainer被锁住， 帮会成员无法和他交互
		"""
		self.locked = True

	def unlock( self ):
		"""
		define method.
		Trainer被开锁， 帮会成员恢复和他交互
		"""
		self.locked = False

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
	
	def sendTrainInfoToPlayer( self, srcEntityId, researchType ):
		"""
		Define method.
		发送技能数据给玩家
		"""
		srcEntity = BigWorld.entities[srcEntityId]

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

	def researchSkill( self, srcEntityId, skillID ):
		"""
		define method.
		客户端向服务器请求研发该技能
		"""
		srcEntity = BigWorld.entities[srcEntityId]
		
		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

	def clearTongSkill( self, srcEntityId, skillID ):
		"""
		define method.
		选择了遗忘某技能
		"""
		srcEntity = BigWorld.entities[srcEntityId]
		
		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return
		
# Trainer.py
