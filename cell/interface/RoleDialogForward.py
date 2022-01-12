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
		��ѯһ����Ϸ�������������������ҵ�״̬��״̬��ͨ���ص����ظ�client���Ӧ��GameObject��

		@param dstEntity: Ҫ��ѯ��һ����Ϸ���󷢷ŵ�����
		@type  dstEntity: Entity
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao

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
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		dstEntity = BigWorld.entities[ dstEntity.id ]			
		dstEntity.getScript().gossipWith( dstEntity, self, talkID )

	def questSelectForward( self, dstEntity, questID ):
		"""
		define method
		@type dstEntity: Entity
		@type   questID: INT32
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		dstEntity = BigWorld.entities[ dstEntity.id ]			
		dstEntity.getScript().questSelect( dstEntity, self, questID )

	def questAcceptForward( self, dstEntity, questID ):
		"""
		define method
		@type dstEntity: Entity
		@type   questID: INT32
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		dstEntity = BigWorld.entities[ dstEntity.id ]			
		dstEntity.getScript().questAccept( dstEntity, self, questID )

	def questDetailForward( self, dstEntity, questID ):
		"""
		define method
		@type dstEntity: Entity
		@type   questID: INT32
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		dstEntity = BigWorld.entities[ dstEntity.id ]			
		dstEntity.getScript().questDetail( dstEntity, self, questID )

	def questChooseRewardForward( self, dstEntity, questID, rewardIndex, codeStr ):
		"""
		define method
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		dstEntity = BigWorld.entities[ dstEntity.id ]			
		dstEntity.getScript().questChooseReward( dstEntity, self, questID, rewardIndex, codeStr )

	def gossipQuestChooseRewardForward( self, dstEntity, questID, rewardIndex ):
		"""
		define method
		@type   dstEntity: Entity
		@type     questID: INT32
		@type rewardIndex: INT8
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		dstEntity = BigWorld.entities[ dstEntity.id ]			
		dstEntity.getScript().gossipQuestChooseReward( dstEntity, self, questID, rewardIndex )

	def acceptQuestForward( self , questID  ):
		"""
		define method
		Զ�̽���һ������ ( ��Ǳ��������Ҫ��������ɹ�������NPC��ǰ����λ�� �����ҪԶ������ set ������������ַ����ȿ� )
		@param questID: ����ID
		"""
		quest = self.getQuest( questID )
		state = quest.query( self )
		if state == csdefine.QUEST_STATE_NOT_HAVE:
			quest.accept( self )

	def setQuestVal( self , questID , setKey , setVal ):
		"""
		define method
		Զ���������questsTable������ı��
		@param questID: ����ID
		@param setKey: �������ô洢�� key
		@param setVal: �������ô洢�� value
		"""
		if not self.questsTable.has_quest( questID ):
			return
		self.questsTable[questID].set( setKey , setVal )

	def completeQuestForward( self , questID , rewardIndex ):
		"""
		define method
		Զ���������
		@param setKey: �������ô洢 key
		@param setVal: �������ô洢�� value
		"""
		quest = self.getQuest( questID )
		if quest != None:
			quest.complete( self, rewardIndex )

	def taskStatusForward( self, dstEntity ):
		"""
		define method
		@param 	dstEntity: ��������
		@type   dstEntity: Entity
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		dstEntity = BigWorld.entities.get( dstEntity.id, None )
		if dstEntity is None:
			return
		
		dstEntity.getScript().taskStatus( dstEntity, self )
		
	def collectStatusForward( self, dstEntity ):
		"""
		define method
		@param 	dstEntity: �ɼ���
		@type   dstEntity: Entity
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity
		dstEntity = BigWorld.entities.get( dstEntity.id, None )
		if dstEntity is None:
			return
		
		dstEntity.getScript().collectStatus( dstEntity, self )
		
	def pickUpStatusForward( self, dstEntity, index ):
		"""
		define method
		@param 	dstEntity: �ɼ���
		@type   dstEntity: Entity
		@param 	index: �ɼ���Ʒindex
		@type   index: int8
		"""
		dstEntity = BigWorld.entities.get( dstEntity.id, None )
		if dstEntity is None:
			return
			
		dstEntity.getScript().onPickUpItemByIndex( dstEntity, self, index )
		
	def onIncreaseQuestTaskStateForward( self, dstEntity ):
		"""
		define method
		@param index: Ҫ�趨��ɵ�����Ŀ�������λ��
		@type  index: INT16
		@param 	dstEntity: ��������
		@type   dstEntity: Entity
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		dstEntity = BigWorld.entities[ dstEntity.id ]			
		dstEntity.getScript().onIncreaseQuestTaskState( dstEntity, self )
#
# $Log: not supported by cvs2svn $
# Revision 1.21  2007/12/19 04:08:46  kebiao
# ����onIncreaseQuestTaskState��ؽӿ� ȥ����������
#
# Revision 1.20  2007/12/19 03:39:16  kebiao
# onSetQuestTaskComplete to onIncreaseQuestTaskState
#
# Revision 1.19  2007/12/19 02:13:27  kebiao
# ��ӣ�onSetQuestTaskComplete���ĳ������Ŀ��
#
# Revision 1.18  2007/12/14 11:36:12  zhangyuxing
# �޸ģ�questChooseReward ���Ӳ��� kitTote, order
#
# Revision 1.17  2007/12/13 01:56:55  zhangyuxing
# no message
#
# Revision 1.16  2007/12/13 01:11:30  zhangyuxing
# �����ӿڣ�def taskStatusForward( self, dstEntity)�� ������
# ������ѯ����Ŀ�ꡣ
#
# Revision 1.15  2007/11/23 06:37:39  phw
# removed: from NPC import NPC
#
# Revision 1.14  2007/10/29 04:09:05  yangkai
# ɾ���ɵĲ��Ϻϳɣ����κϳ���ؽӿ�
#
# Revision 1.13  2007/09/24 08:38:39  kebiao
# ɾ��:
# <setTempForward>
# <setForward>
#
# Revision 1.12  2007/06/26 00:40:52  kebiao
# Զ���������
#
# Revision 1.11  2007/06/19 08:34:16  huangyongwei
# ������״̬������ csstatus �аᵽ csdefine ��
#
# Revision 1.10  2007/06/14 09:28:04  huangyongwei
# QUEST_STATE_NOT_HAVE �Ķ��屻�ƶ��� csstatus ��
#
# Revision 1.9  2007/06/14 00:38:16  kebiao
# ���Ϻϳ�
#
# Revision 1.8  2007/04/06 04:24:09  kebiao
# ����Զ�����κϳ�
# mergeOrnamentForward
#
# Revision 1.7  2007/04/04 01:01:40  kebiao
# ȥ�� acceptQuestForward ��key��val����
#
# Revision 1.6  2007/03/20 02:00:29  kebiao
# ������Զ������������ô洢�ı��
#
# Revision 1.5  2007/03/15 07:27:32  kebiao
# ���Զ�̽����� ��������ֵ ���������ʱ���
#
# Revision 1.4  2006/12/21 11:06:30  phw
# change getSrcClass() to getScript()
#
# Revision 1.3  2006/06/08 09:12:45  phw
# no message
#
# Revision 1.2  2006/03/22 02:22:06  phw
# ���ӷ���questDetailForward()
#
# Revision 1.1  2006/02/28 08:04:23  phw
# no message
#
#