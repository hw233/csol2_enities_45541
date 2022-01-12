# -*- coding: gb18030 -*-
#
# $Id: Buff_65004.py,v 1.4 12:16 2010-5-19 jiangyi Exp $

"""
������Ч��
"""
import random
import BigWorld
import csconst
import csdefine
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_65004( Buff_Normal ):
	"""
	example:buff����ʱЧ�ڣ���λ�κ�һ�γɹ�������������Ϊ�����߻ָ��൱�ڱ����˺���x%�ķ���ֵ
				���۳�Ŀ������ķ���ֵ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0 #��Ϊ�����߻ָ��൱�ڱ����˺���x%������ֵ
		 
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / 100.0	
		self.odd = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )

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
		n_odd = random.randint(0,100)
		if self.odd > 0 and n_odd > self.odd:
			return
		if skill.getType() != csdefine.BASE_SKILL_TYPE_PHYSICS and skill.getType() != csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL:
			return
		mpAdd = int( damage * self._p1 )
		if mpAdd > 0:
			caster.addMP( mpAdd )

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
		receiver.appendAttackerAfterDamage( buffData[ "skill" ] )
		
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
		receiver.appendAttackerAfterDamage( buffData[ "skill" ] )
		
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
		receiver.removeAttackerAfterDamage( buffData[ "skill" ].getUID() )
#
# $Log: not supported by cvs2svn $
# Revision 1.3  2007/12/21 04:21:10  kebiao
# ����һЩBUG
#
# Revision 1.2  2007/12/06 08:14:04  kebiao
# �޸�BUG
#
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
# 
#