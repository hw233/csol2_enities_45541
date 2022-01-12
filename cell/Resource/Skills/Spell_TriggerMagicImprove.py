# -*- coding: gb18030 -*-

#edit by wuxo 2012-2-9

from Spell_MagicImprove import Spell_MagicImprove


class Spell_TriggerMagicImprove(Spell_MagicImprove):
	def __init__( self ) :
		Spell_MagicImprove.__init__( self )
		self._triggerSpellID = 0	#触发的技能ID
		self._triggerTime    = 0	#当前技能处于触发可使用状态（母技能此项参数无需填写）	
		self._parentID       = 0         #母技能ID
		
	def init( self, dictData ):
		"""
		读取技能配置
		@param dictData:	配置数据
		@type dictData:	python dictData
		"""
		Spell_MagicImprove.init( self, dictData )
		
		if dictData["param2"] != "":
			self._parentID = int( dictData["param2"] )	
		
		if dictData["param3"] != "":
			self._triggerSpellID = int( dictData["param3"] )
		
		if dictData["param4"] != "":
			self._triggerTime  = float( dictData["param4"] ) #触发的技能持续时间
		
		
		
	def cast( self, caster, target ):
		"""
		正式向一个目标或位置施放
		"""
		Spell_MagicImprove.cast( self, caster, target )
		
		if self._parentID == 0:
			self._parentID = self.getID()
		caster.addTriggerSpell(self._parentID, self._triggerSpellID)
		
		
	def getTriggerTime(self):
		"""
		获得当前技能（被触发）处于可释放状态的时间
		"""
		return self._triggerTime