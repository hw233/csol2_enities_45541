# -*- coding: gb18030 -*-
#
# $Id: Buff_22001.py,v 1.2 2008-05-19 08:01:12 kebiao Exp $

"""
��õ���ʱ��buff
"""

import BigWorld
import csconst
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_99013( Buff_Normal ):
	"""
	��õ���ʱ���buff��
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

	def receive( self, caster, receiver ):
		"""
		���ڸ�Ŀ��ʩ��һ��buff�����е�buff�Ľ��ն�����ͨ���˽ӿڣ�
		�˽ӿڱ����жϽ������Ƿ�ΪrealEntity��
		����������Ҫͨ��receiver.receiveOnReal()�ӿڴ���

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ��ߣ�None��ʾ������
		@type  receiver: Entity
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( casterID, self )
			return

		if receiver.getState() == csdefine.ENTITY_STATE_DEAD:
			return

		buffs = receiver.findBuffsByBuffID( self._buffID )
		#�ж��Ƿ�����ͬ��buff
		if len( buffs ) > 0:
			# �Ѵ�����ͬ���͵�buff
			self.doAppend( receiver, buffs[0] )
		else:
			receiver.addBuff( self.getNewBuffData( caster, receiver ) )
		receiver.statusMessage( csstatus.SKILL_CAST_ADD_FISH_TIME, self._persistent / 60 )

	def doAppend( self, receiver, buffIndex ):
		"""
		Virtual method.
		��һ�������Ѿ����ڵ�ͬ����BUFF����׷�Ӳ���
		�����BUFF����׷��ʲô�ɼ̳��߾���
		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffs: �������ͬ���͵�BUFF����attrbuffs��λ��,BUFFDAT ����ͨ�� receiver.getBuff( buffIndex ) ��ȡ
		"""
		buffdata = receiver.getBuff( buffIndex )
		sk = buffdata["skill"]
		buffdata["persistent"] += self._persistent
		receiver.client.onUpdateBuffData( buffIndex, buffdata )

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
		receiver.setTemp( "has_fishing_time", True )	# ��¼����Ƿ��ܵ���ı��
		Buff_Normal.doReload( self, receiver, buffData )

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
		receiver.setTemp( "has_fishing_time", True )	# ��¼����Ƿ��ܵ���ı��
		Buff_Normal.doBegin( self, receiver, buffData )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		if receiver.getState() == csdefine.ENTITY_STATE_CHANGING:
			# ʹ����·��Ҫȡ������״̬
			receiver.end_body_changing( receiver.id,"" )
		receiver.removeTemp( "has_fishing_time" )	# �������¼����Ƿ��ܵ���ı��