# -*- coding:gb18030 -*-
import BigWorld
import csconst
import csdefine

from Buff_Normal import Buff_Normal
from bwdebug import *

LOCAK_CHAT_CHANNELS = [ csdefine.CHAT_CHANNEL_NEAR, ]

class Buff_299033( Buff_Normal ):
	# 给玩家添加一个潜身观战状态
	def __init__( self ):
		Buff_Normal.__init__( self )
		self.spaceEnable = []
		
	def init( self, data ):
		Buff_Normal.init( self, data )
		if len( data["Param1"] ):
			self.spaceEnable = [ int( i ) for i in data["Param1"].split( ";" ) ] 	#Buff的地图有效性
		
	def doBegin( self, receiver, buffData ):
		# 给状态
		actPet = receiver.pcg_getActPet()
		if actPet: actPet.entity.withdraw( csdefine.PET_WITHDRAW_GMWATCHER )
		receiver.effectStateInc( csdefine.EFFECT_STATE_WATCHER )
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
		receiver.base.chat_lockMyChannels( LOCAK_CHAT_CHANNELS, csdefine.CHAT_FORBID_GUANZHAN, 0 )
		receiver.setTemp( "watch_state", True )
		
	def doReload( self, receiver, buffData ):
		# 给状态
		actPet = receiver.pcg_getActPet()
		if actPet: actPet.entity.withdraw( csdefine.PET_WITHDRAW_GMWATCHER )
		receiver.effectStateInc( csdefine.EFFECT_STATE_WATCHER )
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
		receiver.setTemp( "watch_state", True )
		
	def doLoop( self, receiver, buffData ):
		if not self._checkCurrentSpace( receiver ):
			return False
		
		return Buff_Normal.doLoop( self, receiver, buffData )
		
	def doEnd( self, receiver, buffData ):
		# 取消状态
		receiver.effectStateDec( csdefine.EFFECT_STATE_WATCHER )
		receiver.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
		receiver.base.chat_unlockMyChannels( LOCAK_CHAT_CHANNELS, csdefine.CHAT_FORBID_GUANZHAN )
		receiver.setTemp( "watch_state", False )
		
	def _checkCurrentSpace( self, receiver ):
		# 检查地图有效性
		spaceType = int( receiver.getCurrentSpaceData( csconst.SPACE_SPACEDATA_SPACE_TYPE_KEY ) )
		if spaceType not in self.spaceEnable:
			return False
			
		return True