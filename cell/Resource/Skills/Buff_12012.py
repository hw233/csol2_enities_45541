# -*- coding: gb18030 -*-
#
# $Id: Buff_12012.py,v 1.7 2008-05-28 02:09:42 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
import random

STATES = csdefine.ACTION_FORBID_MOVE
				 
class Buff_12012( Buff_Normal ):
	"""
	example:�������в���Ч��	BUFF	�������в���Ч��	ʹ��λ���ᱻѣ�Ρ���˯����Ĭ���������ƶ��ٶȡ��������ٶ�

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
		
	def springOnImmunityBuff( self, caster, receiver, buffData ):
		"""
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		buff = buffData[ "skill" ]
		if buff.cancelBuff( [csdefine.BUFF_INTERRUPT_INVINCIBLE_EFFECT] ):
			return csstatus.SKILL_BUFF_IS_RESIST
			
		return csstatus.SKILL_GO_ON
		
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
		receiver.appendImmunityBuff( buffData[ "skill" ] )
		receiver.clearBuff( [csdefine.BUFF_INTERRUPT_INVINCIBLE_EFFECT] ) #ɾ�������������п���ɾ����BUFF
		
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
		receiver.appendImmunityBuff( buffData[ "skill" ] )
		
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
		receiver.removeImmunityBuff( buffData[ "skill" ].getUID() )
		
#
# $Log: not supported by cvs2svn $
# Revision 1.6  2008/02/28 08:25:56  kebiao
# �ı�ɾ������ʱ�ķ�ʽ
#
# Revision 1.5  2007/12/25 06:42:57  kebiao
# �޸�����BUFF
#
# Revision 1.4  2007/12/24 09:17:38  kebiao
# ����springOnImmunityBuff����
#
# Revision 1.3  2007/12/22 07:36:43  kebiao
# ADD:IMPORT csstatus
#
# Revision 1.2  2007/12/22 02:26:57  kebiao
# ����������ؽӿ�
#
# Revision 1.1  2007/12/20 06:10:56  kebiao
# no message
#
#