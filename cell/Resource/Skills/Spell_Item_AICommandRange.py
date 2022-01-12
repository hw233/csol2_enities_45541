# -*- coding:gb18030 -*-

from Spell_Item import Spell_Item
from bwdebug import *
import random

class Spell_Item_AICommandRange( Spell_Item ):
	"""
	通过技能向一定范围内特定的怪物发送AI指令
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		self.classNames = []								# 指令发送对象
		self.commandString = 0								# AI指令
		self.range = 0.0									# 搜索范围
		self.amount = 0										# 发送数量
		
	def init( self, data ):
		"""
		"""
		Spell_Item.init( self, data )
		self.classNames = data["param1"].split( "|" )
		self.commandString = int( data["param2"] ) if len( data["param2"] ) > 0 else 0
		self.range = float( data["param3"] ) if data["param3"] else 0.0
		self.amount = int( data["param4"] ) if data["param4"] else 0
		
	def receive( self, caster, receiver ):
		"""
		"""
		if  not self.commandString:
			ERROR_MSG( "Skill %i config error, param2 is None "  % self.getID() )
			return
		
		receiver.sendAICommand( receiver.id, self.commandString )							# 不论发送对象和搜索范围是什么，受术者都给自己发指令
		
		if ( len( self.classNames ) == 0 or self.classNames == [""] ) and not self.range: 	# 若className为空，且范围为0，则只给受术者发指令
			return
		
		sendList= []
		monsterList = receiver.entitiesInRangeExt( self.range, None, receiver.position )
		for e in monsterList:																# 先将符合条件的怪物筛选出来
			if len( self.classNames ) == 0 or self.classNames == [""]:						# 若className为空，则默认给与受术者同类型的怪物发指令
				if e.className == receiver.className:
					sendList.append( e )
			else:
				if e.className in self.classNames:											# 若classNames不为空，则发送AI指令给指定的怪物
					sendList.append( e )
		
		amount = 1
		while( len( sendList ) ):
			if self.amount and amount >= self.amount:										# 若有发送数量限制，满足数量后返回
				return
			i = random.randint( 0, len( sendList ) - 1 )									# 随机选择发送目标
			e = sendList[ i ]
			e.sendAICommand( e.id, self.commandString )
			amount += 1
			sendList.remove( e )
