# -*- coding: gb18030 -*-
#
# $Id: DutyPanel.py,v 1.4 2008-07-02 06:20:35 fangpengjun Exp $

"""
implement DutyPanel window
"""
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.PyGUI import PyGUI
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.controls.TextBox import TextBox
from guis.controls.ComboBox import ComboBox
from guis.controls.ComboBox import ComboItem
from config.client.msgboxtexts import Datas as mbmsgs
import GUIFacade
import csdefine
import csconst
import Const
from ChatFacade import chatFacade

class DutyPanel( Window ):
	__instance=None
	__duties = {}

	def __init__( self ):
		assert DutyPanel.__instance is None,"DutyPanel instance has been created"
		DutyPanel.__instance=self
		panel = GUI.load( "guis/general/relationwindow/tongpanel/tongduty.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )
		self.addToMgr( "dutyPanel" )
		self.pyBinder = None
		self.__triggers = {}
		self.__registerTriggers()
		self.__initPanel( panel )

	@staticmethod
	def instance():
		"""
		获得DutyPanel唯一的实例
		"""
		if DutyPanel.__instance is None:
			DutyPanel.__instance=DutyPanel()
		return DutyPanel.__instance

	@staticmethod
	def getInstance():
		"""
		return class DutyPanel instance,if DutyPanel.__instance is None return None ,
		else return the exclusive DutyPanel instance
		"""
		return DutyPanel.__instance


	def __del__(self):
		"""
		just for testing memroy leak
		"""
		pass

	def __initPanel( self, panel ):
		self.__pyDutyCB = ComboBox( panel.dutyCB )
		self.__pyDutyCB.text = labelGather.getText( "RelationShip:FamilyPanel", "duty" )
		self.__pyDutyCB.autoSelect = False
#		self.__pyDutyCB.width = 168.0
		self.__pyDutyCB.onItemLClick.bind( self.__onDutyChange )
#		self.__getNewDuties() # 初始化职务列表

		self.__pyBtnPreDuty = Button( panel.btnPreDuty )
		self.__pyBtnPreDuty.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnPreDuty.onLClick.bind( self.__onSelectPre )

		self.__pyBtnNextDuty = Button( panel.btnNextDuty )
		self.__pyBtnNextDuty.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnNextDuty.onLClick.bind( self.__onSelectNext )

		self.__pySendMsg = HButtonEx( panel.btnSend )
		self.__pySendMsg.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pySendMsg.onLClick.bind( self.__onSendMsg )
		labelGather.setPyBgLabel( self.__pySendMsg, "RelationShip:RelationPanel", "sendMsg" )

		self.__pyBtnInvite = HButtonEx( panel.btnInvite )
		self.__pyBtnInvite.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnInvite.onLClick.bind( self.__onInviteTeam )
		labelGather.setPyBgLabel( self.__pyBtnInvite, "RelationShip:RelationPanel", "teamInvite" )

		self.__pyStPlayerName = StaticText( panel.proPanel.st_name )		# 角色名字
		self.__pyStPlayerName.text = ""

		self.__pyStProfession = StaticText( panel.proPanel.st_prof )	# 角色职业
		self.__pyStProfession.text = ""

		self.__pyStContribute = StaticText( panel.proPanel.st_contribute )	# 贡献度
		self.__pyStContribute.text = ""

		self.__pyStAreaName = StaticText( panel.proPanel.st_area )			# 所在区域
		labelGather.setPyLabel( self.__pyStAreaName, "RelationShip:RelationPanel", "unknown" )

		self.__pyStTong = StaticText( panel.proPanel.st_tong )				# 所属帮会
		self.__pyStTong.text = ""

		labelGather.setLabel( panel.lbTitle, "RelationShip:FamilyPanel", "memberInfo" )
		labelGather.setLabel( panel.dutyText, "RelationShip:RelationPanel", "rt_tongDuty" )

		labelGather.setLabel( panel.proPanel.label_name, "RelationShip:RelationPanel", "rt_playerName" )
		labelGather.setLabel( panel.proPanel.label_prof, "RelationShip:RelationPanel", "rt_raceClass" )
		labelGather.setLabel( panel.proPanel.label_contribute, "RelationShip:RelationPanel", "rt_tongCont" )
		labelGather.setLabel( panel.proPanel.label_area, "RelationShip:RelationPanel", "rt_area" )
		labelGather.setLabel( panel.proPanel.label_tong, "RelationShip:RelationPanel", "rt_tong" )
	# -------------------------------------------------------------------
	# pravite
	# -------------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_AREA"] = self.__updateArea # 更新区域
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )

	def onInitDutyName(self,duty, dutyName ):
		self.__onInitDutyName(duty, dutyName )

	#-------------------------------------------------------------
	def __getNewDuties( self, memberLevel ):
		self.__pyDutyCB.clearItems()
		# 按权限大小排序
		dutiesList = DutyPanel.__duties.items()
		dutiesList.sort()							# 这里是从小到大
		dutiesList.reverse()
		tong_grade = BigWorld.player().tong_grade
		newDuties = copy.copy( DutyPanel.__duties )
		for key, duty in dutiesList:
			if key >= tong_grade:continue
			if memberLevel <30 and \
			tong_grade > csdefine.TONG_GRADE_DEALER and \
			key == csdefine.TONG_GRADE_DEALER: #小于30级的帮会成员不能设置为商人
				newDuties.pop( csdefine.TONG_GRADE_DEALER )
				continue
		return newDuties

	def __onInitDutyName( self, dutyKey, name ):
		if dutyKey > csdefine.TONG_DUTY_CHIEF:return #过滤帮主职位
		DutyPanel.__duties[dutyKey] = name

	def onUpdateDutyName( self, dutyKey, name ):
		for pyCBItem in self.__pyDutyCB.pyItems:
			if pyCBItem.tag == dutyKey and pyCBItem.text != name:
				pyCBItem.text = name
			if pyCBItem == self.__pyDutyCB.pySelItem:
				self.__pyDutyCB.text = name
		if DutyPanel.__duties.has_key( dutyKey ):
			DutyPanel.__duties[dutyKey] = name

	def onUpdateGrade( self, memberDBID, grade ):
		if memberDBID == BigWorld.player().databaseID:
			self.__reSetCB( grade )

	def __reSetCB( self, grade ):
		self.__pyDutyCB.clearItems()
		player = BigWorld.player()
		for key, duty in DutyPanel.__duties.iteritems():
			if key >= grade:continue
			pyCBItem = ComboItem( duty )
			pyCBItem.h_anchor = "CENTER"
			pyCBItem.tag = key
			self.__pyDutyCB.addItem( pyCBItem )
		canSetGrade = player.tong_checkDutyRights( player.tong_grade, csdefine.TONG_RIGHT_CHANGE_DUTY )
		self.__pyDutyCB.enable = canSetGrade
		self.__pyBtnPreDuty.enable = canSetGrade
		self.__pyBtnNextDuty.enable = canSetGrade

	def __onDutyChange( self, pyItem ):
		if pyItem is None: return
		tag = pyItem.tag
		memberID = self.pyBinder.getID()
		BigWorld.player().tong_setMemberGrade( memberID, tag )

	def __onTextTabOut( self ): # 修改列表中玩家备注
		if self.__pyRemarkBox.tabStop:return
		if self.pyBinder is None:return
		remarkText = self.__pyRemarkBox.text.strip()
		if len( remarkText ) > 7:
			# "备注不能超过7个字符!"
			showAutoHideMessage( 3.0, 0x0721, mbmsgs[0x0c22] )
			return
		elif rds.wordsProfanity.searchMsgProfanity( remarkText ) is not None :
			# "输入的备注有禁用词汇!"
			showAutoHideMessage( 3.0, 0x0722, mbmsgs[0x0c22] )
			return
		BigWorld.player().tong_setMemberScholium( self.pyBinder.getID(), remarkText )

	def __onSendMsg( self ):
		if self.pyBinder is None:return
		name = self.pyBinder.getName()
		chatFacade.whisperWithChatWindow( name )

	def __onInviteTeam( self ):
		if self.pyBinder is None:return
		name = self.pyBinder.getName()
		BigWorld.player().inviteJoinTeam( name )

	def __onSelectPre( self ):
		if self.__pyDutyCB.itemCount < 1:return
		selIndex = self.__pyDutyCB.selIndex
		foreIndex = selIndex - 1
		if foreIndex < 0:return
		foreItem = self.__pyDutyCB.pyItems[foreIndex]
		self.__pyDutyCB.pySelItem = foreItem
		self.__onDutyChange( foreItem )

	def __onSelectNext( self ):
		if self.__pyDutyCB.itemCount < 1:return
		selIndex = self.__pyDutyCB.selIndex
		nextIndex = selIndex + 1
		if nextIndex > self.__pyDutyCB.itemCount - 1:return
		nextItem = self.__pyDutyCB.pyItems[nextIndex]
		self.__pyDutyCB.pySelItem = nextItem
		self.__onDutyChange( nextItem )

	def __updateArea( self, memberDBID, spaceType, position, lineNumber ):
		if self.pyBinder and self.pyBinder._memberDBID == memberDBID:
			areaStr = labelGather.getText( "RelationShip:RelationPanel", "unknown" )
			if spaceType.startswith("fu_ben") and spaceType not in Const.CC_FUBENNAME_DONOT_CONVERT_LIST:
				areaStr = labelGather.getText( "RelationShip:RelationPanel", "spaceCopy" )
				return
			area = rds.mapMgr.getArea( spaceType, position )
			areaStr = lineNumber and labelGather.getText( "RelationShip:RelationPanel", "lineNumber" )%(area.name,lineNumber) or area.name
			self.__pyStAreaName.text = areaStr

	# ----------------------------------------------------
	def onEvent( self, macroName, *args ) :
		DutyPanel.instance().__triggers[macroName]( *args )

	def show( self, pyBinder ):
		if not pyBinder is None:
			self.reset()
			self.pyBinder = pyBinder
			player = BigWorld.player()
			self.__pyStPlayerName.text = pyBinder.getName()
			memberDBID = pyBinder._memberDBID
			memberGrade = player.tong_memberInfos[memberDBID].getGrade()

			player.base.tong_requestMemberMapInfos()
			self.__pyStContribute.text = str( pyBinder.getContribute() ) + "/" + str( pyBinder.getTotalContribute() ) # 贡献度
			self.__pyStTong.text = player.tongName # 所属帮会
			self.__pyStProfession.text = labelGather.getText( "RelationShip:TongPanel", "profInfo" )%( str( pyBinder.getLevel() ), str( pyBinder.getMetier() ) ) # 职业
			tongGrade = player.tong_grade
			memberLevel = pyBinder.getLevel()
			canSetGrade = player.tong_checkDutyRights( tongGrade, csdefine.TONG_RIGHT_CHANGE_DUTY ) and memberGrade < tongGrade
			self.__pyDutyCB.enable = canSetGrade
			self.__pyBtnPreDuty.enable = canSetGrade
			self.__pyBtnNextDuty.enable = canSetGrade
			newDuties = self.__getNewDuties( memberLevel )
			dutiesList = newDuties.keys()
			dutiesList.sort()							# 这里是从小到大
			dutiesList.reverse()
			self.__pyDutyCB.text = labelGather.getText( "RelationShip:FamilyPanel", "duty" )
			disDuties = []
			for grade in dutiesList:
				if canSetGrade and grade >= tongGrade:
					disDuties.append( grade )
					continue
				duty = player.tong_dutyNames.get( grade, "" )
				pyCBItem = ComboItem( duty )
				pyCBItem.h_anchor = "CENTER"
				pyCBItem.tag = grade
				self.__pyDutyCB.addItem( pyCBItem )
			resDuties = list( set( dutiesList ) - set( disDuties ) )
			resDuties.sort()
			resDuties.reverse()
			if memberGrade in resDuties:
				selIndex = resDuties.index( memberGrade )
				self.__pyDutyCB.selIndex = selIndex
			Window.show( self, pyBinder )

	def reset( self ):
		self.__pyStPlayerName.text = ""
		self.__pyStContribute.text = ""
		self.__pyStTong.text = ""
		self.__pyStProfession.text = ""
		labelGather.setPyLabel( self.__pyStAreaName, "RelationShip:RelationPanel", "unknown" )

	def hide( self ):
		self.pyBinder = None
		Window.hide( self )
		self.__deregisterTriggers()
		self.dispose()
		self.removeFromMgr()
		DutyPanel.__instance=None
		self.__triggers=None
