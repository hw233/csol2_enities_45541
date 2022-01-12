# -*- coding: gb18030 -*-
#
# $Id: PetBreed.py,v 1.4 2008-08-26 02:16:51 huangyongwei Exp $

"""
implement PetBreed Window
"""

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.controls.StaticLabel import StaticLabel
from guis.controls.ODComboBox import ODComboBox
from guis.controls.ComboBox import ComboItem
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from gbref import rds
import event.EventCenter as ECenter
import GUIFacade
import csdefine
import csconst
import csstatus
import utils
from PetFormulas import formulas
import GUIFacade

FOSTER_EXPENSE = 100000 #宠物繁殖收取费用

class PetFoster( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/petswindow/aboutnpc/petfoster.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.dstState = -1
		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )

		mutexGroups = [ MutexGroup.TRADE1, MutexGroup.PET1 ]
		rds.mutexShowMgr.addRootToMutexGroups( self, mutexGroups )		# 添加到多个互斥组

	def __initialize( self, wnd ):
		labelGather.setLabel( wnd.lbTitle, "PetsWindow:PetFoster", "lbTitle" )

		self.__pyStDstName = StaticText( wnd.dstPetPanel.bgTitle.stTitle ) 				#队友名字
		self.__pyStDstName.text = ""

		self.__pyStMyName = StaticText( wnd.myPetPanel.bgTitle.stTitle ) 					#自己名字
		self.__pyStMyName.text = ""

		self.__pyMyFosterPet = FosterPet( wnd.myPetPanel ) 				#自己宠物信息栏
		self.__pyMyFosterPet.initialize()
		self.__pyMyFosterPet.setPetCBReadAttr( True )

		self.__pyDstFosterPet = FosterPet( wnd.dstPetPanel )			#对方宠物信息栏
		self.__pyDstFosterPet.initialize()
		self.__pyDstFosterPet.setPetCBReadAttr( False )
		self.__pyDstFosterPet.setPetCBEnable( False )

		self.__pyExpPanel = CSRichText( wnd.rtExpPanel )					#繁殖说明
		self.__pyExpPanel.text = ""

		self.__pyRtExpense = CSRichText( wnd.rtExpense )					#所需花费
		self.__pyRtExpense.maxWidth = 200.0
		self.__pyRtExpense.text = ""

		self.__pyRtRemianTime = CSRichText( wnd.rtRemainTime )			#剩余时间
		self.__pyRtRemianTime.text = ""

		self.__pyBtnLock = HButtonEx( wnd.btnLock )						#锁定按钮
		self.__pyBtnLock.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnLock.enable = False
		self.__pyBtnLock.onLClick.bind( self.__onLock )
		labelGather.setPyBgLabel( self.__pyBtnLock, "PetsWindow:PetFoster", "btnLock" )

		self.__pyFosterBtn = HButtonEx( wnd.btnFoster )					#繁殖按钮
		self.__pyFosterBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyFosterBtn.enable = False
		self.__pyFosterBtn.onLClick.bind( self.__onBreed )
		labelGather.setPyBgLabel( self.__pyFosterBtn, "PetsWindow:PetFoster", "btnFoster" )
		
		labelGather.setLabel( wnd.myPetPanel.nameText, "PetsWindow:PetFoster", "nameText" )
		labelGather.setLabel( wnd.dstPetPanel.nameText, "PetsWindow:PetFoster", "nameText" )

	# -------------------------------------------------------------
	# pravite
	# -------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_PETFOSTER_PROCREATE_STATE"] 		= self.__onUpdateProcState
		self.__triggers["EVT_ON_PETFOSTER_DST_STATE_CHANGE"] 		= self.__onDstStateChange
		self.__triggers["EVT_ON_PETFOSTER_DST_PETEPITOME_CHANGE"] 	= self.__onDstPetChange
		self.__triggers["EVT_ON_PETFOSTER_REMAIN_TIME"]				= self.__onUpdateRemainTime
		self.__triggers["EVT_ON_PETFOSTER_MY_PET_CHANGE"] 			= self.__onMyPetChange
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	#------------------------------------------------------------
	def __onUpdateProcState( self, oldState, newState ):
		"""
		自身宠物繁殖状态改变通知
		"""
		self.__pyFosterBtn.enable = newState == csdefine.PET_PROCREATION_LOCK and \
			self.dstState in [csdefine.PET_PROCREATION_LOCK, csdefine.PET_PROCREATION_SURE]
		if newState == csdefine.PET_PROCREATION_DEFAULT: #初始状态
