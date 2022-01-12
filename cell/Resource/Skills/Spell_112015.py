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
	引火烧身，对自身及其周围敌单位造成一次火系法术伤害。
	"""
	def __init__( self ):
		"""
		"""
		Spell_Magic.__init__( self )
	
	
	def getReceivers( self, caster, target ):
		"""
		virtual method
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。
		@return: array of Entity

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		receivers = self._receiverObject.getReceivers( caster, target )
		receivers.append( caster )
		return receivers
		

#$Log: not supported by cvs2svn $
#
#