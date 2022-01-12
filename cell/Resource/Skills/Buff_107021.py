# -*- coding:gb18030 -*-

import csstatus
import csdefine
from bwdebug import *
import Const
from Buff_Normal import Buff_Normal
from Function import newUID

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_JUMP


class Buff_107021( Buff_Normal ):
	"""
	dota中谜团的F，隔几秒钟对目标造成眩晕/定身/昏睡效果
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self.effectInterval = 1							# 效果作用周期时长，注意：这个不能大于非效果作用周期
		self.noEffectInterval = 1						# 非效果作用周期时长
		self.effect = csdefine.EFFECT_STATE_VERTIGO		# 默认的效果
		self.isEffect = False							# 效果是否在作用中
		self.tickCount = 0								# 处于效果/不处于效果状态持续时长，每一个tick是1秒
		
	def init( self, data ):
		"""
		"""
		Buff_Normal.init( self, data )
		self.effect = int( data["Param1"] )				# 默认的效果
		self.effectInterval = int( data["Param2"] )		# 效果作用周期时长，注意：这个不能大于非效果作用周期
		self.noEffectInterval = int( data["Param3"] )	# 非效果作用周期时长
		
	def doBeginEffect( self, receiver ):
		"""
		开始效果
		"""
		# 加入移动限制，以确保buff对移动限制效果生效 by姜毅
		if receiver.isMoving():
			receiver.stopMoving()
		# 执行附加效果
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( self.effect )
		self.isEffect = True
		self.tickCount = 0
		
	def doEndEffect( self, receiver ):
		"""
		结束效果
		"""
		receiver.effectStateDec( self.effect )
		receiver.actCounterDec( STATES )
		
		self.isEffect = False
		self.tickCount = 0
		
		
	def doBegin( self, receiver, buffData ):
		"""
		"""
		if receiver.attrIntonateTimer > 0 and receiver.attrIntonateSkill.getType() in Const.INTERRUPTED_BASE_TYPE or\
			( receiver.attrHomingSpell and receiver.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ) :
			receiver.interruptSpell( csstatus.SKILL_IN_BLACKOUT )
		self.doBeginEffect( receiver )
		
	def doLoop( self, receiver, buffData ):
		"""
		"""
		self.tickCount += 1
		if self.isEffect:
			if self.tickCount == self.effectInterval:
				self.doEndEffect( receiver )
		else:
			if self.tickCount == self.noEffectInterval:
				self.doBeginEffect( receiver )
		return Buff_Normal.doLoop( self, receiver, buffData )
		
	def doEnd( self, receiver, buffData ):
		Buff_Normal.doEnd( self, receiver, buffData )
		self.doEndEffect( receiver )
		
	def addToDict( self ):
		"""
		"""
		return { "param": { "isEffect":self.isEffect, "tickCount":self.tickCount } }
		
	def createFromDict( self, data ):
		"""
		"""
		obj = Buff_107021()
		obj.__dict__.update( self.__dict__ )
		obj.isEffect = data["param"]["isEffect"]
		obj.tickCount = data["param"]["tickCount"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
		