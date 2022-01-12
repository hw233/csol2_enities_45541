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

TRADE_SWAP_ITEM = 1		# ��Ʒ����
TRADE_SWAP_PET = 0		# ���ｻ��

# ----------------------------------------------------------------
# ������������ߴ�������
# ----------------------------------------------------------------
from AbstractTemplates import MultiLngFuncDecorator

class deco_TeammateResetPyItems( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF ) :
		"""
		����������µ���������������ĳߴ�
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
		���½�ɫѪ��
		"""
		self.__pyRoleBox.updateHP( hp, hpMax )
	
	def updateRoleMP( self, mp, mpMax ):
		"""
		���½�ɫħ��ֵ
		"""
		self.__pyRoleBox.updateMP( mp, mpMax )
	
	def updateRoleHeader( self, header ):
		"""
		���½�ɫͷ��
		"""
		self.__pyRoleBox.updateHeader( header )
	
	def addRoleBuff( self, buffInfo ):
		"""
		��ɫ���buff
		"""
		self.__pyRoleBox.addBuff( buffInfo )
	
	def removeRoleBuff( self, buffInfo ):
		"""
		��ɫ�Ƴ�buff
		"""
		self.__pyRoleBox.removeBuff( buffInfo )
	
	def updateRoleBuff( self, index, itemInfo ):
		"""
		��ɫ����buff
		"""
		self.__pyRoleBox.updateBuff( index, itemInfo )
	
	def clearRoleBuff( self ):
		"""
		��ս�ɫbuff
		"""
		self.__pyRoleBox.clearBuff()
	
	def setRoleCaptain( self, isCaptain ):
		"""
		���öӳ����
		"""
		self.__pyRoleBox.isCaptain = isCaptain
	
	def setRoleClassMark( self, classMark ):
		"""
		����ְҵ���
		"""
		self.__pyRoleBox.tclassMark = classMark
	
	def changeRoleLevel( self, level ):
		"""
		��ɫ�ȼ��ı�
		"""
		if level == 0:
			self.__pyRoleBox.tLevel = "???"
		else:
			self.__pyRoleBox.tLevel = level
	
	def changeRoleName( self, name ):
		"""
		��ɫ���Ƹı�
		"""
		self.__pyRoleBox.tname = name
	
	def onMemberLogOut( self ):
		"""
		��������
		"""
		if self.__pyPetBox.visible:
			self.__pyPetBox.visible = False
			self.__pyPetBox.petID = 0

	# -------------------------------------------------------------------
	def onAddMemberPet( self, petID, uname, name, modelNumber, species ):
		"""
		��ʾ������Ϣ���
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
		���¶��ѳ�����Ϣ
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
		��ȡ����һ����������
		"""
		if name != "":
			return name
		return uname
	
	def updatePetHP( self, hp, hpMax ):
		"""
		���³���Ѫ��
		"""
		self.__pyPetBox.updateHP( hp, hpMax )
	
	def updatePetMP( self, mp, mpMax ):
		"""
		���³���ħ��ֵ
		"""
		self.__pyPetBox.updateMP( mp, mpMax )

	def changePetID( self, petID ):
		"""
		����id�ı�
		"""
		self.__pyPetBox.petID = petID
	
	def updatePetHeader( self, header ):
		"""
		���³���ͷ��
		"""
		self.__pyPetBox.updateHeader( header )
	
	def changePetLevel( self, level ):
		"""
		����ȼ��ı�
		"""
		if level == 0:
			self.__pyPetBox.tLevel = "???"
		else:
			self.__pyPetBox.tLevel = level
	
	def changePetName( self, name,nameColor ):
		"""
		�������Ƹı�
		"""
		self.__pyPetBox.tname = name
		self.__pyPetBox.setNameColr( nameColor )
	
	def addPetBuff( self, buffInfo ):
		"""
		�������buff
		"""
		self.__pyPetBox.addBuff( buffInfo )
	
	def removePetBuff( self, buffInfo ):
		"""
		�����Ƴ�buff
		"""
		self.__pyPetBox.removeBuff( buffInfo )
	
	def updatePetBuff( self, index, itemInfo ):
		"""
		�������buff
		"""
		return
		self.__pyPetBox.updateBuff( index, itemInfo )
	
	def clearPlayerBuff( self ):
		"""
		��ճ���buff
		"""
		self.__pyPetBox.clearBuff()
	
	def onWithdrawPet( self ):
		"""
		�ջس���
		"""
		self.__pyPetBox.visible = False
		self.__pyPetBox.petID = 0

	def getPetBox( self ):
		"""
		�Ƿ���ڳ���ͷ��
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
# ���ѳ���ͷ��
class PetBox( Control ):
	
	__cc_item_size = 12.0, 13.0
	
	def __init__( self, box, pyBinder = None ):
		Control.__init__( self, box, pyBinder )
		self.focus = True
		self.__initialize( box )
		self.pyBuffItems_ = []			# ����buff����
		self.pyDBuffItems_ = []		# ����buff����
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
		self.pyBinder.isLogOut = False #ȥ�����ѵ�������Ƥ
		if hpMax == "???" or hpMax == 0: #�������ߺ���HP����Ϊ�ʺ�
			rate = 1
			self.pyLbHP_.text = "???/???"
			self.pyBinder.isLogOut = True #������������������Ƥ��������ӵ�ԭ���Ƕ����ڽ�ɫ����ǰ���ߵĻ�ԭ���Ĵ�����޷�����������Ƥ
		else:
			rate = float( hp  ) / hpMax
			self.pyLbHP_.text = "%d/%d" % ( hp, hpMax )
		self.pyHPBar_.value = rate
		self.pyHPBar_.visible = True
	
	def updateMP( self, mp, mpMax ):
		rate = 0
		if mpMax == "???" or mpMax == 0: #�������ߺ���MP��Ϊ�ʺ�
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
		���ͷ��ѡȡ����
		"""
		Control.onLClick_( self, mods )
		try:
			entity = BigWorld.entities[self.petID]
		except:
			return
		rds.targetMgr.bindTarget( entity )
	
	def addBuff( self, itemInfo ) :
		"""
		�������һ�� buff ʱ������
		"""
		skillID = itemInfo.baseItem.getSourceSkillID()
		if itemInfo.baseItem.isMalignant(): #����buff
			for pyItem in self.pyDBuffItems_:
				if pyItem.itemInfo and pyItem.itemInfo.baseItem.getSourceSkillID() == skillID:
					pyItem.update( itemInfo )
					return
		else: #����buff
			for pyItem in self.pyBuffItems_:
				if pyItem.itemInfo and pyItem.itemInfo.baseItem.getSourceSkillID() == skillID:
					pyItem.update( itemInfo )
					return
		baseItem = itemInfo.baseItem
		if baseItem.isMalignant():# ����buff
			pyItem = self.getEmptyItem_( self.pyDBuffItems_ )
			pyItem.update( itemInfo )
		else: #����buff
			pyItem = self.getEmptyItem_( self.pyBuffItems_ )
			pyItem.update( itemInfo )
	
	def removeBuff( self, buffInfo ) :
		"""
		��ɾ����һ�� buff ʱ������
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
		����һ�� buff ����ʱ������
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
		����������ɫ���������ִ���
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
			rowIndex = index/5			# ������
			colIndex = index%5			# ������
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
			rowIndex = index/5			# ������
			colIndex = index%5			# ������
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
		�˵�����ǰ������
		"""
		self.pyCMenu_.clear()
		self.pyCMenu_.pyItems.adds( [self.pyMenu] )
		return True
		
	def __onAfterMenuPopUp( self ) :
		"""
		�˵����������
		"""
		self.__updateMenu()
	
	def __updateMenu( self ):
		"""
		ˢ�¶��ѳ���״̬
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
		���˵�ѡ����ʱ������
		"""
		pyItem.handler()
	
	def __espialPet( self ):
		"""
		�۲���ѳ���
		"""
		if BigWorld.entities.has_key( self.petID ) :
			pet = BigWorld.entities[ self.petID ]
			if rds.targetMgr.isPetTarget( pet ):
				pet.requeryPetDatas()
		
