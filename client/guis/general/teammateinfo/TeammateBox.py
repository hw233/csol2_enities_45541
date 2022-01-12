# -*- coding: gb18030 -*-
#
# $Id: TeammateBox.py,v 1.21 2008-08-30 09:12:32 huangyongwei Exp $

"""
imlement item will breaked
"""

import csdefine
import csconst
import GUIFacade
from ChatFacade import chatFacade
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.controls.ProgressBar import HProgressBar as ProgressBar
from guis.controls.StaticText import StaticText
from guis.controls.Icon import Icon
from guis.controls.ContextMenu import ContextMenu
from guis.controls.ContextMenu import DefMenuItem
from TeamVoteWnd import TeamVoteWnd
from BuffItem import BuffItem
from EspialTarget import espial
from LabelGather import labelGather
from PetFormulas import formulas
import Const

TRADE_SWAP_ITEM = 1		# 物品交易
TRADE_SWAP_PET = 0		# 宠物交易

# ----------------------------------------------------------------
# 调整属性字体尺寸修饰器
# ----------------------------------------------------------------
from AbstractTemplates import MultiLngFuncDecorator

class deco_TeammateResetPyItems( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF ) :
		"""
		繁体版下重新调整部分属性字体的尺寸
		"""
		SELF._TeammateBox__pyLbHP.fontSize = 11
		SELF._TeammateBox__pyLbHP.charSpace = -1

		SELF._TeammateBox__pyLbMP.fontSize = 11
		SELF._TeammateBox__pyLbMP.charSpace = -1

		SELF._TeammateBox__pyLbLevel.fontSize = 11
		SELF._TeammateBox__pyLbLevel.charSpace = -1

class TeammateBox( PyGUI ):
	
	def __init__( self ):
		box = GUI.load( "guis/general/teammateinfo/teammatebox.gui" )
		uiFixer.firstLoadFix( box )
		PyGUI.__init__( self, box )
		self.__initialize( box )
		self.__teammateID = None
	
	def __initialize( self, box ):
		self.__pyRoleBox = RoleBox( box.roleBox, self )
		
		self.__pyPetBox = PetBox( box.petBox, self )
		self.__pyPetBox.visible = False

	def updateRoleHP( self, hp, hpMax ):
		"""
		更新角色血量
		"""
		self.__pyRoleBox.updateHP( hp, hpMax )
	
	def updateRoleMP( self, mp, mpMax ):
		"""
		更新角色魔法值
		"""
		self.__pyRoleBox.updateMP( mp, mpMax )
	
	def updateRoleHeader( self, header ):
		"""
		更新角色头像
		"""
		self.__pyRoleBox.updateHeader( header )
	
	def addRoleBuff( self, buffInfo ):
		"""
		角色添加buff
		"""
		self.__pyRoleBox.addBuff( buffInfo )
	
	def removeRoleBuff( self, buffInfo ):
		"""
		角色移除buff
		"""
		self.__pyRoleBox.removeBuff( buffInfo )
	
	def updateRoleBuff( self, index, itemInfo ):
		"""
		角色更新buff
		"""
		self.__pyRoleBox.updateBuff( index, itemInfo )
	
	def clearRoleBuff( self ):
		"""
		清空角色buff
		"""
		self.__pyRoleBox.clearBuff()
	
	def setRoleCaptain( self, isCaptain ):
		"""
		设置队长标记
		"""
		self.__pyRoleBox.isCaptain = isCaptain
	
	def setRoleClassMark( self, classMark ):
		"""
		设置职业标记
		"""
		self.__pyRoleBox.tclassMark = classMark
	
	def changeRoleLevel( self, level ):
		"""
		角色等级改变
		"""
		if level == 0:
			self.__pyRoleBox.tLevel = "???"
		else:
			self.__pyRoleBox.tLevel = level
	
	def changeRoleName( self, name ):
		"""
		角色名称改变
		"""
		self.__pyRoleBox.tname = name
	
	def onMemberLogOut( self ):
		"""
		队友下线
		"""
		if self.__pyPetBox.visible:
			self.__pyPetBox.visible = False
			self.__pyPetBox.petID = 0

	# -------------------------------------------------------------------
	def onAddMemberPet( self, petID, uname, name, modelNumber, species ):
		"""
		显示宠物信息面板
		"""
		if not self.__pyPetBox.visible:
			self.__pyPetBox.visible = not self.isLogOut
		petName = formulas.getDisplayName( species, uname, name )
		hierarchy = formulas.getHierarchy( species )
		nameColor = ( 255, 255, 255, 255 )
		if hierarchy == csdefine.PET_HIERARCHY_INFANCY2:
			modelNumber += Const.PET_ATTACH_MODELNUM
			nameColor = ( 254, 163, 8, 255 )
		elif hierarchy == csdefine.PET_HIERARCHY_INFANCY1:
			nameColor = ( 0, 0, 255, 255 )
		headTexture = rds.npcModel.getHeadTexture( modelNumber )
		self.changePetID( petID )
		self.updatePetHeader( headTexture )
