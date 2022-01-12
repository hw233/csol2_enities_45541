# -*- coding: gb18030 -*-


import BigWorld
import Math
import random
import math
import csstatus
import csconst

from Spell_Item import Spell_Item
from bwdebug import *

class Spell_Item_Tong_CallMember( Spell_Item ):
	"""
	召唤道具，将帮会成员传送过来
	"""
	def init( self, dict ):
		"""
		初始化
		"""
		Spell_Item.init( self, dict )
		self.limitLevel = int( dict["param1"] )				# 只有使用玩家等级正负x级的帮会成员才能收到提示
		self.showMessage = int( dict["param2"] )				# 提示框的内容1为运镖内容，2为帮会内容，3为...
		
		
	def useableCheck( self, caster, target ):
		"""
		校验技能是否能使用
		"""
		if caster.tong_dbID == 0:
			caster.statusMessage( csstatus.SKILL_ITEM_ADD_NOT_TONG_ATTRIBUTE )
			return False
		
		return Spell_Item.useableCheck( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		userDBID = receiver.databaseID
		tongOnlineMember = receiver.getTongOnlineMember()							# 获取帮会在线成员
		spaceName = receiver.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )	# 获取施法者所在的地图名
		if len( tongOnlineMember ) == 0:				# 假如帮会没有在线成员
			return
		lineNumber = receiver.getCurrentSpaceLineNumber()
		tong = receiver.tong_getTongEntity( receiver.tong_dbID )
		if tong:
			tong.infoCallMember( userDBID, lineNumber, spaceName, receiver.position, receiver.direction, self.limitLevel, self.showMessage )
	#	Spell_Item.receive( self, caster, receiver )
