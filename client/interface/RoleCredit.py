# -*- coding: gb18030 -*-
#
# $Id: RoleCredit.py,v 1.5 2008-08-30 10:08:47 wangshufeng Exp $


import BigWorld
from bwdebug import *
import event.EventCenter as ECenter
from FactionMgr import factionMgr
import csdefine
import csconst
import csstatus
import Language
import Math
import config.client.labels.RoleCredit as lbDatas
from config.Title import Datas as g_TitleData
from Color import cscolors

prestigeStrDict = { csdefine.PRESTIGE_ENEMY : lbDatas.PRESTIGE_ENEMY,
					csdefine.PRESTIGE_STRANGE:lbDatas.PRESTIGE_STRANGE,
					csdefine.PRESTIGE_NEUTRAL:lbDatas.PRESTIGE_NEUTRAL,
					csdefine.PRESTIGE_FRIENDLY:lbDatas.PRESTIGE_FRIENDLY,
					csdefine.PRESTIGE_RESPECT:lbDatas.PRESTIGE_RESPECT,
					csdefine.PRESTIGE_ADMIRE:lbDatas.PRESTIGE_ADMIRE,
					csdefine.PRESTIGE_ADORE:lbDatas.PRESTIGE_ADORE,
					}

class RoleCredit:
	"""
	角色的声望、称号、荣誉interface
	"""
	def __init__( self ):
		"""
		"""
		self.prestige = {}		# 声望数据

	def prestigeUpdate( self, factionID, value ):
		"""
		Define method.
		声望改变，提供给server的通知函数

		@param factionID : 势力factionID
		@type factionID : UINT8
		@param value : 增加或减少的声望值
		@type value : INT32
		"""
		if not self.prestige.has_key( factionID ):
			ERROR_MSG( "Key error on faction ID:%s, maybe not initiated yet." % factionID )
			return
		oldLevel = self.getPretigeLevel( factionID )
		self.prestige[ factionID ] += value
		if self.prestige[ factionID ] > csconst.PRESTIGE_UPLIMIT:
			self.prestige[ factionID ] = csconst.PRESTIGE_UPLIMIT
		if self.prestige[ factionID ] < csconst.PRESTIGE_LOWERLIMIT:
			self.prestige[ factionID ] = csconst.PRESTIGE_LOWERLIMIT
		newLevel = self.getPretigeLevel( factionID )
		if value != 0:
			if value >= 1:
				self.statusMessage( csstatus.PRESTIGE_VALUE_INCREASE, factionMgr.getName( factionID ), value )
			else:
				self.statusMessage( csstatus.PRESTIGE_VALUE_REDUCE, factionMgr.getName( factionID ), abs( value ) )
		powerName = factionMgr.getName( factionID )
		if newLevel != oldLevel:
			self.statusMessage( csstatus.PRESTIGE_VALUE_UPDATE, powerName, prestigeStrDict[newLevel] )
		ECenter.fireEvent( "EVT_ON_ROLE_PRESTIGE_UPDATE", factionID ) # 声望更新


	def receivePrestige( self, factionID, value ):
		"""
		Define method.
		玩家登录，接收声望数据的函数

		@param factionID : 势力factionID
		@type factionID : UINT8
		@param value : 声望值
		@type value : INT32
		"""
		self.prestige[ factionID ] = value
		ECenter.fireEvent( "EVT_ON_ROLE_PRESTIGE_UPDATE", factionID ) # 声望更新


	def turnOnPrestige( self, factionID, value ):
		"""
		Define method.
		首次增加声望，声望开启
		@param factionID : 势力factionID
		@type factionID : UINT8
		@param value : 增加的声望值
		@type value : INT32
		"""
		self.prestige[ factionID ] = value
		if value != 0:
			if value >= 1:
				self.statusMessage( csstatus.PRESTIGE_VALUE_INCREASE, factionMgr.getName( factionID ), value )
			else:
				self.statusMessage( csstatus.PRESTIGE_VALUE_REDUCE, factionMgr.getName( factionID ), abs( value ) )
		ECenter.fireEvent( "EVT_ON_ROLE_PRESTIGE_ADD", factionID ) #开启某个声望

	def getPrestige( self, factionID ):
		"""
		获得对应factionID的势力声望

		@param factionID : 势力factionID
		@type factionID : UINT32
		"""
		try:
			return self.prestige[ factionID ]
		except KeyError:
			ERROR_MSG( "Key error on faction ID %s:" % factionID )
			return None

	def getPretigeLevel( self, factionID ):
		"""
		获得对应factionID的势力声望等级

		PRESTIGE_ENEMY				=			1	# 仇敌
		PRESTIGE_STRANGE			=			2	# 冷淡
		PRESTIGE_NEUTRAL			=			3	# 中立
		PRESTIGE_FRIENDLY			=			4	# 友善
		PRESTIGE_RESPECT			=			5	# 尊重
		PRESTIGE_ADMIRE				=			6	# 崇敬
		PRESTIGE_ADORE				=			7	# 崇拜
		"""
		return self.getPrestige( factionID ) < -3000 and csdefine.PRESTIGE_ENEMY \
			or self.getPrestige( factionID ) < 0     and csdefine.PRESTIGE_STRANGE \
			or self.getPrestige( factionID ) < 3000  and csdefine.PRESTIGE_NEUTRAL \
			or self.getPrestige( factionID ) < 9000  and csdefine.PRESTIGE_FRIENDLY \
			or self.getPrestige( factionID ) < 21000 and csdefine.PRESTIGE_RESPECT \
			or self.getPrestige( factionID ) < 42000 and csdefine.PRESTIGE_ADMIRE \
			or csdefine.PRESTIGE_ADORE

	def getPretigeDes( self, value ):
		"""
		获得对应factionID的势力声望等级

		PRESTIGE_ENEMY				=			1	# 仇敌
		PRESTIGE_STRANGE			=			2	# 冷淡
		PRESTIGE_NEUTRAL			=			3	# 中立
		PRESTIGE_FRIENDLY			=			4	# 友善
		PRESTIGE_RESPECT			=			5	# 尊重
		PRESTIGE_ADMIRE				=			6	# 崇敬
		PRESTIGE_ADORE				=			7	# 崇拜
		"""
		return value < -3000 and prestigeStrDict[ csdefine.PRESTIGE_ENEMY ] \
			or value < 0     and prestigeStrDict[ csdefine.PRESTIGE_STRANGE ] \
			or value < 3000  and prestigeStrDict[ csdefine.PRESTIGE_NEUTRAL ] \
			or value < 9000  and prestigeStrDict[ csdefine.PRESTIGE_FRIENDLY ]\
			or value < 21000 and prestigeStrDict[ csdefine.PRESTIGE_RESPECT ]\
			or value < 42000 and prestigeStrDict[ csdefine.PRESTIGE_ADMIRE ]\
			or prestigeStrDict[ csdefine.PRESTIGE_ADORE ]

	def onTitleAdded( self, titleID ) :
		"""
		@type 		titleID : UINT8

		新加称号的通知
		"""
		titleName = self.getAddTitle( titleID )
		if titleID not in [ csdefine.TITLE_ALLY_ID, csdefine.TITLE_COUPLE_MALE_ID, csdefine.TITLE_COUPLE_FEMALE_ID, csdefine.TITLE_TEACH_PRENTICE_ID ]:
			self.statusMessage( csstatus.TITLE_ADDED, titleName )
		ECenter.fireEvent( "EVT_ON_ROLE_TITLE_ADD", titleID, titleName )

	def onTitleRemoved( self, titleID ):
		"""
		@type 		titleID : UINT8

		移除称号的通知
		"""
		title = self.getAddTitle( titleID )
		if titleID == csdefine.TITLE_COUPLE_MALE_ID or titleID == csdefine.TITLE_COUPLE_FEMALE_ID:
			titleName = lbDatas.TITLE_COUPLE
		elif titleID == csdefine.TITLE_TEACH_PRENTICE_ID:
			titleName = lbDatas.TITLE_PRENTICE
		elif titleID == csdefine.TITLE_ALLY_ID:
			titleName = lbDatas.TITLE_ALLY
		else:
			titleName = title
		self.statusMessage( csstatus.TITLE_LOSED, titleName )
		ECenter.fireEvent( "EVT_ON_ROLE_TITLE_REMOVE", titleID )

	def getAddTitle( self, titleID ):
		"""
		@type 		titleID: INT32
		"""
		try:
			return g_TitleData[ titleID ]["name"]
		except KeyError, err:
			DEBUG_MSG( "%s--%s", KeyError, err )
			return ""

	def getTitleColor( self, titleID ):
		"""
		@type		titleID: INT32
		"""
		try:
			color = g_TitleData[ titleID ][ "color" ]
			return  cscolors[ color ]
		except KeyError, err:
			DEBUG_MSG( "%s--%s", KeyError, err )
			return (51.0, 204.0, 240.0, 255.0)	#这是默认颜色值

	def updateTitlesDartRob( self, factionID ):
		"""
		Define method.
		更新客户端称号的显示
		"""
		if self.isRobbing( self ):
			# 如果是劫镖，每个称号后面都显示“拦路虎”，并且如果玩家选择“无”称号，则直接显示“拦路虎”
			pass
		elif self.isDarting( self ):
			# 如果运镖，则每个称号后面显示“兴隆号”或“昌平号”
			if factionID == 37:
				# 显示“兴隆号”
				pass
			else:
				# 显示“昌平号”
				pass

	def onPrestigeChange( self ):
		"""
		Define method
		声望改变在客户端的触发
		"""
		self.refurbishAroundQuestStatus()
#
# $Log: not supported by cvs2svn $
# Revision 1.4  2008/07/19 01:56:53  wangshufeng
# 添加称号系统
#
# Revision 1.3  2008/07/17 03:16:45  fangpengjun
# 将势力由25个增加到30个
#
# Revision 1.2  2008/07/16 10:16:27  fangpengjun
# 添加界面所需信息
#
# Revision 1.1  2008/07/14 04:13:49  wangshufeng
# add new interface：RoleCredit
#
#