#		self.changePetName( petName, nameColor )
		
	def onRecPetInfo( self, petInfos ):
		"""
		更新队友宠物信息
		"""
		modelNumber = petInfos[9]
		species = petInfos[-1]
		petID = petInfos[0]
		hierarchy = formulas.getHierarchy( species )
		petName = formulas.getDisplayName( species, petInfos[1], petInfos[2] )
		nameColor = ( 255, 255, 255, 255 )
		if BigWorld.entities.has_key( petID )and \
		hierarchy in [csdefine.PET_HIERARCHY_INFANCY1, csdefine.PET_HIERARCHY_INFANCY2]:
			petName = self.getNearHierarchy1Name( petInfos[1], petInfos[2] )
		if hierarchy == csdefine.PET_HIERARCHY_INFANCY2:
			modelNumber += Const.PET_ATTACH_MODELNUM
			nameColor = ( 254, 163, 8, 255 )
		elif hierarchy == csdefine.PET_HIERARCHY_INFANCY1:
			nameColor = ( 0, 0, 255, 255 )
		headTexture = rds.npcModel.getHeadTexture( modelNumber )
		self.changePetID( petID )
#		self.changePetLevel( petInfos[3] )
#		self.changePetName( petName, nameColor )
		self.updatePetHP( petInfos[4], petInfos[5] )
		self.updatePetMP( petInfos[6], petInfos[7] )
		self.updatePetHeader( headTexture )
	
	def getNearHierarchy1Name( self, uname, name ):
		"""
		获取附近一代宝宝名称
		"""
		if name != "":
			return name
		return uname
	
	def updatePetHP( self, hp, hpMax ):
		"""
		更新宠物血量
		"""
		self.__pyPetBox.updateHP( hp, hpMax )
	
	def updatePetMP( self, mp, mpMax ):
		"""
		更新宠物魔法值
		"""
		self.__pyPetBox.updateMP( mp, mpMax )

	def changePetID( self, petID ):
		"""
		宠物id改变
		"""
		self.__pyPetBox.petID = petID
	
	def updatePetHeader( self, header ):
		"""
		更新宠物头像
		"""
		self.__pyPetBox.updateHeader( header )
	
	def changePetLevel( self, level ):
		"""
		宠物等级改变
		"""
		if level == 0:
			self.__pyPetBox.tLevel = "???"
		else:
			self.__pyPetBox.tLevel = level
	
	def changePetName( self, name,nameColor ):
		"""
		宠物名称改变
		"""
		self.__pyPetBox.tname = name
		self.__pyPetBox.setNameColr( nameColor )
	
	def addPetBuff( self, buffInfo ):
		"""
		宠物添加buff
		"""
		self.__pyPetBox.addBuff( buffInfo )
	
	def removePetBuff( self, buffInfo ):
		"""
		宠物移除buff
		"""
		self.__pyPetBox.removeBuff( buffInfo )
	
	def updatePetBuff( self, index, itemInfo ):
		"""
		宠物更新buff
		"""
		return
		self.__pyPetBox.updateBuff( index, itemInfo )
	
	def clearPlayerBuff( self ):
		"""
		清空宠物buff
		"""
		self.__pyPetBox.clearBuff()
	
	def onWithdrawPet( self ):
		"""
		收回宠物
		"""
		self.__pyPetBox.visible = False
		self.__pyPetBox.petID = 0

	def getPetBox( self ):
		"""
		是否存在宠物头像
		"""
		return self.__pyPetBox.visible

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getTeammateID( self ) :
		return self.__pyRoleBox.teammateID

	def _setTeammateID( self, teammateID ) :
		
		self.__pyRoleBox.teammateID = teammateID

	def _getIsLogOut( self ):
		return self.__pyRoleBox.isRoleLogOut

	def _setIsLogOut( self, isLogOut ):
		self.__pyRoleBox.isRoleLogOut = isLogOut
		if self.__pyPetBox.petID > 0:
			self.__pyPetBox.visible = not isLogOut
	
	def _getRoleHeader( self ):
		return self.__pyRoleBox.pyHeader_
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	teammateID = property( _getTeammateID, _setTeammateID )
	isLogOut = property( _getIsLogOut, _setIsLogOut )
	roleHeader = property( _getRoleHeader )
	
