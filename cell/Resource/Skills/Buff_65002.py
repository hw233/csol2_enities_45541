# -*- coding: gb18030 -*-
#
# $Id: Buff_65002.py,v 1.7 2008-09-04 07:46:27 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csdefine
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_65002( Buff_Normal ):
	"""
	example:ͬ���ھ�	BUFF	�����˺�/�˺�����	BUFF����ʱ�ܵ����˺����һ���ٷֱȣ���ʹ�������ܵ����˺���ֵ��һ���ٷֱȵ��������˺�%
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0 #�ܵ����˺���߼ӳ�
		self._p2 = 0 #�����˺�����
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100	
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )  / 100.0	

	def springOnDamage( self, caster, receiver, skill, damage ):
		"""
		virtual method.
		���˺�����󣨼�����˺�����ʱ�˿����Ѿ����ˣ�����������Ҫ����һЩ��Ҫ���ܵ��˺��Ժ��ٴ�����Ч����

		�����ڣ�
		    ����Ŀ��ʱ$1%���ʸ���Ŀ������˺�$2
		    ����Ŀ��ʱ$1%����ʹĿ�깥��������$2������$3��
		    ������ʱ$1���ʻָ�$2����
		    ������ʱ$1%�����������$2������$3��
		    etc.
		@param   caster: ʩ����
		@type    caster: Entity
		@param   receiver: ������
		@type    receiver: Entity
		@param   skill: ����ʵ��
		@type    skill: Entity
		@param   damage: ʩ������ɵ��˺�
		@type    damage: int32
		"""
		#ʹ�Լ��ܵ��������˺���ߣ����Ұ���ʱ�ܵ��˺���x%�����������ߣ�����������˺��ǲ������С����������ܡ��мܡ�������
		rebound_damage = damage * self._p2
		rebound_damage = self.calcDotDamage( receiver, receiver, csdefine.DAMAGE_TYPE_VOID, rebound_damage )		
		if rebound_damage <= 0: return
		caster.receiveSpell( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_REBOUND|csdefine.DAMAGE_TYPE_VOID, rebound_damage, 0 )
		caster.receiveDamage( receiver.id, 0, csdefine.DAMAGE_TYPE_REBOUND|csdefine.DAMAGE_TYPE_VOID, rebound_damage )
		
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
		receiver.receive_damage_percent += self._p1
		receiver.receive_magic_damage_percent += self._p1
		receiver.appendVictimAfterDamage( buffData[ "skill" ] )
		
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
		receiver.receive_damage_percent += self._p1
		receiver.receive_magic_damage_percent += self._p1
		receiver.appendVictimAfterDamage( buffData[ "skill" ] )
		
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
		receiver.receive_damage_percent -= self._p1
		receiver.receive_magic_damage_percent -= self._p1
		receiver.removeVictimAfterDamage( buffData[ "skill" ].getUID() )
#
# $Log: not supported by cvs2svn $
# Revision 1.6  2008/08/11 07:55:59  kebiao
# ����BUFF�˺���DOLOOPʱ δ���л������ղ���
#
# Revision 1.5  2008/04/10 04:08:26  kebiao
# ��Ϊ�ڽ����˺�֮ǰ֪ͨ�ͻ��˽��ܼ��ܴ���
#
# Revision 1.4  2008/04/10 03:25:50  kebiao
# modify to receiveSpell pertinent.
#
# Revision 1.3  2008/03/31 09:04:02  kebiao
# �޸�receiveDamage��֪ͨ�ͻ��˽���ĳ���ܽ���ֿ�
# ����ͨ��receiveSpell֪ͨ�ͻ���ȥ���֣�֧�ָ����ܲ�ͬ�ı���
#
# Revision 1.2  2008/02/28 08:25:56  kebiao
# �ı�ɾ������ʱ�ķ�ʽ
#
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
# 
#