#			if not self.visible:return
			self.hide()
		elif newState == csdefine.PET_PROCREATION_WAITING: #进入等待状态
			pass
#			if BigWorld.player().isCaptain(): #自己是队长
#				self.__onOpenFosterWnd()
		elif newState == csdefine.PET_PROCREATION_SELECTING: #宠物选择状态
			if oldState in [csdefine.PET_PROCREATION_DEFAULT, csdefine.PET_PROCREATION_WAITING]:
				self.__onOpenFosterWnd()
			if BigWorld.player().isCaptain(): #队长
				self.__pyBtnLock.enable = oldState != csdefine.PET_PROCREATION_WAITING
			else:
				self.__pyBtnLock.enable = oldState != csdefine.PET_PROCREATION_DEFAULT
		elif newState == csdefine.PET_PROCREATION_LOCK: #锁定状态
			self.__pyBtnLock.enable = False
			self.__pyMyFosterPet.setPetCBEnable( False )
			self.__pyFosterBtn.enable = self.dstState == csdefine.PET_PROCREATION_LOCK
		elif newState == csdefine.PET_PROCREATION_SURE: #确认状态
			self.__pyFosterBtn.enable = False
			self.__pyMyFosterPet.setPetCBEnable( False )
		else: #确认后进入繁殖状态
			if BigWorld.player().isCaptain():
				expense = formulas.getProcreatePetCost()
				expenseText = utils.currencyToViewText( expense )
#				self.__pyRtExpense.text = PL_Font.getSource( "需要费用:%s"%expenseText, fc = ( 230, 227, 185, 255 ) )
		if newState in [csdefine.PET_PROCREATION_LOCK, csdefine.PET_PROCREATION_SURE]:
			self.__pyMyFosterPet.stateStr = labelGather.getText( "PetsWindow:PetFoster", "lockedStatus" )
		else:
			self.__pyMyFosterPet.stateStr = labelGather.getText( "PetsWindow:PetFoster", "unlockStatus" )

	def __onOpenFosterWnd( self ):
		"""
		玩家触发npc对话弹出界面，进入等待状态
		"""
		targeter=GUIFacade.getGossipTarget()
		if targeter is None:
			targeter=BigWorld.player()
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr(targeter , "getRoleAndNpcSpeakDistance" ):
			distance = targeter.getRoleAndNpcSpeakDistance()
		self.__trapID = BigWorld.addPot(targeter.matrix, csconst.COMMUNICATE_DISTANCE, self.__onEntitiesTrapThrough )#打开窗口后为玩家添加对话陷阱
		petEpitomes = self.__getProcreatePets()
		for epitome in petEpitomes:
			self.__pyMyFosterPet.addPetCBItem( epitome )
		self.__pyDstFosterPet.initialize()
		self.show()

	def __delTrap( self ):
		"""
		删除陷阱
		"""
		if self.__trapID is not None:
			BigWorld.delPot( self.__trapID )									#删除玩家的对话陷阱
			self.__trapID = None

	def __onEntitiesTrapThrough( self, isEnter,handle ):
		"""
		与NPC对话陷阱
		"""
		if not isEnter:
			self.hide()														#隐藏当前繁殖窗口

	def __getProcreatePets( self ):
		"""
		获取可繁殖的宠物信息
		"""
		petEpitomes = []
		for epitome in BigWorld.player().pcg_getPetEpitomes().itervalues() :
			if epitome.conjured :
				continue
			if not formulas.isHierarchy( epitome.species, csdefine.PET_HIERARCHY_INFANCY1 ) :
				continue
			if epitome.level < csconst.PET_PROCREATE_MIN_LEVEL :
				continue
			if epitome.life < csconst.PET_PROCREATE_LIFT_NEED:
				continue
			if epitome.joyancy < csconst.PET_PROCREATE_JOY_NEED:
				continue
			petEpitomes.append( epitome )
		return petEpitomes

	# -------------------------------------------------------------------
	def __onDstStateChange( self, dstState ):
		"""
		对方状态改变通知
		"""
		self.dstState = dstState
		player = BigWorld.player()
		self.__pyFosterBtn.enable = player.procreateState == csdefine.PET_PROCREATION_LOCK and \
			dstState in [csdefine.PET_PROCREATION_LOCK, csdefine.PET_PROCREATION_SURE]
		if dstState == csdefine.PET_PROCREATION_DEFAULT: #初始状态，说明队友关闭了窗口
			self.hide()
		elif dstState == csdefine.PET_PROCREATION_WAITING: #等待状态
			player = BigWorld.player()
