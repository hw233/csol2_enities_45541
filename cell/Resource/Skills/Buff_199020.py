# -*- coding: gb18030 -*-
#


"""
Ŀ����5���ը�����Լ�����Χ5��������������20%�������˺���
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
import csdefine

class Buff_199020( Buff_Normal ):
	"""
	Ŀ����5���ը�����Լ�����Χ5��������������20%�������˺���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0
		self._p2 = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = float( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) / 100	# �˺�
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )		# Ѱ�ҷ�Χ

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���
		buff �����󣬱�ը
		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		
		damage = int( receiver.HP_Max * self._p1 )
		receiver.receiveSpell( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_PHYSICS, damage, 0 )
		receiver.receiveDamage( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_PHYSICS, damage )

		for i in receiver.entitiesInRangeExt( self._p2, "Role", receiver.position ):
			damage = int( i.HP_Max * self._p1 )
			i.receiveSpell( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_PHYSICS, damage, 0 )
			i.receiveDamage( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_PHYSICS, damage )
		for i in receiver.entitiesInRangeExt( self._p2, "Pet", receiver.position ):
			damage = int( i.HP_Max * self._p1 )
			i.receiveSpell( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_PHYSICS, damage, 0 )
			i.receiveDamage( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_PHYSICS, damage )
#