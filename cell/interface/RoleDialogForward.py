# -*- coding: gb18030 -*-
#
# $Id: RoleDialogForward.py,v 1.22 2008-08-07 08:52:25 zhangyuxing Exp $

"""

"""

import csdefine
import BigWorld
import Love3
from bwdebug import *

class RoleDialogForward:
	"""
	"""
	def questStatusForward( self, dstEntity ):
		"""
		define method
		查询一个游戏对象所有任务相对于玩家的状态，状态将通过回调返回给client相对应的GameObject。

		@param dstEntity: 要查询哪一个游戏对象发放的任务
		@type  dstEntity: Entity
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao

		dstEntity = BigWorld.entities.get( dstEntity.id, None )
		if dstEntity is None:
			return
		dstEntity.getScript().questStatus( dstEntity, self )

	def gossipWithForward( self, dstEntity, talkID ):
		"""
		define method
		@type dstEntity: Entity
		@type    talkID: string
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		dstEntity = BigWorld.entities[ dstEntity.id ]			
		dstEntity.getScript().gossipWith( dstEntity, self, talkID )

	def questSelectForward( self, dstEntity, questID ):
		"""
		define method
		@type dstEntity: Entity
		@type   questID: INT32
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		dstEntity = BigWorld.entities[ dstEntity.id ]			
		dstEntity.getScript().questSelect( dstEntity, self, questID )

	def questAcceptForward( self, dstEntity, questID ):
		"""
		define method
		@type dstEntity: Entity
		@type   questID: INT32
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		dstEntity = BigWorld.entities[ dstEntity.id ]			
		dstEntity.getScript().questAccept( dstEntity, self, questID )

	def questDetailForward( self, dstEntity, questID ):
		"""
		define method
		@type dstEntity: Entity
		@type   questID: INT32
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		dstEntity = BigWorld.entities[ dstEntity.id ]			
		dstEntity.getScript().questDetail( dstEntity, self, questID )

	def questChooseRewardForward( self, dstEntity, questID, rewardIndex, codeStr ):
		"""
		define method
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		dstEntity = BigWorld.entities[ dstEntity.id ]			
		dstEntity.getScript().questChooseReward( dstEntity, self, questID, rewardIndex, codeStr )

	def gossipQuestChooseRewardForward( self, dstEntity, questID, rewardIndex ):
		"""
		define method
		@type   dstEntity: Entity
		@type     questID: INT32
		@type rewardIndex: INT8
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		dstEntity = BigWorld.entities[ dstEntity.id ]			
		dstEntity.getScript().gossipQuestChooseReward( dstEntity, self, questID, rewardIndex )

	def acceptQuestForward( self , questID  ):
		"""
		define method
		远程接受一个任务 ( 因潜能任务需要共享任务成功后设置NPC当前所在位置 因此需要远程设置 set 其他任务传入空字符串既可 )
		@param questID: 任务ID
		"""
		quest = self.getQuest( questID )
		state = quest.query( self )
		if state == csdefine.QUEST_STATE_NOT_HAVE:
			quest.accept( self )

	def setQuestVal( self , questID , setKey , setVal ):
		"""
		define method
		远程设置玩家questsTable里任务的标记
		@param questID: 任务ID
		@param setKey: 设置永久存储的 key
		@param setVal: 设置永久存储的 value
		"""
		if not self.questsTable.has_quest( questID ):
			return
		self.questsTable[questID].set( setKey , setVal )

	def completeQuestForward( self , questID , rewardIndex ):
		"""
		define method
		远程完成任务
		@param setKey: 设置永久存储 key
		@param setVal: 设置永久存储的 value
		"""
		quest = self.getQuest( questID )
		if quest != None:
			quest.complete( self, rewardIndex )

	def taskStatusForward( self, dstEntity ):
		"""
		define method
		@param 	dstEntity: 任务箱子
		@type   dstEntity: Entity
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		dstEntity = BigWorld.entities.get( dstEntity.id, None )
		if dstEntity is None:
			return
		
		dstEntity.getScript().taskStatus( dstEntity, self )
		
	def collectStatusForward( self, dstEntity ):
		"""
		define method
		@param 	dstEntity: 采集点
		@type   dstEntity: Entity
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity
		dstEntity = BigWorld.entities.get( dstEntity.id, None )
		if dstEntity is None:
			return
		
		dstEntity.getScript().collectStatus( dstEntity, self )
		
	def pickUpStatusForward( self, dstEntity, index ):
		"""
		define method
		@param 	dstEntity: 采集点
		@type   dstEntity: Entity
		@param 	index: 采集物品index
		@type   index: int8
		"""
		dstEntity = BigWorld.entities.get( dstEntity.id, None )
		if dstEntity is None:
			return
			
		dstEntity.getScript().onPickUpItemByIndex( dstEntity, self, index )
		
	def onIncreaseQuestTaskStateForward( self, dstEntity ):
		"""
		define method
		@param index: 要设定完成的任务目标的索引位置
		@type  index: INT16
		@param 	dstEntity: 任务箱子
		@type   dstEntity: Entity
		"""
		# 由于引擎mailbox自动转换为entity配置被改变为不转换，所以这里要手动转化为entity, kebiao
		dstEntity = BigWorld.entities[ dstEntity.id ]			
		dstEntity.getScript().onIncreaseQuestTaskState( dstEntity, self )
#
# $Log: not supported by cvs2svn $
# Revision 1.21  2007/12/19 04:08:46  kebiao
# 调整onIncreaseQuestTaskState相关接口 去掉索引参数
#
# Revision 1.20  2007/12/19 03:39:16  kebiao
# onSetQuestTaskComplete to onIncreaseQuestTaskState
#
# Revision 1.19  2007/12/19 02:13:27  kebiao
# 添加：onSetQuestTaskComplete完成某个任务目标
#
# Revision 1.18  2007/12/14 11:36:12  zhangyuxing
# 修改：questChooseReward 增加参数 kitTote, order
#
# Revision 1.17  2007/12/13 01:56:55  zhangyuxing
# no message
#
# Revision 1.16  2007/12/13 01:11:30  zhangyuxing
# 新增接口：def taskStatusForward( self, dstEntity)， 作用是
# 帮助查询任务目标。
#
# Revision 1.15  2007/11/23 06:37:39  phw
# removed: from NPC import NPC
#
# Revision 1.14  2007/10/29 04:09:05  yangkai
# 删除旧的材料合成，首饰合成相关接口
#
# Revision 1.13  2007/09/24 08:38:39  kebiao
# 删除:
# <setTempForward>
# <setForward>
#
# Revision 1.12  2007/06/26 00:40:52  kebiao
# 远程完成任务
#
# Revision 1.11  2007/06/19 08:34:16  huangyongwei
# 将任务状态定义由 csstatus 中搬到 csdefine 中
#
# Revision 1.10  2007/06/14 09:28:04  huangyongwei
# QUEST_STATE_NOT_HAVE 的定义被移动到 csstatus 中
#
# Revision 1.9  2007/06/14 00:38:16  kebiao
# 材料合成
#
# Revision 1.8  2007/04/06 04:24:09  kebiao
# 增加远程首饰合成
# mergeOrnamentForward
#
# Revision 1.7  2007/04/04 01:01:40  kebiao
# 去掉 acceptQuestForward 的key与val参数
#
# Revision 1.6  2007/03/20 02:00:29  kebiao
# 增加了远程设置玩家永久存储的标记
#
# Revision 1.5  2007/03/15 07:27:32  kebiao
# 添加远程接任务 设置任务值 设置玩家临时标记
#
# Revision 1.4  2006/12/21 11:06:30  phw
# change getSrcClass() to getScript()
#
# Revision 1.3  2006/06/08 09:12:45  phw
# no message
#
# Revision 1.2  2006/03/22 02:22:06  phw
# 增加方法questDetailForward()
#
# Revision 1.1  2006/02/28 08:04:23  phw
# no message
#
#