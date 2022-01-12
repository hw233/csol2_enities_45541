# -*- coding: gb18030 -*-

import BigWorld
import csdefine
from Buff_Normal import Buff_Normal

class Buff_299036( Buff_Normal ):
	"""
	���ĳ����״̬�������ɣ�δ�ύ����֪ͨ����ˢ��������
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self.questID = 0
		self.spaceName = ""

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self.questID = int(dict["Param1"])
		self.spaceName = dict["Param2"]
		
	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		����buff����ʾbuff��ÿһ������ʱӦ����ʲô��

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL�������������򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		spaceBase = receiver.getCurrentSpaceBase()
		spaceEntity = BigWorld.entities.get( spaceBase.id )
		if spaceEntity:
			if spaceEntity.className != "xin_fei_lai_shi_001_25_dao":
				return False
			q = receiver.getQuest( self.questID )
			if q:
				state = q.query( receiver )
				if state == csdefine.QUEST_STATE_FINISH:
					spaceEntity.getScript().spawnTransportDoor( spaceEntity )
					return False
		
		return Buff_Normal.doLoop( self, receiver, buffData )