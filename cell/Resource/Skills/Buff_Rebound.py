# -*- coding: gb18030 -*-
#
# $Id: Buff_Rebound.py,v 1.5 2008-02-28 08:25:56 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_Rebound( Buff_Normal ):
	"""
	�˺��������
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
		pass
			
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
		receiver.removeVictimAfterDamage( buffData[ "skill" ].getUID() )
		
class Buff_Rebound_Magic( Buff_Rebound ):
	"""
	�����˺��������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Rebound.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Rebound.init( self, dict )
		
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
		pass
#
# $Log: not supported by cvs2svn $
# Revision 1.4  2008/02/13 08:46:53  kebiao
# �޸��˵ײ�ṹ
#
# Revision 1.3  2008/01/30 09:00:07  kebiao
# add: Buff_Rebound_Magic
#
# Revision 1.2  2008/01/30 07:24:31  kebiao
# ����һ����ʽ����
#
# Revision 1.1  2008/01/30 07:08:14  kebiao
# no message
#
#