# ----------------------------------------------------------------
class RoleBox( PetBox ) :
	__cc_pro_states = {}									# ��ְͬҵ��״̬��� mapping λ
	__cc_pro_states[csdefine.CLASS_FIGHTER]	 = ( 1, 1 )		# սʿ
	__cc_pro_states[csdefine.CLASS_SWORDMAN] = ( 1, 2 )		# ����
	__cc_pro_states[csdefine.CLASS_ARCHER]	 = ( 2, 1 )		# ����
	__cc_pro_states[csdefine.CLASS_MAGE]	 = ( 2, 2 )		# ��ʦ

	__cg_pyBuffItems						 = []			# buff item �����
	__cc_item_size = 12.0, 25.0

	def __init__( self, box, pyBinder = None ) :
		PetBox.__init__( self, box, pyBinder )
		self.__tclassMark = -1
		self.teammateID = 0

		self.pyLbName_ = StaticText( box.lbName )
		self.pyLbName_.fontSize = 11
		self.pyLbName_.h_anchor = 'CENTER'
		self.pyLbLevel_ = StaticText( box.lbLevel )			# ���ѵȼ�
		self.pyLbLevel_.fontSize = 11
		self.pyLbLevel_.h_anchor = 'CENTER'
		self.pyCMenu_.onBeforePopup.bind( self.__onMenuPopUp )
		self.pyCMenu_.onAfterPopUp.bind( self.__onAfterMenuPopUp )
		self.pyCMenu_.onItemClick.bind( self.__onMenuItemClick )

		self.__menuItems = {}			# ���������еĲ˵������ÿ����ʾʱ�����´���
		self.__createMenuItems()
		self.__initialize( box )
		self.__resetPyItems()

	def __del__( self ) :
		if Debug.output_del_TeammateBox :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		PetBox.dispose( self )
		RoleBox.__cg_pyBuffItems += self.pyBuffItems_		# ���� buff item

	# ---------------------------------------
	def __initialize( self, box ) :
		self.__pyMark = PyGUI( box.captainMark )
		self.__pyMark.visible = False
		
		self.__pyClassMark = Icon( box.classMark )				# ����ְҵ���
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
			rowIndex = index/5			# ������
			colIndex = index%5			# ������
			pyItem.top = top + pyItem.height*rowIndex
			pyItem.left = colIndex*pyItem.width + 1.0 * colIndex
			pyItems.append( pyItem )

	@deco_TeammateResetPyItems
	def __resetPyItems( self ) :
		"""
		���貿��UIԪ�ص�λ�á���С�����������
		"""
		pass											# ����汾�����޸�

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onMenuPopUp( self ) :
		"""
		�˵�����ǰ������
		"""
		self.pyCMenu_.clear()
		self.__constructMenu()
		return True

	# -------------------------------------------------
	def __createMenuItems( self ) :
		"""
		�������п����õ��Ĳ˵���
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
		self.__menuItems["persistence"] = menuList						# ������һ�飬����˵�ÿ�ε���������ʾ

		pyItem0 = DefMenuItem()
		labelGather.setPyLabel( pyItem0, "teammateinfo:tmbox_MU", "miKickTeammate" )
		pyItem0.handler = self.__kickOutTeammate
		pyItem1 = DefMenuItem()
		labelGather.setPyLabel( pyItem1, "teammateinfo:tmbox_MU", "miSetCaptain" )
		pyItem1.handler = self.__changeCaptain
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )			# �����飬���Ѳ���
		self.__menuItems["teammate"] = [pySplitter, pyItem1, pyItem0]

		pyItem0 = DefMenuItem()
		labelGather.setPyLabel( pyItem0, "teammateinfo:tmbox_MU", "miInviteJoinTong" )
		pyItem0.handler = self.__InviteJoinTong
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		self.__menuItems["joinTong"] = [pySplitter, pyItem0]			# �����飬���������
		
		pyItem0 = DefMenuItem()
		labelGather.setPyLabel( pyItem0, "teammateinfo:tmbox_MU", "kickingVote" )
		pyItem0.handler = self.__kickingVote
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		self.__menuItems["kickingVote"] = [pySplitter, pyItem0]			# �����飬���������

	def __constructMenu( self ) :
		"""
		���ݵ�ǰ״̬�����Ҽ��˵�
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
		�˵����������
		"""
		self.__updateMenu()

	def __updateMenu( self ) :
		"""
		������ҵ�״̬���²˵������Ч��
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
		self.__menuItems["persistence"][0].enable = not self.isRoleLogOut									# ������˽����Ϣ��ѡ��
		self.__menuItems["persistence"][2].enable = tnear and samePlanes and 0 <= distance <= 10.0								# ���۲족ѡ��
		self.__menuItems["persistence"][4].enable = tnear and samePlanes and 0 <= distance <= 20.0								# �����桱ѡ��
		self.__menuItems["persistence"][6].enable = tnear and samePlanes and 0 <= distance <= csconst.COMMUNICATE_DISTANCE		# ��������Ʒ���ס�ѡ��
		self.__menuItems["persistence"][7].enable = tnear and samePlanes and 0 <= distance <= csconst.COMMUNICATE_DISTANCE		# ��������ｻ�ס�ѡ��
		#self.__menuItems["teammate"][0].enable = tnear and 0<= distance <= 15									# ��������桱ѡ��
		self.__menuItems["teammate"][1].enable = not self.isRoleLogOut												# ������Ϊ�ӳ���ѡ��
		BigWorld.callback( 0.1, self.__updateMenu )

	# ----------------------------------------------------------------
	# menuitem handlers
	# ----------------------------------------------------------------
	def __whisper( self, pyItem ) :
		"""
		��Ŀ�����˽��
		"""
		if not self.isRoleLogOut :
			chatFacade.whisperWithChatWindow( self.tname )

	def __espialTarget( self, pyItem ):
		"""
		����۲�Է���װ��������
		"""
		if BigWorld.entities.has_key( self.teammateID ) :
			teammate = BigWorld.entities[ self.teammateID ]
			espial.onEspialTarget( teammate )

	def __followTarget( self, pyItem ):
		"""
		����Ŀ���ƶ�
		"""
		if BigWorld.entities.has_key( self.teammateID ) :
			BigWorld.player().autoFollow( self.teammateID )

	def __inviteTradeItem( self, pyItem ) :
		"""
		������Ʒ����
		"""
		if BigWorld.entities.has_key( self.teammateID ) :
			teammate = BigWorld.entities[ self.teammateID ]
			GUIFacade.inviteSwapItem( teammate, TRADE_SWAP_ITEM )

	def __inviteTradePet( self, pyItem ):
		"""
		������ｻ��
		"""
		if BigWorld.entities.has_key( self.teammateID ) :
			teammate = BigWorld.entities[ self.teammateID ]
			GUIFacade.inviteSwapItem( teammate, TRADE_SWAP_PET )

	def __addToBuddy( self, pyItem ) :
		"""
		��Ϊ����
		"""
		BigWorld.player().addFriend( self.tname )

	def __addToBlackList( self, pyItem ) :
		"""
		�ӵ�������
		"""
		BigWorld.player().addBlacklist( self.tname )

	def __kickOutTeammate( self, pyItem ) :
		"""
		��������
		"""
		GUIFacade.kickoutTeam( self.teammateID )

	def __changeCaptain( self, pyItem ) :
		"""
		����Ŀ��Ϊ�ӳ�
		"""
		BigWorld.player().changeCaptain( self.teammateID )

	def __InviteRide( self, pyItem ):
		"""
		���빲��
		"""
		player = BigWorld.player()
		player.cell.inviteRide( self.teammateID )

	def __inviteFollow( self, pyItem ) :
		"""
		Ҫ���Ǹ�����
		"""
		BigWorld.player().inviteFollow( self.teammateID )

	def __InviteJoinTong( self, pyItem ):
		"""
		���������
		"""
		player = BigWorld.player()
		player.tong_requestJoinByPlayerName( self.tname )
	
	def __kickingVote( self, pyItem ):
		"""
		����ͶƱ
		"""
		voteWnd = TeamVoteWnd.instance()
		voteWnd.show( self )
		
	# -------------------------------------------------
	@staticmethod
	def __getBuffItem() :
		"""
		���һ�� buff item
		"""
		if len( RoleBox.__cg_pyBuffItems ) :
			return RoleBox.__cg_pyBuffItems.pop()
		return BuffItem()

	# -------------------------------------------------
	def __onMenuItemClick( self, pyItem ) :
		"""
		���˵�ѡ����ʱ������
		"""
		pyItem.handler( pyItem )

	def __onShowClass( self, pyMark ):
		"""
		��ʾְҵ��Ϣ
		"""
		classRace = self.__tclassMark
		if csconst.g_chs_class.has_key( classRace ):
			classText = csconst.g_chs_class[classRace]
			toolbox.infoTip.showToolTips( self, classText )

	def __onHideClass( self, pyMark ):
		"""
		����ְҵ��Ϣ
		"""
		toolbox.infoTip.hide()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def updateBuff( self, index, itemInfo ) :
		"""
		����һ�� buff ����ʱ������
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
		self.pyLbLevel_.text = str( level ) # + "��"
	# -------------------------------------------------
	tclassMark = property( _getTclassMark, _setTclassMark )
	isCaptain = property( _getIsCaptain, _setIsCaptain )
	isRoleLogOut = property( _getIsRoleLogOut, _setIsRoleLogOut )
	tname = property( _getTName, _setTName )
	tLevel = property( _getTLevel, _setTLevel )