# -*- coding: gb18030 -*-
#
# $Id: TeammateArray.py,v 1.17 2008-08-26 02:20:21 huangyongwei Exp $

"""
imlement teammate array window
"""

from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.controls.Button import Button
from TeammateBox import TeammateBox
from config.client.msgboxtexts import Datas as mbmsgs
import GUIFacade
import csdefine
import BigWorld

class TeammateArray( RootGUI ) :
	__cc_rows  = 28.0

	def __init__( self ) :
		wnd = GUI.load( "guis/general/teammateinfo/arraywindow.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.h_dockStyle = "LEFT"
		self.v_dockStyle = "TOP"
		self.__initialize( wnd )
		self.focus= False
		self.moveFocus = False
		self.posZSegment = ZSegs.L5
		self.activable_ = False
		self.escHide_ 		 = False

		self.h_dockStyle = "LEFT"
		self.v_dockStyle = "TOP"

		self.__teammates = MapList()
		self.__isVisible = False

		self.__triggers = {}
		self.__registerTriggers()

	def __initialize( self, wnd ) :
		self.__pyArray = PyGUI( wnd.arrayPanel )

		self.__pyShowBtn = Button( wnd.showBtn )
		self.__pyShowBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyShowBtn.onLClick.bind( self.__showArray )
		self.__pyShowBtn.visible = False
		self.__pyHideBtn = Button( wnd.hideBtn )
		self.__pyHideBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyHideBtn.onLClick.bind( self.__hideArray )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_TEAMMATESWINDOW"] = self.__toggleVisible
		self.__triggers["EVT_ON_INVITE_JOIN_TEAM"] = self.__onInviteToJoin
		self.__triggers["EVT_ON_REQUEST_JOIN_TEAM"] = self.__onRequestJoin
		self.__triggers["EVT_ON_TEAM_DISBANDED"] = self.__onTeamDisbanded
		self.__triggers["EVT_ON_TEAM_MEMBER_ADDED"] = self.__onMemberJoinIn
		self.__triggers["EVT_ON_TEAM_MEMBER_LEFT"] = self.__onMemberLeft
		self.__triggers["EVT_ON_TEAM_MEMBER_HP_CHANGED"] = self.__onMemberHPChanged
		self.__triggers["EVT_ON_TEAM_MEMBER_MP_CHANGED"] = self.__onMemberMPChanged
		self.__triggers["EVT_ON_TEAM_MEMBER_LEVEL_CHANGED"] = self.__onMemberLevelChanged
		self.__triggers["EVT_ON_TEAM_MEMBER_NAME_CHANGED"] = self.__onMemberNameChanged
		self.__triggers["EVT_ON_TEAM_MEMBER_HEADER_CHANGED"] = self.__onMemberHeaderChanged
		self.__triggers["EVT_ON_TEAM_CAPTAIN_CHANGED"] = self.__onCaptainChanged

		self.__triggers["EVT_ON_TEAM_MEMBER_REJOIN"] = self.__onRejoin
		self.__triggers["EVT_ON_TEAM_MEMBER_LOG_OUT"] = self.__onMemberLogOut
		self.__triggers["EVT_ON_TEAMMEMBER_ADD_BUFF"] = self.__onAddBuff
		self.__triggers["EVT_ON_TEAMMEMBER_REMOVE_BUFF"] = self.__onRemoveBuff
		self.__triggers["EVT_ON_TEAMMEMBER_UPDATE_BUFF"] = self.__onUpdateBuff
		self.__triggers["EVT_ON_INVITE_FOLLOW"] = self.__onInviteFollow
		
		self.__triggers["EVT_ON_TEAM_ADD_MEMBER_PET"] = self.__onTeamAddPet
		self.__triggers["EVT_ON_TEAM_MEMBER_PET_INFO_RECEIVE"] = self.__onRecPetInfo
		self.__triggers["EVT_ON_TEAM_MEMBER_PET_WITHDRAWED"] = self.__onPetWithdraw
		self.__triggers["EVT_ON_TEAMMEMBER_PET_ADD_BUFF"] = self.__onPetAddBuff
		self.__triggers["EVT_ON_TEAMMEMBER_PET_REMOVE_BUFF"] = self.__onPetRemoveBuff
		self.__triggers["EVT_ON_ENTER_SPECIAL_COPYSPACE"] = self.__onEnterSpaceCopy
		self.__triggers["EVT_ON_LEAVE_CHALLENGE_COPY"] = self.__onLeaveChalCopy

		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )

	# -------------------------------------------------
	def __layout( self ) :
		if len( self.__teammates ) == 0 : return
		pyFirstBox = self.__teammates.values()[0]
		pyFirstBox.left = 0.0
		pyFirstBox.top = 0.0
		top = 0.0
		for index, pyBox in enumerate( self.__teammates.values() ) :
			if index == 0: continue
			pyAboveBox = self.__teammates.values()[index-1]  #上一个队友头像
			if not pyAboveBox.getPetBox():  #如果没有出战宠物，则往上缩进
				pyBox.left = pyFirstBox.left
				pyBox.top = top + pyBox.height - self.__cc_rows
			else:
				pyBox.left = pyFirstBox.left
				pyBox.top = top + pyBox.height
			top = pyBox.top
		pyLastBox = self.__teammates.values()[-1]
		self.__pyArray.width = pyLastBox.right
		self.__pyArray.height = pyLastBox.bottom
		self.width = self.__pyArray.width
		self.height = self.__pyArray.bottom

	# -------------------------------------------------
	def __showArray( self ) :
		self.__pyArray.visible = True
		self.__pyShowBtn.visible = False
		self.__pyHideBtn.visible = True

	def __hideArray( self ) :
		self.__pyArray.visible = False
		self.__pyHideBtn.visible = False
		self.__pyShowBtn.visible = True

	# -------------------------------------------------
	def __addTeammate( self, joinor ) :
		pyBox = TeammateBox()
		self.__pyArray.addPyChild( pyBox )
		pyBox.teammateID = joinor.objectID
		pyBox.isLogOut = not joinor.online
		self.__teammates[joinor.objectID] = pyBox
		player = BigWorld.player()
		id = player.captainID
		pyBox.setRoleCaptain( id == pyBox.teammateID )
		self.__layout()

	def __removeTeammate( self, id ) :
		self.__teammates.pop( id ).dispose()
		self.__layout()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onLeaveWorld( self ) :
		self.hide()
		for pyWnd in self.__teammates.values() :
			pyWnd.dispose()
		self.__teammates = {}

	# ----------------------------------------------------------------
	# triggers
	# ----------------------------------------------------------------
	def __toggleVisible( self ) :
		"""
		显示/隐藏所有队友窗口
		"""
		if len( self.__teammates ) == 0 :
			self.visible = 0
			return
		self.visible = not self.visible

	def __onInviteToJoin( self, inviter ) :
		def notarize( id ) :
			result = False
			if id == RS_YES : result = True
			GUIFacade.revertInviteJoinTeam( result )
		# "%s 邀请你加入他的队伍，你是否接受？"
		msg = mbmsgs[0x0d61] % inviter
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def __onRequestJoin( self, requester ) :
		def notarize( id ) :
			result = False
			if id == RS_YES : result = True
			GUIFacade.revertRequestJoinTeam( result )
		# "%s 请求加入你的队伍，你是否同意？"
		msg = mbmsgs[0x0d62] % requester
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def __onInviteFollow( self, entityid ):
		captain = BigWorld.entities[entityid]
		if not captain: #如果玩家不存在了,退出
			return
		name = captain.playerName
		def notarize( id ) :
			if id == RS_YES :
				BigWorld.player().autoFollow( captain.id )
		# "%s 邀请你跟随他，你是否接受？"
		msg = mbmsgs[0x0d63] % name
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def __onTeamDisbanded( self ) :
		for pyBox in self.__teammates.values() :
			pyBox.dispose()
		self.__teammates.clear()
		self.scriptVisible = False

	def __onMemberJoinIn( self, joinor ) :
		# 理论上，下面这个永远不会触发，如果触发了，就必须检查具体的原因
		assert not self.__teammates.has_key( joinor.objectID )
		teammateID = joinor.objectID
		self.__addTeammate( joinor )
		self.__onMemberNameChanged( teammateID, joinor.name )
		self.__onMemberHeaderChanged( teammateID, joinor.header )
		self.__onMemberClassMarkChanged( teammateID, joinor.raceclass )
		self.__onMemberLevelChanged( teammateID, joinor.level )
		self.__onMemberHPChanged( teammateID, joinor.hp, joinor.hpMax )
		self.__onMemberMPChanged( teammateID, joinor.mp, joinor.mpMax )
		self.scriptVisible = True

	def __onMemberLeft( self, teammateID ) :
		if self.__teammates.has_key( teammateID ) :
			self.__removeTeammate( teammateID )
		if len( self.__teammates ) == 0 :
			self.scriptVisible = False

	def __onMemberHPChanged( self, teammateID, hp, hpMax ) :
		if self.__teammates.has_key( teammateID ) :
			self.__teammates[teammateID].updateRoleHP( hp, hpMax )

	def __onMemberMPChanged( self, teammateID, mp, mpMax ) :
		if self.__teammates.has_key( teammateID ):
			self.__teammates[teammateID].updateRoleMP( mp, mpMax )

	def __onMemberLevelChanged( self, teammateID, level ) :	# wsf，队友的等级改变
		if self.__teammates.has_key( teammateID ) :
			self.__teammates[teammateID].changeRoleLevel( level )

	def __onMemberNameChanged( self, teammateID, name ) :
		if self.__teammates.has_key( teammateID ) :
			self.__teammates[teammateID].changeRoleName( name )

	def __onMemberHeaderChanged( self, teammateID, header ) :
		if self.__teammates.has_key( teammateID ) :
			self.__teammates[teammateID].updateRoleHeader( header )

	def __onMemberClassMarkChanged( self, teammateID, classRace ):
		if self.__teammates.has_key( teammateID ) :
			self.__teammates[teammateID].setRoleClassMark( classRace )