# --------------------------------------------------------------------------
# 队友宠物头像
class PetBox( Control ):
	
	__cc_item_size = 12.0, 13.0
	
	def __init__( self, box, pyBinder = None ):
		Control.__init__( self, box, pyBinder )
		self.focus = True
		self.__initialize( box )
		self.pyBuffItems_ = []			# 良性buff格子
		self.pyDBuffItems_ = []		# 恶性buff格子
		self.petID = 0
		
		self.initBDItems_( self.pyBuffItems_, 0.0 )
		self.initBDItems_( self.pyDBuffItems_, self.__cc_item_size[1] )
	
	def __del__( self ) :
		if Debug.output_del_TeammateBox :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		Control.dispose( self )
		self.pyBuffItems_ = []
		self.pyDBuffItems_ = []
	
	def __initialize( self, box ):
		self.pyHeader_ = PyGUI( box.header )
		
		self.pyLbHP_ = StaticText( box.lbHP )
		self.pyLbHP_.fontSize = 11
		self.pyLbHP_.h_anchor = 'CENTER'
		self.pyLbMP_ = StaticText( box.lbMP )
		self.pyLbMP_.fontSize = 11
		self.pyLbMP_.h_anchor = 'CENTER'

		self.pyHPBar_ = ProgressBar( box.hpBar )

		self.pyMPBar_ = ProgressBar( box.mpBar )

		self.pyBuffPanel_ = PyGUI( box.buffPanel )
		
		self.pyCMenu_ = ContextMenu()
		self.pyCMenu_.addBinder( self )
		
		self.pyMenu = DefMenuItem()
		labelGather.setPyLabel( self.pyMenu, "teammateinfo:tmbox_MU", "miEspial" )
		self.pyMenu.handler = self.__espialPet

		self.pyCMenu_.onBeforePopup.bind( self.__onMenuPopUp )
		self.pyCMenu_.onAfterPopUp.bind( self.__onAfterMenuPopUp )
		self.pyCMenu_.onItemClick.bind( self.__onMenuItemClick )
	
	def updateHP( self, hp, hpMax ):
		rate = 0
		self.pyBinder.isLogOut = False #去除队友的离线蒙皮
		if hpMax == "???" or hpMax == 0: #队友离线后将其HP都设为问号
			rate = 1
			self.pyLbHP_.text = "???/???"
			self.pyBinder.isLogOut = True #给队友面板加上离线蒙皮，在这里加的原因是队友在角色上线前离线的话原来的代码就无法加上离线蒙皮
		else:
			rate = float( hp  ) / hpMax
			self.pyLbHP_.text = "%d/%d" % ( hp, hpMax )
		self.pyHPBar_.value = rate
		self.pyHPBar_.visible = True
	
	def updateMP( self, mp, mpMax ):
		rate = 0
		if mpMax == "???" or mpMax == 0: #队友离线后将其MP设为问号
			rate = 1
			self.pyLbMP_.text = "???/???"
		else:
			rate = float( mp  ) / mpMax
			self.pyLbMP_.text = "%d/%d"%( mp, mpMax )
		self.pyMPBar_.value = rate
		self.pyMPBar_.visible = True
	
	def updateHeader( self, header ):
		self.pyHeader_.texture = header
	
	def onLClick_( self, mods ):
		"""
		点击头像，选取宠物
		"""
		Control.onLClick_( self, mods )
		try:
			entity = BigWorld.entities[self.petID]
		except:
			return
		rds.targetMgr.bindTarget( entity )
	
	def addBuff( self, itemInfo ) :
		"""
		当添加了一个 buff 时被触发
		"""
		skillID = itemInfo.baseItem.getSourceSkillID()
		if itemInfo.baseItem.isMalignant(): #恶性buff
			for pyItem in self.pyDBuffItems_:
				if pyItem.itemInfo and pyItem.itemInfo.baseItem.getSourceSkillID() == skillID:
					pyItem.update( itemInfo )
					return
		else: #良性buff
			for pyItem in self.pyBuffItems_:
				if pyItem.itemInfo and pyItem.itemInfo.baseItem.getSourceSkillID() == skillID:
					pyItem.update( itemInfo )
					return
		baseItem = itemInfo.baseItem
		if baseItem.isMalignant():# 恶性buff
			pyItem = self.getEmptyItem_( self.pyDBuffItems_ )
			pyItem.update( itemInfo )
		else: #良性buff
			pyItem = self.getEmptyItem_( self.pyBuffItems_ )
			pyItem.update( itemInfo )
	
	def removeBuff( self, buffInfo ) :
		"""
		当删除了一个 buff 时被触发
		"""
		pyItems = []
		top = 0
		if buffInfo.baseItem.isMalignant():
			pyItems = self.pyDBuffItems_
			top = self.__cc_item_size[1]
		else:
			pyItems = self.pyBuffItems_
			top = 0.0
		pyItem = self.findItem_( pyItems, buffInfo )
		if pyItem is None :
			self.layoutItems_( pyItems, top )
			return
		pyItem.update( None )
		if pyItem in self.pyDBuffItems_:
			self.pyDBuffItems_.remove( pyItem )
			self.pyDBuffItems_.append( pyItem )
		else:
			self.pyBuffItems_.remove( pyItem )
			self.pyBuffItems_.append( pyItem )
		self.layoutItems_( pyItems, top )
	
	def updateBuff( self, index, itemInfo ) :
		"""
		当有一个 buff 更新时被触发
		"""
		pyItems = []
		baseItem = itemInfo.baseItem
		if itemInfo.baseItem.isMalignant():
			pyItems = self.pyDBuffItems_
		else:
			pyItems = self.pyBuffItems_
		for pyItem in pyItems :
			if pyItem is None or pyItem.itemInfo is None: continue
			if pyItem.itemInfo.baseItem.getSourceSkillID() == baseItem.getSourceSkillID() :
				pyItem.update( buffInfo )
	
	def clearBuff( self ) :
		for pyItem in self.pyDBuffItems_ + self.pyBuffItems_ :
			pyItem.update( None )
			
	def setNameColr( self, nameColor ):
		"""
		宠物名称颜色，用以区分代数
		"""
		self.pyLbName_.color = nameColor
		
	def findItem_( self, pyItems, info ) :
		"""
		find item which it's buff/duff infrmation is argument info
		"""
		for pyItem in pyItems :
			if pyItem.itemInfo is None: continue
			if pyItem.itemInfo.baseItem.getSourceSkillID() == info.baseItem.getSourceSkillID() :
				return pyItem
		return None
	
	def layoutItems_( self, pyItems, top ) :
		"""
		relayout all buff/duff items
		"""
		for index, pyItem in enumerate( pyItems ) :
			pyItem.index = index
			rowIndex = index/5			# 行索引
			colIndex = index%5			# 列索引
			pyItem.top = top + pyItem.height*rowIndex
			pyItem.left = colIndex*pyItem.width + 1.0 * colIndex
	
	def getEmptyItem__( self, pyItems ) :
		"""
		find out an item with no buff/duff information
		"""
		for pyItem in pyItems :
			if pyItem.itemInfo is None :
				return pyItem
		if pyItems == []:return
		pyItems.append( pyItems.pop( 0 ) )
		self.layoutItems_( pyItems, pyItems[0].top )
		return pyItems[-1]
	
	def initBDItems_( self, pyItems, top ) :
		"""
		initialize all buff/duff items
		"""
		for index in xrange( 5 ) :
			pyItem = BuffItem()
			self.pyBuffPanel_.addPyChild( pyItem )
			rowIndex = index/5			# 行索引
			colIndex = index%5			# 列索引
			pyItem.top = top + pyItem.height*rowIndex
			pyItem.left = colIndex*pyItem.width + 1.0 * colIndex
			pyItems.append( pyItem )
	
	def getEmptyItem_( self, pyItems ) :
		"""
		find out an item with no buff/duff information
		"""
		for pyItem in pyItems :
			if pyItem.itemInfo is None :
				return pyItem
		if pyItems == []:return
		pyItems.append( pyItems.pop( 0 ) )
		self.layoutItems_( pyItems, pyItems[0].top )
		return pyItems[-1]

	def __onMenuPopUp( self ) :
		"""
		菜单弹出前被调用
		"""
		self.pyCMenu_.clear()
		self.pyCMenu_.pyItems.adds( [self.pyMenu] )
		return True
		
	def __onAfterMenuPopUp( self ) :
		"""
		菜单弹出后调用
		"""
		self.__updateMenu()
	
	def __updateMenu( self ):
		"""
		刷新队友宠物状态
		"""
		if not self.pyCMenu_.visible : return
		tnear = False
		distance = -1
		if BigWorld.entities.has_key( self.petID ):
			pet = BigWorld.entities[self.petID]
			distance = BigWorld.player().position.flatDistTo( pet.position )
			tnear = True
		self.pyMenu.enable = tnear and 0 <= distance <= 10.0
		BigWorld.callback( 0.5, self.__updateMenu )
	
	def __onMenuItemClick( self, pyItem ):
		"""
		当菜单选项被点击时被调用
		"""
		pyItem.handler()
	
	def __espialPet( self ):
		"""
		观察队友宠物
		"""
		if BigWorld.entities.has_key( self.petID ) :
			pet = BigWorld.entities[ self.petID ]
			if rds.targetMgr.isPetTarget( pet ):
				pet.requeryPetDatas()
		
