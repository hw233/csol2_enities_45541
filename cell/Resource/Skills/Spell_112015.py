# -*- coding: gb18030 -*-
#
# $Id: Spell_112015.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from Spell_Magic import Spell_Magic


class Spell_112015( Spell_Magic ):
	"""
	������������������Χ�е�λ���һ�λ�ϵ�����˺���
	"""
	def __init__( self ):
		"""
		"""
		Spell_Magic.__init__( self )
	
	
	def getReceivers( self, caster, target ):
		"""
		virtual method
		ȡ�����еķ���������������Entity�б�
		���е�onArrive()������Ӧ�õ��ô˷�������ȡ��Ч��entity��
		@return: array of Entity

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		receivers = self._receiverObject.getReceivers( caster, target )
		receivers.append( caster )
		return receivers
		

#$Log: not supported by cvs2svn $
#
#