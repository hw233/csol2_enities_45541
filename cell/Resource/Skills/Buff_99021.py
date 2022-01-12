# -*- coding: gb18030 -*-
#
#


import BigWorld
import csconst
import csstatus
import Const
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_99021( Buff_Normal ):
	"""
	"������BUFF099021��֧�֣�����ʹ�����е���ͨBUFF�ű���
	��ɫ�ڴ��ڴ�BUFFʱ����������������ͨ�ø�����ʾ֮ǰ����ʾ��ҡ��Ƿ�ʹ�÷����ԭ�ظ����ѡ���ǡ���
	BUFF��ʧԭ�ظ��ѡ�񡰷񡱣�BUFF��������ʾ������ͨ�ø�����ʾ��"	
	
	2	����	322441	�����	����	���Լ����������һ��״̬���ڴ�״̬������ʱ���ɾ͵ظ�����ָ���������������״̬����10����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) / 100.0
		
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
	
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		if not receiver.state == csdefine.ENTITY_STATE_DEAD:
			return

		receiver.setHP( receiver.HP_Max * self._p1 )
		receiver.setMP( receiver.MP_Max * self._p1 )
		receiver.changeState( csdefine.ENTITY_STATE_FREE )
		receiver.updateTopSpeed()
		