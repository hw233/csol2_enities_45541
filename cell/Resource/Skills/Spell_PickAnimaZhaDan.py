# -*- coding: gb18030 -*-
from Spell_BuffNormal import *

class Spell_PickAnimaZhaDan( Spell ):
	"""
	拾取灵气玩法炸弹效果
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		self.destroyAnimaRange = 0.0 # 销毁多大范围的灵气
		self.isResertCount = False #是否重置继续数
	
	def init( self, data ):
		"""
		读取技能配置
		@param data: 配置数据
		@type  data: python dict
		"""
		Spell.init( self, data )
		self.destroyAnimaRange = float( data[ "param1" ] )
		self.isResertCount = bool( data[ "param2" ] )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		self.receiveLinkBuff( caster, receiver )
		if self.destroyAnimaRange:
			desList = receiver.entitiesInRangeExt( self.destroyAnimaRange, "TrapPickAnima", receiver.position )
			for trap in desList:
				trap.destroy()
				
		if self.isResertCount:
			receiver.getCurrentSpaceCell().resertAddition( receiver.planesID, receiver )