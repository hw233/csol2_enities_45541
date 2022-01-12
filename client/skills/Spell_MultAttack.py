# -*- coding: gb18030 -*-
#
# $Id: Spell_MultAttack.py,v 1.14 2008-08-06 06:17:09 qilan Exp $

"""
Spell�����ࡣ
"""
import BigWorld
from bwdebug import *
from SpellBase import *
from event.EventCenter import *
import ItemTypeEnum
import csstatus
from Function import Functor

class Spell_MultAttack( Spell ):
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		self._attackCount = int( dict[ "param1" ] )
		if self._attackCount <= 0: self._attackCount = 1

	def receiveSpell( self, target, casterID, damageType, damage  ):
		"""
		���ܼ��ܴ���

		@type   casterID: OBJECT_ID
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		player = BigWorld.player()
		if casterID:
			try:
				caster = BigWorld.entities[casterID]
			except KeyError:
				#�����������ԭ���� �ڷ�������һ��entity����һ��entityʩ�� ���������ǿ��ĵ�ʩ���ߵ�
				#���ͻ��˿��ܻ���Ϊĳԭ�� �磺�����ӳ� ���ڱ���û�и��µ�AOI�е��Ǹ�ʩ����entity����
				#��������ִ��� written by kebiao.  2008.1.8
				return
		else:
			caster = None

		count = 1
		if damage > 0:
			p2 = damage
			damage /= self._attackCount
			if target.HP < p2:
				count = target.HP / damage + 1
			else:
				count = self._attackCount
		# ������Ч����
		self._skillAE( player, target, caster, damageType, damage  )
		self.showSkillInfo( count, player, target, casterID, damageType, damage  )

	def showSkillInfo( self, attackCount, player, target, casterID, damageType, damage  ):
		"""
		# �˺���Ϣ��ʾ
		"""
		if target.isAlive():
			target.onReceiveDamage( casterID, self, damageType, damage  )							# ϵͳ��Ϣ
			if attackCount > 1:
				BigWorld.callback( 0.3, Functor( self.showSkillInfo, attackCount - 1, player, target, casterID, damageType, damage  ) )

#
# $Log: not supported by cvs2svn $
# Revision 1.13  2008/08/06 05:50:33  kebiao
# ����receiveDamage�ӿڲ��� skill.receiveSpell ȥ��skillID
#
# Revision 1.12  2008/08/06 03:31:31  kebiao
# ����receiveDamage�ӿڲ��� skill.receiveSpell ȥ��skillID
#
# Revision 1.11  2008/08/05 02:04:43  qilan
# �����˺�ϵͳ��Ϣ�ӿ�
#
# Revision 1.10  2008/07/07 09:17:24  kebiao
# �޸�����Ի�
#
# Revision 1.9  2008/07/05 01:07:13  kebiao
# no message
#
# Revision 1.8  2008/07/04 04:00:05  kebiao
# no message
#
# Revision 1.7  2008/07/04 01:06:14  zhangyuxing
# ���������󣬲�����ʾ��Ϣ
#
# Revision 1.6  2008/05/29 05:56:17  kebiao
# no message
#
# Revision 1.5  2008/05/28 07:47:46  kebiao
# no message
#
# Revision 1.3  2008/05/28 07:31:56  kebiao
# no message
#
#