# -*- coding:gb18030 -*-
import BigWorld
import csconst
import csdefine

from Buff_Normal import Buff_Normal
from bwdebug import *

# 挑战副本状态
STATE = csdefine.ACTION_FORBID_VEHICLE | csdefine.ACTION_FORBID_CALL_PET | csdefine.ACTION_FORBID_WIELD

class Buff_9003( Buff_Normal ):
	"""
	设置玩家使用恢复HP和MP物品(非buff效果恢复)时候的恢复放大比例
	格斗副本专用BUFF
	"""
	def __init__( self ):
		Buff_Normal.__init__( self )
		self.hpAmendPercent = 0.0
		self.mpAmendPercent = 0.0
		
	def init( self, data ):
		Buff_Normal.init( self, data )
		self.hpAmendPercent = int( data["Param1"] if len( data["Param1"] ) > 0 else 0 ) / 100.0
		self.mpAmendPercent = int( data["Param2"] if len( data["Param2"] ) > 0 else 0 ) / 100.0
		
	def doBegin( self, receiver, buffData ):
		# 给状态
		receiver.actCounterInc( STATE )
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.setTemp( "Item_cure_hp_amend_percent", self.hpAmendPercent )
		receiver.setTemp( "Item_cure_mp_amend_percent", self.mpAmendPercent )
		receiver.startMagicChangeChallenge()
		
	def doReload( self, receiver, buffData ):
		# 给状态
		receiver.actCounterInc( STATE )
		
		self.__checkCurrentSpace( receiver )
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.setTemp( "Item_cure_hp_amend_percent", self.hpAmendPercent )
		receiver.setTemp( "Item_cure_mp_amend_percent", self.mpAmendPercent )
		receiver.startMagicChangeChallenge()
		
	def doLoop( self, receiver, buffData ):
		if not self.__checkCurrentSpace( receiver ):
			receiver.challengeSpaceOnLeaveSpecial()
			return False
		
		return Buff_Normal.doLoop( self, receiver, buffData )
		
	def doEnd( self, receiver, buffData ):
		# 取消状态
		receiver.actCounterDec( STATE )
		
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeTemp( "Item_cure_hp_amend_percent" )
		receiver.removeTemp( "Item_cure_mp_amend_percent" )
		receiver.stopMagicChangeChallenge()
		
	def __checkCurrentSpace( self, receiver ):
		# 检查是否还在挑战副本内
		spaceName = BigWorld.getSpaceDataFirstForKey( receiver.spaceID, csconst.SPACE_SPACEDATA_KEY )
		# 格斗副本的className都是fu_ben_ge_dou开始
		if "fu_ben_hua_shan" not in spaceName:
			return False
			
		return True