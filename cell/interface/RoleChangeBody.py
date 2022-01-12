# -*- coding: gb18030 -*-
#
# 玩家变身系统	2009-01-10 SongPeifang & LinQing
#

from bwdebug import *
import BigWorld
import csdefine
import csstatus
import Const
import csconst

class RoleChangeBody:
	"""
	玩家变身系统
	"""
	def __init__( self ):
		"""
		"""
		self.currentModelNumber = ""
		self.currentModelScale = 1.0

	def canChangeBody( self ):
		"""
		检查玩家是否允许变身
		"""
		if self.onFengQi: return False
		return True

	def begin_body_changing( self, modelNumber, modelScale ):
		"""
		Define method.
		玩家变身的接口
		"""
		if not self.canChangeBody():
			return
		# 设置变身模型编号
		self.currentModelNumber = modelNumber
		self.currentModelScale = modelScale
		if self.queryTemp( "BODY_CHANGE_NOT_CHANGE_STATE", False ):	# 有不改变状态标记
			return
		self.changeState( csdefine.ENTITY_STATE_CHANGING )	# 设置变身状态

	def enterCopyBeforeNirvanaBodyChanging( self ):
		self.retractVehicle( self.id )
		self.currentModelNumber = Const.JUQING_MODELNUM_MAPS.get( self.getGender() | self.getClass(), "" )
		self.currentModelScale = csconst.MATCHING_DICT[self.getGender()][self.getClass()]

	def enterCopyYeZhanFengQiBodyChanging( self ):
		"""
		Define method.
		夜战凤栖变身模型
		"""
		self.retractVehicle( self.id )	# 下骑宠
		if self.pcg_getActPet():		# 收回宠物
			self.pcg_withdrawPet( self.id )
		self.currentModelNumber = Const.YEZHAN_MODELNUM_MAPS.get( self.getGender() | self.getClass(), "" )
		self.currentModelScale = csconst.MATCHING_DICT[self.getGender()][self.getClass()]

	def getCurrentBodyNumber( self ):
		"""
		获得当前模型名
		"""
		return self.currentModelNumber

	def setCurrentBodyNumber( self, modelNumber ):
		"""
		设置当前模型名
		"""
		self.currentModelNumber = modelNumber

	def end_body_changing( self, srcEntityID, bodyNumer ):
		"""
		Define method.
		玩家取消变身的接口
		"""
		if srcEntityID != self.id:
			HACK_MSG( "非法调用者." )
			return
		if not self.canChangeBody():
			return
		if self.attrIntonateSkill:		# 如果是正在吟唱就要取消吟唱
			reason = csstatus.SKILL_PLAYER_STOP_BODY_CHANGING
			if self.currentModelNumber == "fishing":
				reason = csstatus.SKILL_PLAYER_STOP_FISHING
			self.interruptSpell( reason )
		if self.queryTemp( "SAME_TYPE_BUFF_REPLACE", False ) and self.queryTemp( "ROLE_BODY_BUFF_END", False ):  # 同类型buff替换
			return
		self.currentModelNumber = bodyNumer
		
		if self.getState() == csdefine.ENTITY_STATE_CHANGING and not self.queryTemp( "BODY_CHANGE_NOT_CHANGE_STATE", False ): # 没有不改变状态标记
			self.changeState( csdefine.ENTITY_STATE_FREE )

	def remove_bc_cards( self, cardIDList ):
		"""
		define method
		没收玩家身上的变身卡片
		"""
		for i in cardIDList:
			item = self.findItemFromNKCK_( int(i) )	# 判断是否已经有纸牌了
			if item != None:
				self.removeItem_( item.order, reason = csdefine.DELETE_ITEM_REMOVE_BC_CARDS )		# 移除掉玩家身上的纸牌