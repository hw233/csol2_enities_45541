# -*- coding: gb18030 -*-
import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_22128( Buff_Normal ):
	"""
	��BUFF�ڸ���ʱ�䵽��֮�����һ����QTTaskEventTrigger����������10�������п�ͼ������ by mushuang
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self.questID = 0
		self.taskIndex = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		# Param1 ����ID
		# Param2 ����Ŀ������
		Buff_Normal.init( self, dict )
		self.questID = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )
		self.taskIndex = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )

	def doLoop( self, receiver, buffData ):
		"""
		irtual method; call only by real entity.
		����buff����ʾbuff��ÿһ������ʱӦ����ʲô��

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL�������������򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		# ����������ϵ���Ӧ���״̬
		receiver.questTaskIncreaseState( self.questID, self.taskIndex )
		return True