#			self.__teammates[teammateID].tclassMark = classRace

	def __onCaptainChanged( self, captainID ) :
		player = BigWorld.player()
		id = player.captainID
		for pyBox in self.__teammates.values() :
			pyBox.setRoleCaptain( id == pyBox.teammateID )

	def __onRejoin( self, oldEntityID, newEntityID ):
		# 队员重新上线，这将会引起队员旧的entityID与新的entityID不一样，
		# 需要在这里把旧的引用删除，把新的引用加上
		pyBox = self.__teammates[oldEntityID]
		self.__teammates.pop( oldEntityID )
		self.__teammates[newEntityID] = pyBox
		pyBox.teammateID = newEntityID
		pyBox.isLogOut = False

	def __onMemberLogOut( self, teammateID ):
		for pyBox in self.__teammates.values() :
			if teammateID == pyBox.teammateID :
				pyBox.isLogOut = True
				#队友离线后将其HP、MP和level都设为问号
				pyBox.updateRoleHP( "???", "???" )
				pyBox.updateRoleMP( "???", "???" )
				pyBox.changeRoleLevel( 0 )
				pyBox.clearRoleBuff()	# 下线后清空
				pyBox.onMemberLogOut()
				
	def __onEnterSpaceCopy( self, skills, spaceType ):
		"""
		进入挑战副本，更改角色头像
		"""
		HEAD_MAPPINGS = { csdefine.GENDER_MALE:{"chiyou": "npcm1000",
											"huangdi": "npcm1002",
											"houyi": "npcm1004",
											"nuwo": "npcm1006",
										},
					csdefine.GENDER_FEMALE:{ "chiyou": "npcm1001",
											"huangdi": "npcm1003",
											"houyi": "npcm1005",
											"nuwo": "npcm1007"
										}
						}
		DEFAULT_MAPPINGS = { csdefine.CLASS_FIGHTER: "chiyou", 
							csdefine.CLASS_SWORDMAN: "huangdi", 
							csdefine.CLASS_ARCHER: "houyi", 
							csdefine.CLASS_MAGE: "nuwo" 
						}
		if spaceType == csdefine.SPACE_TYPE_CHALLENGE:
			player = BigWorld.player()
			for membID, atype in player.memberAvatars.items():
				pyTeamBox = self.__teammates.get( membID, None )
				teammate = player.teamMember.get( membID, None )
				if pyTeamBox is None:continue
				if teammate is None:continue
				gender = teammate.gender
				raceclass = teammate.raceclass
				if atype == "":
					atype = DEFAULT_MAPPINGS.get( raceclass, "" )
				headText = HEAD_MAPPINGS[gender][atype]
				headTexture = "maps/monster_headers/%s.dds"%headText
				pyTeamBox.updateRoleHeader( headTexture )
	
	def __onLeaveChalCopy( self ):
		"""
		离开副本的回调
		"""
		for membID, teammate in BigWorld.player().teamMember.items():
			pyTeamBox = self.__teammates.get( membID, None )
			if pyTeamBox is None:continue
			header = teammate.header
			pyTeamBox.updateRoleHeader( header )
	# -------------------------------------------------
	def __onAddBuff( self, teammateID, buffInfo ) :
		"""
		当增加一个 buff 时被调用
		"""
		if buffInfo.isNotIcon: return	# 不需要显示的buff
		self.__teammates[teammateID].addRoleBuff( buffInfo )

	def __onRemoveBuff( self, teammateID, buffInfo ) :
		"""
		当删除一个 buff 时被调用
		"""
		self.__teammates[teammateID].removeRoleBuff( buffInfo )

	def __onUpdateBuff( self, teammateID, index, buffInfo ) :
		"""
		当一个 buff 更新时被调用
		"""
		self.__teammates[teammateID].updateRoleBuff( index, buffInfo )
	
	def __onTeamAddPet( self, teammateID, petID, uname, name, modelNumber, species ):
		"""
		添加队友宠物回调
		"""
		self.__teammates[teammateID].onAddMemberPet( petID, uname, name, modelNumber, species )
		self.__layout()
	
	def __onRecPetInfo( self, teammateID, petInfos ):
		"""
		接收队友宠物信息
		"""
		self.__teammates[teammateID].onRecPetInfo( petInfos )
	
	def __onPetWithdraw( self, teammateID ):
		"""
		队友收回宠物
		"""
		self.__teammates[teammateID].onWithdrawPet()
		self.__layout()
	
	def __onPetAddBuff( self, teammateID, buffInfo ):
		"""
		队友宠物添加buff
		"""
		self.__teammates[teammateID].addPetBuff( buffInfo )
		
	def __onPetRemoveBuff( self, teammateID, bufff ):
		"""
		队友宠物移除buff
		"""
		self.__teammates[teammateID].removePetBuff( bufff )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getVisible( self ) :
		return self.__isVisible

	def _setVisible( self, isVisible ) :

		if len( self.__teammates ) == 0 :
			RootGUI._setVisible( self, False )
		else :
			RootGUI._setVisible( self, isVisible )
		self.__isVisible = isVisible

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	scriptVisible = property( _getVisible, _setVisible )
