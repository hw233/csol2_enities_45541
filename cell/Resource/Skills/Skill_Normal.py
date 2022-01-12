# -*- coding: gb18030 -*-
#
# $Id: Skill_Normal.py,v 1.7 2008-08-13 07:55:41 kebiao Exp $

"""
���������ࡣ
"""

from bwdebug import *
from SpellBase.Spell import Spell
import BigWorld
import csconst
import csstatus
import csdefine

class Skill_Normal( Spell ):
	"""
		���ܵĳ�����Ч��
		����"Buff"�����"Buff_"��ͷ
		ע������Ϊ�ɰ��е�Condition��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )

	def getType( self ):
		"""
		ȡ�û�����������
		��Щֵ��BASE_SKILL_TYPE_*֮һ
		"""
		return csdefine.BASE_SKILL_TYPE_PASSIVE
		
	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		ΪĿ�긽��һ��Ч����ͨ�������ϵ�Ч����ʵ������������ͨ��detach()ȥ�����Ч��������Ч���ɸ����������о�����
		
		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		pass

	def detach( self, ownerEntity ):
		"""
		virtual method = 0;
		ִ����attach()�ķ������

		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		pass
			
	def use( self, caster, receiver, position ):
		"""
		virtual method = 0.
		����� target/position ʩչһ���������κη�����ʩ������ɴ˽���
		dstEntity��position�ǿ�ѡ�ģ����õĲ�����None���棬���忴���������Ƕ�Ŀ�껹��λ�ã�һ��˷���������client����ͳһ�ӿں���ת������
		Ĭ��ɶ��������ֱ�ӷ��ء�
		ע���˽ӿڼ�ԭ���ɰ��е�cast()�ӿ�
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ��ߣ�None��ʾ������
		@type  receiver: Entity
		@param position: λ��
		@type  position: VECTOR3
		"""
		ERROR_MSG( "I not support this the function!" )
		return

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param   receiver: Ŀ��ʵ�壬���û�н�������ΪNone
		@type    receiver: Entity
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		ERROR_MSG( "I not support this the function!" )
		return csstatus.SKILL_UNKNOW
		
	def receive( self, caster, receiver ):
		"""
		virtual method = 0.
		���ÿһ�������߽�����������������˺����ı����Եȵȡ�
		ͨ������´˽ӿ�����onArrive()���ã��������п�����SpellUnit::receiveOnreal()�������ã�
		���ڴ���һЩ��Ҫ�������ߵ�real entity�����������顣�������Ƿ���Ҫ��real entity���Ͻ��գ�
		�ɼ����������receive()�����йضϣ������ṩ��ػ��ơ�
		
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		ERROR_MSG( "I not support this the function!" )
		return

	def newSelf( self ):
		"""
		����һ���µ�UID����ʵ��
		"""
		data = self.addToDict()
		return self.createFromDict( data )

#
# $Log: not supported by cvs2svn $
# Revision 1.6  2008/02/27 07:57:15  kebiao
# add:import csdefine
#
# Revision 1.5  2007/12/25 09:31:59  kebiao
# delete:
# import Effects
#
# Revision 1.4  2007/10/26 07:06:41  kebiao
# ����ȫ�µĲ߻�ս��ϵͳ������
#
# Revision 1.3  2007/08/15 03:28:41  kebiao
# �¼���ϵͳ
#
# Revision 1.2  2007/07/10 07:54:57  kebiao
# ���µ������������ܽṹ��˸�ģ�鲿�ֱ��޸�
#
#
#