# ----------------------------------------------------------------
class RoleBox( PetBox ) :
	__cc_pro_states = {}									# 不同职业的状态标记 mapping 位
	__cc_pro_states[csdefine.CLASS_FIGHTER]	 = ( 1, 1 )		# 战士
	__cc_pro_states[csdefine.CLASS_SWORDMAN] = ( 1, 2 )		# 剑客
	__cc_pro_states[csdefine.CLASS_ARCHER]	 = ( 2, 1 )		# 射手
	__cc_pro_states[csdefine.CLASS_MAGE]	 = ( 2, 2 )		# 法师

	__cg_pyBuffItems						 = []			# buff item 对象池
	__cc_item_size = 12.0, 25.0

	def __init__( self, box, pyBinder = None ) :
		PetBox.__init__( self, box, pyBinder )
		self.__tclassMark = -1
		self.teammateID = 0

		self.pyLbName_ = StaticText( box.lbName )
		self.pyLbName_.fontSize = 11
		self.pyLbName_.h_anchor = 'CENTER'
		self.pyLbLevel_ = StaticText( box.lbLevel )			# 队友等级
		self.pyLbLevel_.fontSize = 11
		self.pyLbLevel_.h_anchor = 'CENTER'
		self.pyCMenu_.onBeforePopup.bind( self.__onMenuPopUp )
		self.pyCMenu_.onAfterPopUp.bind( self.__onAfterMenuPopUp )
		self.pyCMenu_.onItemClick.bind( self.__onMenuItemClick )

		self.__menuItems = {}			# 分组存放所有的菜单项，不再每次显示时都重新创建
		self.__createMenuItems()
		self.__initialize( box )
		self.__resetPyItems()

	def __del__( self ) :
		if Debug.output_del_TeammateBox :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		PetBox.dispose( self )
		RoleBox.__cg_pyBuffItems += self.pyBuffItems_		# 回收 buff item

	# ---------------------------------------
	def __initialize( self, box ) :
		self.__pyMark = PyGUI( box.captainMark )
		self.__pyMark.visible = False
		
		self.__pyClassMark = Icon( box.classMark )				# 队友职业标记
		self.__pyClassMark.crossFocus = True
		self.__pyClassMark.onMouseEnter.bind( self.__onShowClass )
		self.__pyClassMark.onMouseLeave.bind( self.__onHideClass )
		self.__pyClassMark.visible = True

		self.initBDItems_( self.pyBuffItems_, 0.0 )
		self.initBDItems_( self.pyDBuffItems_, self.__cc_item_size[1] )

	def initBDItems_( self, pyItems, top ) :
		"""
		initialize all buff/duff items
		"""
		for index in xrange( 10 ) :
			pyItem = BuffItem()
			self.pyBuffPanel_.addPyChild( pyItem )
			rowIndex = index/5			# 行索引
			colIndex = index%5			# 列索引
			pyItem.top = top + pyItem.height*rowIndex
			pyItem.left = colIndex*pyItem.width + 1.0 * colIndex
			pyItems.append( pyItem )

	@deco_TeammateResetPyItems
	def __resetPyItems( self ) :
		"""
		重设部分UI元素的位置、大小、字体等属性
		"""
		pass											# 简体版本不作修改

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onMenuPopUp( self ) :
		"""
		菜单弹出前被调用
		"""
		self.pyCMenu_.clear()
		self.__constructMenu()
		return True

	# -------------------------------------------------
	def __createMenuItems( self ) :
		"""
		创建所有可能用到的菜单项
		"""
		menuList = []
		pyItem0 = DefMenuItem()
		labelGather.setPyLabel( pyItem0, "teammateinfo:tmbox_MU", "miWhisper" )
		pyItem0.handler = self.__whisper
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		menuList.extend( [pyItem0, pySplitter] )

		pyItem0 = DefMenuItem()
		labelGather.setPyLabel( pyItem0, "teammateinfo:tmbox_MU", "miEspial" )
		pyItem0.handler = self.__espialTarget
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		menuList.extend( [pyItem0, pySplitter] )

		pyItem0 = DefMenuItem()
		labelGather.setPyLabel( pyItem0, "teammateinfo:tmbox_MU", "miFollow" )
		pyItem0.handler = self.__followTarget
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		menuList.extend( [pyItem0, pySplitter] )

		pyItem0 = DefMenuItem()
		labelGather.setPyLabel( pyItem0, "teammateinfo:tmbox_MU", "miItemTrade" )
		pyItem0.handler = self.__inviteTradeItem
		
		pyItem1 = DefMenuItem()
		labelGather.setPyLabel( pyItem1, "teammateinfo:tmbox_MU", "miPetTrade" )
		pyItem1.handler = self.__inviteTradePet
		
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		menuList.extend( [pyItem0, pyItem1, pySplitter] )

		pyItem0 = DefMenuItem()
		labelGather.setPyLabel( pyItem0, "teammateinfo:tmbox_MU", "miAddFriend" )
		pyItem0.handler = self.__addToBuddy
		pyItem1 = DefMenuItem()
		labelGather.setPyLabel( pyItem1, "teammateinfo:tmbox_MU", "miAddBlacklist" )
		pyItem1.handler = self.__addToBlackList
		menuList.extend( [pyItem0, pyItem1] )
		self.__menuItems["persistence"] = menuList						# 创建第一组，这组菜单每次弹出都会显示

		pyItem0 = DefMenuItem()
		labelGather.setPyLabel( pyItem0, "teammateinfo:tmbox_MU", "miKickTeammate" )
		pyItem0.handler = self.__kickOutTeammate
		pyItem1 = DefMenuItem()
		labelGather.setPyLabel( pyItem1, "teammateinfo:tmbox_MU", "miSetCaptain" )
		pyItem1.handler = self.__changeCaptain
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )			# 第三组，队友操作
		self.__menuItems["teammate"] = [pySplitter, pyItem1, pyItem0]

		pyItem0 = DefMenuItem()
		labelGather.setPyLabel( pyItem0, "teammateinfo:tmbox_MU", "miInviteJoinTong" )
		pyItem0.handler = self.__InviteJoinTong
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		self.__menuItems["joinTong"] = [pySplitter, pyItem0]			# 第五组，邀请加入帮会
		
		pyItem0 = DefMenuItem()
		labelGather.setPyLabel( pyItem0, "teammateinfo:tmbox_MU", "kickingVote" )
		pyItem0.handler = self.__kickingVote
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		self.__menuItems["kickingVote"] = [pySplitter, pyItem0]			# 第五组，邀请加入帮会

	def __constructMenu( self ) :
		"""
		根据当前状态创建右键菜单
		"""
		player = BigWorld.player()
		self.pyCMenu_.clear()
		pyItems = self.__menuItems["persistence"]
		self.pyCMenu_.pyItems.adds( pyItems )
		if player.isCaptain() :
			pyItems = self.__menuItems["teammate"]
			self.pyCMenu_.pyItems.adds( pyItems )
		if player.isJoinTong() and player.tong_grade&csdefine.TONG_GRADE_CAN_SET_CONSCRIBE:
			pyItems = self.__menuItems["joinTong"]
			self.pyCMenu_.pyItems.adds( pyItems )
		if player.insideMatchedCopy:
			pyItems = self.__menuItems["kickingVote"]
			self.pyCMenu_.pyItems.adds( pyItems )

	def __onAfterMenuPopUp( self ) :
		"""
		菜单弹出后调用
		"""
		self.__updateMenu()

	def __updateMenu( self ) :
		"""
		根据玩家的状态更新菜单项的有效性
		"""
		if not self.pyCMenu_.visible : return
		tnear = False
		distance = -1
		if BigWorld.entities.has_key( self.teammateID ) :
			teammate = BigWorld.entities[ self.teammateID ]
			player = BigWorld.player()
			distance = player.position.flatDistTo( teammate.position )
			samePlanes = player.isSamePlanes( teammate )
			tnear = True
		self.__menuItems["persistence"][0].enable = not self.isRoleLogOut									# “发送私聊消息”选项
		self.__menuItems["persistence"][2].enable = tnear and samePlanes and 0 <= distance <= 10.0								# “观察”选项
		self.__menuItems["persistence"][4].enable = tnear and samePlanes and 0 <= distance <= 20.0								# “跟随”选项
		self.__menuItems["persistence"][6].enable = tnear and samePlanes and 0 <= distance <= csconst.COMMUNICATE_DISTANCE		# “请求物品交易”选项
		self.__menuItems["persistence"][7].enable = tnear and samePlanes and 0 <= distance <= csconst.COMMUNICATE_DISTANCE		# “请求宠物交易”选项
		#self.__menuItems["teammate"][0].enable = tnear and 0<= distance <= 15									# “邀请跟随”选项
		self.__menuItems["teammate"][1].enable = not self.isRoleLogOut												# “设置为队长”选项
		BigWorld.callback( 0.1, self.__updateMenu )

	# ----------------------------------------------------------------
	# menuitem handlers
	# ----------------------------------------------------------------
	def __whisper( self, pyItem ) :
		"""
		与目标进行私聊
		"""
		if not self.isRoleLogOut :
			chatFacade.whisperWithChatWindow( self.tname )

	def __espialTarget( self, pyItem ):
		"""
		请求观察对方的装备和属性
		"""
		if BigWorld.entities.has_key( self.teammateID ) :
			teammate = BigWorld.entities[ self.teammateID ]
			espial.onEspialTarget( teammate )

	def __followTarget( self, pyItem ):
		"""
		跟随目标移动
		"""
		if BigWorld.entities.has_key( self.teammateID ) :
			BigWorld.player().autoFollow( self.teammateID )

	def __inviteTradeItem( self, pyItem ) :
		"""
		请求物品交易
		"""
		if BigWorld.entities.has_key( self.teammateID ) :
			teammate = BigWorld.entities[ self.teammateID ]
			GUIFacade.inviteSwapItem( teammate, TRADE_SWAP_ITEM )

	def __inviteTradePet( self, pyItem ):
		"""
		请求宠物交易
		"""
		if BigWorld.entities.has_key( self.teammateID ) :
			teammate = BigWorld.entities[ self.teammateID ]
			GUIFacade.inviteSwapItem( teammate, TRADE_SWAP_PET )

	def __addToBuddy( self, pyItem ) :
		"""
		加为好友
		"""
		BigWorld.player().addFriend( self.tname )

	def __addToBlackList( self, pyItem ) :
		"""
		加到黑名单
		"""
		BigWorld.player().addBlacklist( self.tname )

	def __kickOutTeammate( self, pyItem ) :
		"""
		开除队友
		"""
		GUIFacade.kickoutTeam( self.teammateID )

	def __changeCaptain( self, pyItem ) :
		"""
		设置目标为队长
		"""
		BigWorld.player().changeCaptain( self.teammateID )

	def __InviteRide( self, pyItem ):
		"""
		邀请共骑
		"""
		player = BigWorld.player()
		player.cell.inviteRide( self.teammateID )

	def __inviteFollow( self, pyItem ) :
		"""
		要求那个跟随
		"""
		BigWorld.player().inviteFollow( self.teammateID )

	def __InviteJoinTong( self, pyItem ):
		"""
		邀请加入帮会
		"""
		player = BigWorld.player()
		player.tong_requestJoinByPlayerName( self.tname )
	
	def __kickingVote( self, pyItem ):
		"""
		踢人投票
		"""
		voteWnd = TeamVoteWnd.instance()
		voteWnd.show( self )
		
	# -------------------------------------------------
	@staticmethod
	def __getBuffItem() :
		"""
		获得一个 buff item
		"""
		if len( RoleBox.__cg_pyBuffItems ) :
			return RoleBox.__cg_pyBuffItems.pop()
		return BuffItem()

	# -------------------------------------------------
	def __onMenuItemClick( self, pyItem ) :
		"""
		当菜单选项被点击时被调用
		"""
		pyItem.handler( pyItem )

	def __onShowClass( self, pyMark ):
		"""
		显示职业信息
		"""
		classRace = self.__tclassMark
		if csconst.g_chs_class.has_key( classRace ):
			classText = csconst.g_chs_class[classRace]
			toolbox.infoTip.showToolTips( self, classText )

	def __onHideClass( self, pyMark ):
		"""
		隐藏职业信息
		"""
		toolbox.infoTip.hide()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def updateBuff( self, index, itemInfo ) :
		"""
		当有一个 buff 更新时被触发
		"""
		pyItems = []
		if itemInfo.baseItem.isMalignant():
			pyItems = self.pyDBuffItems_
		else:
			pyItems = self.pyBuffItems_
		for pyItem in pyItems :
			if pyItem is None or pyItem.itemInfo is None: continue
			if pyItem.itemInfo == buffInfo :
				pyItem.update( buffInfo )
	
	def updateHP( self, hp, hpMax ) :
		PetBox.updateHP( self, hp, hpMax )

	def updateMP( self, mp, mpMax ):
		PetBox.updateMP( self, mp, mpMax )

	def updateHeader( self, header ) :
		PetBox.updateHeader( self, header )

	def onLClick_( self, mods ):
		try:
			entity = BigWorld.entities[self.teammateID]
		except:
			return
		rds.targetMgr.bindTarget( entity )

	# -------------------------------------------------
	def _getTclassMark( self ):
		return self.__tclassMark

	def _setTclassMark( self, mark ):
		self.__tclassMark = mark
		if self.__cc_pro_states.has_key( mark ):
			self.__pyClassMark.visible = True
			texture = self.__cc_pro_states[mark]
			util.setGuiState( self.__pyClassMark.getGui(), ( 2, 2 ), texture )

	# -------------------------------------------------
	def _getIsCaptain( self ) :
		return self.__pyMark.pyMark.visible

	def _setIsCaptain( self, isCaptain ) :
		self.__pyMark.visible = isCaptain

	def _getIsRoleLogOut( self ):
		return self.getGui().hpBar.materialFX == "COLOUR_EFF"
	
	def _setIsRoleLogOut( self, isLogOut ):
		fx = { True : "COLOUR_EFF", False : "BLEND" }
		for n, ch in self.getGui().children :
			ch.materialFX = fx[bool( isLogOut )]
	# -------------------------------------------------
	def _getTName( self ) :
		return self.pyLbName_.text

	def _setTName( self, name ) :
		self.pyLbName_.text = name

	# -------------------------------------------------
	def _getTLevel( self ) :
		return self.pyLbLevel_.text

	def _setTLevel( self, level ) :
		self.pyLbLevel_.text = str( level ) # + "级"
	# -------------------------------------------------
	tclassMark = property( _getTclassMark, _setTclassMark )
	isCaptain = property( _getIsCaptain, _setIsCaptain )
	isRoleLogOut = property( _getIsRoleLogOut, _setIsRoleLogOut )
	tname = property( _getTName, _setTName )
	tLevel = property( _getTLevel, _setTLevel )