# -*- coding: gb18030 -*-

# 系统技能，生成一个AreaRestrictTransducer的entity(陷阱功能entity)，在施放者位置

import BigWorld
import csdefine
import csstatus
from SpellBase.HomingSpell import HomingSpellBuff
import Love3

class Spell_power_catch( HomingSpellBuff ):
	"""
	系统技能
	生成一个AreaRestrictTransducer的entity(陷阱功能entity)
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		HomingSpellBuff.__init__( self )
		self.buff = 0					# 陷阱销毁时间


	def init( self, dictData ):
		"""
		读取技能配置
		@param dictData:	配置数据
		@type dictData:	python dictData
		"""
		HomingSpellBuff.init( self, dictData )
		self._buffID = int( dictData["param4"] )
		HomingSpellBuff.init( self, dictData )



	def onInterrupted( self, caster, reason ):
		"""
		引导技能被打断回调
		"""
		HomingSpellBuff.onInterrupted( self, caster, reason )
		if reason == csstatus.SKILL_INTERRUPTED_BY_SPELL_3:
			Love3.g_skills[self._buffID].receiveLinkBuff( None, caster )


	def canInterruptSpell( self, reason ):
		"""
		可否被该原因打断
		"""
		return reason != csstatus.SKILL_INTERRUPTED_BY_SPELL_2

