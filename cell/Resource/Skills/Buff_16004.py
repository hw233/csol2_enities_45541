# -*- coding: gb18030 -*-
#
# $Id: Buff_16004.py,v 1.12 2008-08-11 07:55:59 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Rebound import Buff_Rebound_Magic

class Buff_16004( Buff_Rebound_Magic ):
	"""
	example:Ч������ʱ�����ܵ��ķ���������ת��һ����ֵ�����������ϡ�����ת�Ƶ�λ����Ϊ����

	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Rebound_Magic.__init__( self )
		self._p1 = 0 #
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Rebound_Magic.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) 	

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
		if caster.id == receiver.id or receiver.state == csdefine.ENTITY_STATE_DEAD or skill.getType() != csdefine.BASE_SKILL_TYPE_MAGIC:
			return
		
		value = int( self.initPhysicsDotDamage( receiver, caster, self._p1 ) )
		value = self.calcDotDamage( receiver, receiver, csdefine.DAMAGE_TYPE_MAGIC, value )
		if value <= 0:
			return
		caster.receiveSpell( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_REBOUND|csdefine.DAMAGE_TYPE_MAGIC, value, 0 )
		caster.receiveDamage( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_REBOUND|csdefine.DAMAGE_TYPE_MAGIC, value )
		SkillMessage.buff_ReboundDamageMagic( caster, receiver, value )

#
# $Log: not supported by cvs2svn $
# Revision 1.11  2008/04/10 04:08:26  kebiao
# ��Ϊ�ڽ����˺�֮ǰ֪ͨ�ͻ��˽��ܼ��ܴ���
#
# Revision 1.10  2008/04/10 03:25:50  kebiao
# modify to receiveSpell pertinent.
#
# Revision 1.9  2008/03/31 09:04:02  kebiao
# �޸�receiveDamage��֪ͨ�ͻ��˽���ĳ���ܽ���ֿ�
# ����ͨ��receiveSpell֪ͨ�ͻ���ȥ���֣�֧�ָ����ܲ�ͬ�ı���
#
# Revision 1.8  2008/02/13 09:26:30  kebiao
# ������IDҲ���䵽�ͻ���,ʹ����ʾ�˺�
#
# Revision 1.7  2008/02/13 08:54:58  kebiao
# ���������˺�û��ʩ����ID
#
# Revision 1.6  2008/02/13 08:41:30  kebiao
# ��������ʾ��Ϣ
#
# Revision 1.5  2008/01/30 08:59:37  kebiao
# �޸ķ�����Ϣ����ʽ
#
# Revision 1.4  2008/01/30 07:07:46  kebiao
# �޸��˼̳й�ϵ
#
# Revision 1.3  2007/12/21 08:52:11  kebiao
# no message
#
# Revision 1.2  2007/12/21 07:28:00  kebiao
# no message
#
# Revision 1.1  2007/12/20 03:34:17  kebiao
# no message
#
#