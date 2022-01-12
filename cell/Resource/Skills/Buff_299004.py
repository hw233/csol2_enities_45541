# -*- coding: gb18030 -*-

import BigWorld
from Buff_Normal import Buff_Normal

class Buff_299004( Buff_Normal ):
	"""
	火焰路径生成Buff
	"""
	def __init__( self ):
		"""
		构造函数
		"""
		Buff_Normal.__init__( self )
		self.lifeTime = 0				# 陷阱销毁时间
		self.repeatTime = 0				# 循环伤害时间
		self.loopTime = 0.0				# 生成陷阱间隔时间
		self.radius = 0.0				# 陷阱半径
		self.enterSpell = 0				# 进入陷阱施放的技能
		self.leaveSpell = 0				# 离开陷阱施放的技能
		self.destroySpell = 0			# 陷阱死亡时释放的技能
		self.modelNumber =  ""			# 陷阱对应的模型(带光效的)
		self.isDisposable = 0			# 是否一次性陷阱（即触发一次就销毁）
		self.skillID = 0				# 陷阱自带技能ID
		self.moveEffective = False		# 是否移动生效，默认移动生效

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		timeStr = dict["Param1"].split( ";" )
		if len( timeStr ) >= 3:
			self.lifeTime = int( timeStr[0] )
			self.repeatTime = int( timeStr[1] )
			self.loopTime = float( timeStr[2] )
		spellStr = dict["Param2"].split( ";" )
		if len( spellStr ) >= 4:
			self.enterSpell = int( spellStr[0] )
			self.leaveSpell = int( spellStr[1] )
			self.destorySpell = int( spellStr[2] )
			self.skillID = int( spellStr[3] )
		modelStr = dict["Param3"].split( ";" )
		if len( modelStr ) >= 3:
			self.radius = float( modelStr[0] )
			self.isDisposable = int( modelStr[1] )
			self.modelNumber = str( modelStr[2] )
			try:
				self.moveEffective = bool( int( modelStr[3] ) )
			except:
				self.moveEffective = False	# 不填默认移动生效

	def _getDict( self, receiver ):
		"""
		"""
		dict = { "radius" : self.radius, \
			"enterSpell" : self.enterSpell, \
			"leaveSpell" : self.leaveSpell, \
			"destroySpell" : self.destroySpell, \
			"originSkill" : self.getID(), \
			"modelNumber" : self.modelNumber, \
			"isDisposable" : self.isDisposable, \
			"lifetime" : self.lifeTime, \
			"repeattime" : self.repeatTime, \
			"casterID" : receiver.id, \
			"uname" : self.getName() }
		return dict

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		# 生成火焰陷阱
		receiver.setTemp( "FLAME_TRAP_DICT", self._getDict( receiver ) )
		receiver.setTemp( "FLAME_SKILLID", self.skillID )
		receiver.setTemp( "FLAME_MOVE_EFFECTIVE", self.moveEffective )
		receiver.getFlameWay( self.loopTime )

	def doReload( self,  receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		# 生成火焰陷阱
		receiver.setTemp( "FLAME_TRAP_DICT", self._getDict( receiver ) )
		receiver.setTemp( "FLAME_SKILLID", self.skillID )
		receiver.setTemp( "FLAME_MOVE_EFFECTIVE", self.moveEffective )
		receiver.getFlameWay( self.loopTime )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.delFlameWay()