#			if not player.isCaptain(): #不是队长
#				self.__onOpenFosterWnd()
		elif dstState == csdefine.PET_PROCREATION_SELECTING: #选择状态
			self.__pyMyFosterPet.setPetCBEnable( True )
			self.__pyBtnLock.enable = self.__pyMyFosterPet.getSelPetItem() is not None
		elif dstState == csdefine.PET_PROCREATION_LOCK: #锁定状态
			self.__pyFosterBtn.enable = player.procreateState == csdefine.PET_PROCREATION_LOCK
		elif dstState == csdefine.PET_PROCREATION_SURE: #确认状态
			self.__pyMyFosterPet.setPetCBEnable( False )
		else: #确认后状态
			if not BigWorld.player().isCaptain(): #不是队长
				expense = formulas.getProcreatePetCost()
				expenseText = utils.currencyToViewText( expense )
#				self.__pyRtExpense.text = PL_Font.getSource( "需要费用:%s"%expenseText, fc = ( 230, 227, 185, 255 ) )
		if dstState in [csdefine.PET_PROCREATION_LOCK, csdefine.PET_PROCREATION_SURE]:
			self.__pyDstFosterPet.stateStr = labelGather.getText( "PetsWindow:PetFoster", "lockedStatus" )
		else:
			self.__pyDstFosterPet.stateStr = labelGather.getText( "PetsWindow:PetFoster", "unlockStatus" )

	def __onDstPetChange( self, petEpitome ):
		"""
		对方更改宠物
		"""
		self.__pyDstFosterPet.setPetInfo( petEpitome )
		self.__pyDstFosterPet.enable = False

	def __onUpdateRemainTime( self, remainTime ):
		"""
		更新繁殖剩余时间
		"""
		if not self.visible:return
		remainHours = remainTime/3600
		remMins = ( remainTime%3600 )/60
		self.__pyRtRemianTime.text = labelGather.getText( "PetsWindow:PetFoster", "remainTime" )%( remainHours, remMins )

	def __onMyPetChange( self, petDBID ):
		"""
		自己选择宠物改变，只是客户端表现
		"""
		petEpitome = BigWorld.player().pcg_getPetEpitome( petDBID )
		self.__pyBtnLock.enable = petEpitome is not None
		if petEpitome is None:return
		self.__pyMyFosterPet.setPetInfo( petEpitome )

	def __onHide( self ):
		"""
		隐藏窗口
		"""
		self.hide()


	def __onLock( self ):
		"""
		锁定繁殖宠物
		"""

		BigWorld.player().cell.pft_playerChangeState( csdefine.PET_PROCREATION_LOCK )

	def __onBreed( self ):
		"""
		开始繁殖，进行一系列条件判断
		"""
		myEpitome = self.__pyMyFosterPet.getPetEpitome()
		dstEpitome = self.__pyDstFosterPet.getPetEpitome()

		if myEpitome is None or dstEpitome is None:return
		player = BigWorld.player()

		if myEpitome.procreated or dstEpitome.procreated : #成熟
			player.statusMessage( csstatus.PET_PROCREATE_FAIL_PROCREATED )
			return

		if not formulas.isHierarchy( myEpitome.species, csdefine.PET_HIERARCHY_INFANCY1 ) or \
			not formulas.isHierarchy( dstEpitome.species, csdefine.PET_HIERARCHY_INFANCY1 ) : #是否为一代宝宝
				player.statusMessage( csstatus.PET_PROCREATE_FAIL_NEED_INFANCY )
				return

		type1 = formulas.getType( myEpitome.species )
		type2 = formulas.getType( dstEpitome.species )
		if type1 != type2 : #是否为同类
			player.statusMessage( csstatus.PET_PROCREATE_FAIL_DIFFER_TYPE )
			return

		if myEpitome.gender == dstEpitome.gender : #同一性别
			player.statusMessage( csstatus.PET_PROCREATE_FAIL_SAME_SEX )
			return

		level1 = myEpitome.level
		level2 = dstEpitome.level
		if level1 < csconst.PET_PROCREATE_MIN_LEVEL or \
			level2 < csconst.PET_PROCREATE_MIN_LEVEL :
				player.statusMessage( csstatus.PET_PROCREATE_FAIL_LEVEL_SHORT )
				return

		if myEpitome.life < csconst.PET_PROCREATE_LIFT_NEED or dstEpitome.life < csconst.PET_PROCREATE_LIFT_NEED:
			player.statusMessage( csstatus.PET_PROCREATE_FAIL_LIFE_LACK )
			return

		if myEpitome.joyancy < csconst.PET_PROCREATE_JOY_NEED or dstEpitome.joyancy < csconst.PET_PROCREATE_JOY_NEED:
			player.statusMessage( csstatus.PET_PROCREATE_FAIL_JOY_LACK )
			return

		player.cell.pft_playerChangeState( csdefine.PET_PROCREATION_SURE ) #确认繁殖

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def show( self ):
		player = BigWorld.player()
		fosterMate = self.getFosterMate()
		if fosterMate is None:return
		self.__pyStDstName.text = labelGather.getText( "PetsWindow:PetFoster", "ownerName" )%fosterMate.name
		self.__pyStMyName.text = labelGather.getText( "PetsWindow:PetFoster", "ownerName" )%player.getName()
		self.__pyMyFosterPet.setPetCBText( labelGather.getText( "PetsWindow:PetFoster", "myPet") )
		self.__pyMyFosterPet.enable = False
		self.__pyDstFosterPet.setPetCBText( labelGather.getText( "PetsWindow:PetFoster", "targetPet") )
		self.__pyMyFosterPet.setPetCBEnable( True )
		self.__pyExpPanel.text = labelGather.getText( "PetsWindow:PetFoster", "explain" )
		moneyText = utils.currencyToViewText( FOSTER_EXPENSE )
		expStr = labelGather.getText( "PetsWindow:PetFoster", "captainPay" )%moneyText
		self.__pyRtExpense.text = PL_Font.getSource( expStr, fc = ( 230, 227, 185, 255 ) )

		Window.show( self )

	def getFosterMate( self ):
		for id, teamMate in BigWorld.player().teamMember.items():
			if id == BigWorld.player().id:continue
			return teamMate
		return None

	def hide( self ):
		self.__pyMyFosterPet.initialize()
		self.__pyDstFosterPet.initialize()
		self.__pyMyFosterPet.stateStr = ""
		self.__pyDstFosterPet.stateStr = ""
		self.__pyBtnLock.enable = False
		self.__pyFosterBtn.enable = False
		self.__pyRtExpense.text = ""
		self.__pyRtRemianTime.text = ""
		self.dstState = -1
		BigWorld.player().cell.pft_playerChangeState( csdefine.PET_PROCREATION_DEFAULT ) #设置初始状态
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		Window.hide( self )

	def onLeaveWorld( self ) :
		self.hide()

