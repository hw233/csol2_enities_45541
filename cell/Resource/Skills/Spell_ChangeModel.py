# -*- coding: gb18030 -*-
#
#更换模型技能
#by wuxo 2012-3-22

from Spell_BuffNormal import Spell_BuffNormal

class Spell_ChangeModel( Spell_BuffNormal ):
	"""
	更换模型技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_BuffNormal.__init__( self )
		self.modelNumber = ""
		
	def init( self, dict ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )
		self.modelNumber = str(dict["param1"])
		if dict["param2"] != "" :
			self.modelScale  = float( dict["param2"] )
		else:
			self.modelScale  = 1.0

	def cast( self, caster, target ):
		"""
		virtual method.
		正式向一个目标或位置施放（或叫发射）法术，此接口通常直接（或间接）由intonate()方法调用。
		
		注：此接口即原来旧版中的castSpell()接口
		
		@param     caster: 使用技能的实体
		@type      caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell_BuffNormal.cast( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		接受者
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		receiver.setModelNumber( self.modelNumber )
		receiver.modelScale = self.modelScale
		self.receiveLinkBuff( caster, receiver )		# 接收额外的CombatSpell效果，通常是buff(如果存在的话)
	
