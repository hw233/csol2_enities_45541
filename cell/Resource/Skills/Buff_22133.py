# -*- coding: gb18030 -*-
#
import BigWorld
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
import random
import time
import csconst

class Buff_22133( Buff_Normal ):
	"""
	��buff���ڼ����Ӫ��������,buff����ʱ�Ƴ���Ӫ����. add by cwl
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		
	def receive( self, caster, receiver ):
		"""
		���ڸ�Ŀ��ʩ��һ��buff�����е�buff�Ľ��ն�����ͨ���˽ӿڣ�
		�˽ӿڱ����жϽ������Ƿ�ΪrealEntity��
		����������Ҫͨ��receiver.receiveOnReal()�ӿڴ���

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( casterID, self )
			return

		buffs = receiver.findBuffsByBuffID( self._buffID )

		#�ж��Ƿ�����ͬ��buff
		if len( buffs ) > 0:
			# �Ѵ�����ͬ���͵�buff
			return
		else:
			receiver.addBuff( self.getNewBuffData( caster, receiver ) )

	def calculateTime( self, caster ):
		"""
		virtual method.
		ȡ�ó���ʱ��
		"""
		if not BigWorld.globalData.has_key( "CampActivityEndTime" ):
			return 1
		return BigWorld.globalData["CampActivityEndTime"]

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч����ʼ�Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.set( "CampQuestEndTime", self.calculateTime( None ) )		# ��¼������Ӫ�����ʱ��

	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�����¼��صĴ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		if BigWorld.globalData.has_key( "CampActivityEndTime" ) and receiver.query( "CampQuestEndTime", 0 ) == BigWorld.globalData["CampActivityEndTime"]:
			return
		# ��������������˵���ϴ���Ӫ��ѽ������Ƴ���buff
		receiver.removeBuffByBuffID( self._buffID, [0] )

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
		if not BigWorld.globalData.has_key( "CampActivityEndTime" ):
			return False
		if len( receiver.findQuestByType( csdefine.QUEST_TYPE_CAMP_ACTIVITY ) ) <= 0 and len( receiver.findQuestByType( csdefine.QUEST_TYPE_CAMP_DAILY ) ) <= 0:
			return False
		return Buff_Normal.doLoop( self, receiver, buffData )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		receiver.remove( "CampQuestEndTime" )
		receiver.removeFailedCampQuests()			# �Ƴ�����ʧ�ܵ���Ӫ����