# --------------------------------------------------------------
# 待繁殖宠物信息
from guis.common.PyGUI import PyGUI
from NPCModelLoader import NPCModelLoader
g_npcmodel = NPCModelLoader.instance()

class FosterPet( PyGUI ):

	_pet_genders = {  csdefine.GENDER_MALE: labelGather.getText( "PetsWindow:PetFoster", "gender_male" ),
		csdefine.GENDER_FEMALE: labelGather.getText( "PetsWindow:PetFoster", "gender_female" )
		}

	_pet_breeds = {csdefine.PET_PROCREATE_STATUS_NONE:	labelGather.getText( "PetsWindow:PetsPanel", "status_none" ),
			csdefine.PET_PROCREATE_STATUS_PROCREATING:	labelGather.getText( "PetsWindow:PetsPanel", "status_procreating" ),
			csdefine.PET_PROCREATE_STATUS_PROCREATED:	labelGather.getText( "PetsWindow:PetsPanel", "status_procreated" )
			}

	def __init__( self, petPanel ):
		PyGUI.__init__( self, petPanel )
		self.__petEpitome = None
		self.__pyFosterPetCB = ODComboBox( petPanel.petCB )
		self.__pyFosterPetCB.autoSelect = False
		self.__pyFosterPetCB.ownerDraw = True
		self.__pyFosterPetCB.onViewItemInitialized.bind( self.onInitialized_ )
		self.__pyFosterPetCB.onDrawItem.bind( self.onDrawItem_ )
		self.__pyFosterPetCB.onItemSelectChanged.bind( self.__onPetSelected )

		self.__pyPetHead = PyGUI( petPanel.petHead )
		self.__pyPetHead.texture = ""

		self.__pyRtPetName = CSRichText( petPanel.rtPetName )
		self.__pyRtPetName.text = ""

		self.__pyRtPetLevel = CSRichText( petPanel.rtPetLevel )
		self.__pyRtPetLevel.text = ""

		self.__pyStState = StaticText( petPanel.stState )
		self.__pyStState.text = ""

	def onInitialized_( self, pyViewItem ):
		pyPetEpitome = StaticLabel()
		pyPetEpitome.focus = False
		pyPetEpitome.foreColor = 236, 218, 157
		pyPetEpitome.h_anchor = "CENTER"
		pyViewItem.addPyChild( pyPetEpitome )
		pyViewItem.pyPetEpitome = pyPetEpitome

	def onDrawItem_( self, pyViewItem ):
		pyPanel = pyViewItem.pyPanel
		if pyViewItem.selected :
			pyViewItem.pyPetEpitome.foreColor = pyPanel.itemSelectedForeColor			# 选中状态下的前景色
			pyViewItem.color = pyPanel.itemSelectedBackColor				# 选中状态下的背景色
		elif pyViewItem.highlight :
			pyViewItem.pyPetEpitome.foreColor = pyPanel.itemHighlightForeColor		# 高亮状态下的前景色
			pyViewItem.color = pyPanel.itemHighlightBackColor				# 高亮状态下的背景色
		else :
			pyViewItem.pyPetEpitome.foreColor = pyPanel.itemCommonForeColor
			pyViewItem.color = pyPanel.itemCommonBackColor
		pyPetEpitome = pyViewItem.pyPetEpitome
		pyPetEpitome.left = 1.0
		pyPetEpitome.top = 1.0
		petEpitome = pyViewItem.listItem
		pyPetEpitome.text = petEpitome.name

	def __onPetSelected( self, selIndex ):
		"""
		选择某个宠物
		"""
		player = BigWorld.player()
		petEpitome = self.__pyFosterPetCB.selItem
		if petEpitome is None:return
		petDBID = petEpitome.databaseID
		player.cell.pft_selectPet( petDBID )
		ECenter.fireEvent( "EVT_ON_PETFOSTER_MY_PET_CHANGE", petDBID )

	def addPetCBItem( self, epitome ):
		"""
		下拉菜单添加宠物列表
		"""
		self.__pyFosterPetCB.addItem( epitome )

	def setPetInfo( self, petEpitome ):
		self.__petEpitome = petEpitome
		if petEpitome is None:return
		self.__pyFosterPetCB.pyBox_.text = petEpitome.name
		level = petEpitome.level
		modelNumber = petEpitome.modelNumber
		self.__pyPetHead.texture = g_npcmodel.getHeadTexture( modelNumber ) #宠物头像
		hierarchy = petEpitome.hierarchy #宠物辈分
		gender = petEpitome.gender #性别
		procreated = petEpitome.procreated
		isBreed = self._pet_breeds.get( procreated, "" )
		if formulas.isHierarchy( hierarchy, csdefine.PET_HIERARCHY_GROWNUP ): #成年宠物
			hierColor = ( 255, 255, 255, 255 )
			hierText = labelGather.getText( "PetsWindow:PetsPanel", "hierarchy_grownup" )
		elif formulas.isHierarchy( hierarchy, csdefine.PET_HIERARCHY_INFANCY1 ): #一代宝宝
			hierColor = ( 0, 0, 255, 255 )
			hierText = labelGather.getText( "PetsWindow:PetsPanel", "hierarchy_infancy1" )
		else: #二代宝宝
			hierColor = ( 254, 163, 8, 255 )
			hierText = labelGather.getText( "PetsWindow:PetsPanel", "hierarchy_infancy2" )
		hierText = PL_Font.getSource( hierText, fc = hierColor )
		gender = petEpitome.gender
		genderStr = self._pet_genders.get( gender ) #性别
		ability = petEpitome.ability #成长度
		name = petEpitome.name
		genderInfo = PL_Font.getSource( "%s%s"%( genderStr, isBreed ), fc=( 1, 255, 216, 255 ) )
		self.__pyRtPetName.text = "%s%s%s"%( hierText, PL_Space.getSource( 4 ), genderInfo )
		levelText = PL_Font.getSource( labelGather.getText( "PetsWindow:PetFoster", "levelText" ), fc = ( 230, 227, 185, 255 ) )
		levelInfo = PL_Font.getSource( "%s%d"%( levelText, level ), fc=( 1, 255, 216, 255 ) )
		abilityText = PL_Font.getSource( labelGather.getText( "PetsWindow:PetFoster", "abilityText" ), fc = ( 230, 227, 185, 255 ) )
		abilityInfo = PL_Font.getSource( "%s%d"%( abilityText, ability ), fc=( 1, 255, 216, 255 ) )
		self.__pyRtPetLevel.text = "%s%s%s"%( levelInfo, PL_Space.getSource( 4 ), abilityInfo )

	def getPetEpitome( self ):
		"""
		获取宠物信息
		"""
		return self.__petEpitome

	def setPetCBText( self, text ):
		"""
		设置宠物名称
		"""
		self.__pyFosterPetCB.pyBox_.text = text

	def setPetCBEnable( self, state = True ):
		"""
		设置下拉菜单状态
		"""
		self.__pyFosterPetCB.enable = state

	def setPetCBReadAttr( self, readOnly = True ):
		"""
		设置下拉菜单只读属性
		"""
		self.__pyFosterPetCB.readOnly = readOnly

	def getSelPetItem( self ):
		"""
		获取选择宠物
		"""
		return self.__pyFosterPetCB.selItem

	def initialize( self ):
		"""
		初始化面板信息
		"""
		self.__pyFosterPetCB.clearItems()
		self.__pyFosterPetCB.pyBox_.text = ""
		self.__pyPetHead.texture = ""
		self.__pyRtPetName.text = ""
		self.__pyRtPetLevel.text = ""

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getStateStr( self ):
		return self.__pyStState.text

	def _setStateStr( self, stateStr ):
		self.__pyStState.text = stateStr
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	stateStr = property( _getStateStr, _setStateStr )
