# -*- coding: gb18030 -*-
#

import csdefine
import csconst
import GUIFacade
import BigWorld
import csstatus
import Const
from guis import *
from LabelGather import labelGather
from AbstractTemplates import Singleton
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.controls.StaticText import StaticText
from guis.controls.ProgressBar import HProgressBar as ProgressBar
from BuffItem import BuffItem

NAME_LIMIT_SHOW_LEN = 16 # NPC名称显示长度限制
YXLM_BUFF_SOURCE_TYPES = (
	csdefine.BUFF_ORIGIN_YXLM_COEXISTENT,
	csdefine.BUFF_ORIGIN_YXLM,
	)

class LolTargetInfo( Singleton, RootGUI ):

	def __init__( self ):
		Singleton.__init__( self )
		wnd = GUI.load( "guis/general/targetinfo/lolcopy/bg.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.escHide_			= False				# 按 esc 键不会隐藏
		self.h_dockStyle = "LEFT"
		self.v_dockStyle = "TOP"
		self.addToMgr( "lolTargetInfo")

		self.posZSegment = ZSegs.L5
		self.activable_ = False
		self.moveFocus		 = False
		self.__target = None
		self.__pyBuffItems = []						# 保存所有 buff 格子
		self.__pyDuffItems = []						# 保存所有 debuff 格子
		self.__pySItems = []						# 目标的特殊buff——英雄联盟副本Boss的buff
		self.__reBuffsCBID = 0
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()

	def __initialize( self, wnd ) :
		self.__pyHead = PyGUI( wnd.head )

		self.__pyLbName = StaticText( wnd.lbName )
		self.__pyLbLevel = StaticText( wnd.lbLevel )
		self.__pyHPBar = ProgressBar( wnd.hpBar )
		self.__pyHPBar.clipMode = "RIGHT"

		self.__pyLevelBg = PyGUI( wnd.levelBg)
		self.__pyLevelBg.visible = True

		self.__pyLbHP = StaticText( wnd.lbHP )
		self.__pyLbHP.fontSize = 12
		self.__pyLbHP.text = ""
		self.__pyLbHP.h_anchor = 'CENTER'

		self.__pyLbComef = StaticText( wnd.lbComef )
		self.__pyLbComef.text = ""

		tempPySBuffs = []
		for name, item in wnd.children:
			if name.startswith( "sItem_"):
				index = int( name.split( "_")[1] )
				pySItem = BuffItem( item.item )
				tempPySBuffs.append( (index, pySItem) )
		tempPySBuffs.sort( key = lambda i : i[0] )
		self.__pySItems = [i[1] for i in tempPySBuffs]

		labelGather.setLabel( wnd.combText, "TargetInfo:main", "miComef" )

	def dispose( self ) :
		self.__deregisterTriggers()
		RootGUI.dispose( self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ENTITY_HP_CHANGED"]		= self.__onHPChanged
		self.__triggers["EVT_ON_ENTITY_HP_MAX_CHANGED"]	= self.__onHPChanged
		self.__triggers["EVT_ON_TARGET_BUFFS_CHANGED"]	= self.__setBuffItems
		self.__triggers["EVT_ON_TARGET_MODEL_CHANGED"] = self.__onTargetModelChanged
		self.__triggers["EVT_ON_TARGET_POWER_CHANGED"] = self.__onTargetPowerChanged
		for eventMacro in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		for eventMacro in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( eventMacro, self )

	def onShowTargetInfo( self, target ):
		RootGUI.hide( self )
		self.__target = target
		if target.getEntityType() in Const.DIRECT_TALK:	# 采集点不显示目标信息 by 姜毅
			return
		title = target.getTitle()
		name = target.getName()
		if name == "":
			return
		if target.isEntityType( csdefine.ENTITY_TYPE_MONSTER ) or \
		target.isEntityType( csdefine.ENTITY_TYPE_NPC ):
			if len( name ) > NAME_LIMIT_SHOW_LEN:
				name = "%s..."%name[:12]
		if hasattr( target, "level" ):
			level = target.getLevel()
			self.__onLevelChanged( target, 1, level )							# 重新设置等级
		self.__pyLbName.text = name							# 重新设置目标名字
		self.__setTargetFont()
		self.__onHPChanged( target, target.HP, target.HP_Max, target.HP )
		self.__pyHead.texture = target.getHeadTexture()		# 重新设置头像
		self.__setBuffItems()								# 重新设定BUFF
		self.__updateTargetPower( target.averageDamage() )
		self.show()

	def onHideTrargetInfo( self, target ) :
		"""
		隐藏目标
		"""
		self.hide()

	# ---------------------------------------
	def __onHPChanged( self, entity, hp, hpMax, oldValue ) :
		"""
		目标 HP 改变的时候被调用
		"""
		if entity != self.__target : return
		if hpMax > 0 :
			self.__pyHPBar.value = float( hp ) / hpMax
		else :
			self.__pyHPBar.value = 0
		if hp == 1 and hpMax == 1:
			self.__pyLbHP.text = ""
		else:
			self.__pyLbHP.text = "%d/%d" % ( hp, hpMax )

	def __onTargetModelChanged( self, entity, oldModel, newModel ):
		"""
		是否隐藏信息
		"""
		if entity != self.__target:return
		headTexture = entity.getHeadTexture()
		if entity.hasFlag( csdefine.ROLE_FLAG_HIDE_INFO ): #隐藏信息状态
			modelNumber = entity.currentModelNumber
			headTexture = g_npcmodel.getHeadTexture( modelNumber )
			self.__onLevelChanged( entity, 1, 0 )
			self.__onHPChanged( entity, 1, 1, 1 )
			self.__onMPChanged( entity, 1, 1 )
			self.__pyLbName.text = ""
			self.__pyClassMark.visible = False
		self.__pyHead.texture = headTexture

	def __onTargetPowerChanged( self, entityID, power ) :
		"""
		目标的战斗力发生改变
		"""
		if self.__target is None:return
		if entityID == self.__target.id :
			self.__updateTargetPower( power )

	def __onNameChanged( self, entityID, nameText ):
		"""
		名字改变
		"""
		if self.__target and self.__target.id == entityID:
			self.__pyLbName.text = nameText

	def __setBuffItems( self ):
		"""
		刷新所有BUFF
		"""
		self.__clearAllBuffs()
 		self.__showTargetBuffs()

	def __showTargetBuffs( self ):
		"""
		将目标身上的所有buff和debuff都显示出来
		"""
		buffInfos = []
		duffInfos = []
		yxlmBuffs = []
		if self.__target:
			for buffItem in self.__target.attrBuffItems:
				if self.__target.getSourceTypeByBuffIndex(buffItem.buffIndex) in YXLM_BUFF_SOURCE_TYPES:
					yxlmBuffs.append( buffItem )
				elif buffItem.baseItem.isMalignant():
					duffInfos.append( buffItem )
				else:
					buffInfos.append( buffItem )
		self.__updateSBuffs( yxlmBuffs )
		self.__updateBuffItems( duffInfos, self.__pyDuffItems )
		self.__updateBuffItems( buffInfos, self.__pyBuffItems )
		self.__layoutBuffs()

	def __cancelUpdateCallback( self ):
		"""
		取消buff自动更新
		"""
		if self.__reBuffsCBID != 0:
			BigWorld.cancelCallback( self.__reBuffsCBID )
			self.__reBuffsCBID = 0

	def __updateBuffItems( self, buffItems, pyBuffItems ):
		"""
		更新buff信息到界面上
		"""
		# 如果已经有BUFF显示在上面了，更新一下就行了
		for index, itemInfo in enumerate( buffItems ):
			if index < len( pyBuffItems ):
				pyBuffItems[ index ].update( itemInfo )
			else:
				self.__onAddBuff( itemInfo, pyBuffItems )

		# 清除多余的BUFF图标
		n = len( pyBuffItems ) - len( buffItems )
		while n > 0:
			pyBuffItems.pop(-1).dispose()
			n = n - 1

	def __clearAllBuffs( self ):
		"""
		删除所有BUFF / DeBuff
		"""
		self.__cancelUpdateCallback()
		self.__updateSBuffs([])
		for pyItem in self.__pyBuffItems :
			pyItem.dispose()
		for pyItem in self.__pyDuffItems :
			pyItem.dispose()
		self.__pyBuffItems = []
		self.__pyDuffItems = []

	def __onAddBuff( self, itemInfo, pyBuffItems ):
		"""
		增加一个BUFF / DeBuff
		"""
		item = GUI.load( "guis/general/targetinfo/common/buffItem.gui" )
		uiFixer.firstLoadFix( item )
		pyItem = BuffItem( item )
		self.addPyChild( pyItem )
		pyItem.update( itemInfo )
		pyBuffItems.append( pyItem )

	def __setTargetFont( self ):										# 重新设置字体颜色
		"""
		设置标签的字体颜色
		"""
		# 根据等级的差别，显示不同的字体颜色
		if not hasattr ( self.__target, "getLevel"):
			return
		dlevel = BigWorld.player().getLevel() - self.__target.getLevel()
		if dlevel <= -5 :
			self.__pyLbLevel.colour = 255, 0, 0, 255
		elif dlevel <= 4 :
			self.__pyLbLevel.colour = 255, 255, 255, 255
		elif dlevel  <= 25 :
			self.__pyLbLevel.colour = 0, 255, 0, 255
		else :
			self.__pyLbLevel.colour = 127, 127, 127, 255

	def __onLevelChanged( self, entity, oldLevel, level ):
		"""
		目标等级改变的时候被调用
		"""
		if entity != self.__target : return
		self.__setTargetFont()
		if level == "" or level == 0:
			self.__pyLevelBg.visible = False
			self.__pyLbLevel.text = ""
		else:
			self.__pyLevelBg.visible = True
			self.__pyLbLevel.text = str( level )

	def __layoutBuffs( self ) :
		"""
		排列所有 Buff / DeBuff 的位置
		"""
		left = scale_util.getGuiLeft( self.gui.sItem_0 )
		top = scale_util.getGuiBottom( self.gui.sItem_0 ) + 2
		for idx, pyItem in enumerate( self.__pyBuffItems ):
			pyItem.left = left + idx * ( pyItem.width + 2 )
			pyItem.top = top

		for idx, pyItem in enumerate( self.__pyDuffItems ):
			pyItem.left = left + idx * ( pyItem.width + 2 )
			pyItem.top = top + pyItem.height + 5

	def __updateTargetPower( self, power ):
		"""
		更新目标的战斗力值
		"""
		self.__pyLbComef.text = str( power )

	# ---------------------------------------------------------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.__target = None
		self.hide()

	def show( self ) :
		if self.__target is not None :
			RootGUI.show( self )

	def hide( self ) :
		#rds.targetMgr.unbindTarget( self.__target )
		self.__clearAllBuffs()
		self.__target = None
		RootGUI.hide( self )

	def __getPyBuffItemByIndex( self, buffIndex, pyBuffItems ):
		"""
		获取空的特殊buff格子
		"""
		for pyItem in pyBuffItems:
			if pyItem.itemInfo.buffIndex == buffIndex:
				return pyItem
		return None

	def __updateSBuffs( self, buffInfos ):
		"""
		更新特殊的buff
		"""
		buffAmount = len( buffInfos )
		for idx, pySItem in enumerate( self.__pySItems ):
			if idx < buffAmount:
				pySItem.update( buffInfos[idx] )
			else :
				pySItem.update( None )
