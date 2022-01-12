# -*- coding: gb18030 -8-

# This module implements the TeamInfoPanel which views teammate and team applicants info
# written by gjx 2009-9-16

from guis import *
from guis.controls.TabCtrl import TabPanel
from guis.controls.ODListPanel import ODListPanel
from guis.controls.ButtonEx import HButtonEx
from RowItem import RowItem
from LabelGather import labelGather
import event.EventCenter as ECenter
import time
import csconst
import csstatus


# --------------------------------------------------------------------
# ������Ϣ������
# --------------------------------------------------------------------
class TeamInfoPanel( TabPanel ) :

	def __init__( self, panel, pyBinder ) :
		TabPanel.__init__( self, panel, pyBinder )
		self.initialize_( panel )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def initialize_( self, panel ) :
		"""
		��ʼ���б�
		"""
		class ListPanel( ODListPanel ) :
			def getViewItem_( self ) :
				return RowItem( self )
		self.pyInfoPanel_ = ListPanel( panel.infoPanel, panel.scrollBar )
		self.pyInfoPanel_.onViewItemInitialized.bind( self.onInitItem_ )
		self.pyInfoPanel_.onDrawItem.bind( self.onDrawItem_ )
		self.pyInfoPanel_.itemHeight = 23
		self.pyInfoPanel_.ownerDraw = True

	# -------------------------------------------------
	def onDrawItem_( self, pyRowItem ) :
		"""
		�ػ���Ϣ��
		"""
		pyRowItem.refreshInfo( pyRowItem.listItem )

	def onInitItem_( self, pyRowItem )	 :
		"""
		��ʼ����Ϣ�У������Զ�����ƺ����ķ���
		"""
		pass

	# -------------------------------------------------
	def onSelected_( self ) :
		"""
		��ѡ��Ϊ�ɼ���������Ϊ�ɼ����
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def clearPanel( self ) :
		"""
		��������Ϣ
		"""
		self.pyInfoPanel_.clearItems()

	def resetState( self ) :
		"""
		ˢ�������Ϣ��ѡ��״̬
		"""
		self.pyInfoPanel_.resetState()


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _setVisible( self, visible ) :
		TabPanel._setVisible( self, visible )
		if visible : self.onSelected_()

	# -------------------------------------------------
	visible = property( TabPanel._getVisible, _setVisible )


# --------------------------------------------------------------------
# ������ӵ������Ϣ���
# --------------------------------------------------------------------
class ApplicantPanel( TeamInfoPanel ) :

	__MAX_AMOUNT = 20											# �б����������������

	def __init__( self, panel, pyBinder ) :
		TeamInfoPanel.__init__( self, panel, pyBinder )

		self.__detectCBID = 0									# ���볬ʱ���ص�ID


	# ----------------------------------------------------------------
	# virtual method
	# ----------------------------------------------------------------
	def initialize_( self, panel ) :
		TeamInfoPanel.initialize_( self, panel )

		self.__pyRefuseBtn = HButtonEx( panel.refuseBtn )			# �ܾ���ť
		self.__pyRefuseBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyRefuseBtn.onLClick.bind( self.__refuse )

		self.__pyClearBtn = HButtonEx( panel.clearBtn )			# ��հ�ť
		self.__pyClearBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyClearBtn.onLClick.bind( self.__clear )

		self.__pyInviteBtn = HButtonEx( panel.acceptBtn )			# ���밴ť
		self.__pyInviteBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyInviteBtn.onLClick.bind( self.__invite )

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pyRefuseBtn, "teammateinfo:teamInfoWindow", "refuseBtn" )
		labelGather.setPyBgLabel( self.__pyClearBtn, "teammateinfo:teamInfoWindow", "clearBtn" )
		labelGather.setPyBgLabel( self.__pyInviteBtn, "teammateinfo:teamInfoWindow", "acceptBtn" )


	# -------------------------------------------------
	# private
	# -------------------------------------------------
	def __refuse( self ) :
		"""
		�ܾ�ĳ����ҵ�������룬�ڹ涨ʱ������
		��������޷��ٷ��͸��ҵ�����
		"""
		selApplicant = self.pyInfoPanel_.selItem
		if selApplicant is None : return
		self.pyInfoPanel_.removeItem( selApplicant )
		BigWorld.player().refusePlayerJoinTeam( selApplicant[3], selApplicant[0] )

	def __clear( self ) :
		"""
		����б��е������������
		"""
		self.clearPanel()

	def __invite( self ) :
		"""
		����ѡ�е���Ҽ������
		"""
		selApplicant = self.pyInfoPanel_.selItem
		if selApplicant is None : return
		self.pyInfoPanel_.removeItem( selApplicant )
		BigWorld.player().allowPlayerJoinTeam( selApplicant[3], selApplicant[0] )

	def __startFilter( self ) :
		if not self.__detectCBID :
			self.__filter()

	def __filter( self ) :
		"""
		��鲢�Ƴ���ʱ���������
		"""
		if self.pyInfoPanel_.itemCount == 0 :
			ECenter.fireEvent( "EVT_ON_SET_CAPTAIN_MARK_NORMAL" )
			self.__shutdownFilter()
			return
		currTime = time.time()
		for applicant in self.pyInfoPanel_.items :
			if currTime - applicant[-1] < 60 : continue
			self.pyInfoPanel_.removeItem( applicant )
		self.__detectCBID = BigWorld.callback( 1, self.__filter )

	def __shutdownFilter( self ) :
		if self.__detectCBID :
			BigWorld.cancelCallback( self.__detectCBID )
			self.__detectCBID = 0

	def __enableButtons( self ) :
		"""
		������ҵ�״̬�仯��ʹ�ܸ������ܰ�ť
		"""
		player = BigWorld.player()
		isCaptain = player.isCaptain()
		self.__pyRefuseBtn.enable = isCaptain
		self.__pyInviteBtn.enable = isCaptain


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onSelected_( self ) :
		self.resetState()
		ECenter.fireEvent( "EVT_ON_SET_CAPTAIN_MARK_NORMAL" )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addApplicant( self, name, metier, level, entityID ) :
		"""
		���յ�������ӵ������Ϣ
		@param	name		: �����ߵ�����
		@param	metier		: �����ߵ�ְҵ
		@param	level		: �����ߵĵȼ�
		@param	entityID	: �����ߵ�entity id
		"""
		for index, n in enumerate( self.pyInfoPanel_.items ) :
			if name == n[0] :
				self.pyInfoPanel_.removeItemOfIndex( index )
				break
		else :
			BigWorld.player().statusMessage( csstatus.TEAM_NOTIFY_NEW_APPLICANT, name )
		pclass = csconst.g_chs_class[ metier ]						# ְҵת��Ϊ����
		applicant = ( name, pclass, level, entityID, time.time() )	# �洢ΪԪ��
		self.pyInfoPanel_.addItem( applicant )
		itemAmount = self.pyInfoPanel_.itemCount
		if itemAmount > self.__MAX_AMOUNT :
			self.pyInfoPanel_.removeItemOfIndex( 0 )
		self.__startFilter()
		if not self.visible or not self.pyBinder.visible :
			ECenter.fireEvent( "EVT_ON_NOTIFY_NEW_TEAM_APPLICANT" )

	def reset( self ) :
		self.clearPanel()
		self.__shutdownFilter()


# --------------------------------------------------------------------
# ��Ա��Ϣ���
# --------------------------------------------------------------------
class TeammatePanel( TeamInfoPanel ) :

	def __init__( self, panel, pyBinder ) :
		TeamInfoPanel.__init__( self, panel, pyBinder )


	# ----------------------------------------------------------------
	# virtual method
	# ----------------------------------------------------------------
	def initialize_( self, panel ) :
		TeamInfoPanel.initialize_( self, panel )

		self.__pyJoinBtn = HButtonEx( panel.joinBtn )			# ��Ӱ�ť
		self.__pyJoinBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyJoinBtn.onLClick.bind( self.__joinTeam )

		self.__pyKickBtn = HButtonEx( panel.kickBtn )			# �޳���ť
		self.__pyKickBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyKickBtn.onLClick.bind( self.__kickAway )
		self.__pyKickBtn.enable = False

		self.__pyFollowBtn = HButtonEx( panel.followBtn )		# �����Ա���水ť
		self.__pyFollowBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyFollowBtn.onLClick.bind( self.__follow )
		self.__pyFollowBtn.enable = False

		self.__pyCancelFollowBtn = HButtonEx( panel.cancelBtn )# ȡ�����水ť
		self.__pyCancelFollowBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelFollowBtn.onLClick.bind( self.__cancelFollow )
		self.__pyCancelFollowBtn.visible = False

		self.__pyLeaveBtn = HButtonEx( panel.leaveBtn )		# ��Ӱ�ť
		self.__pyLeaveBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyLeaveBtn.onLClick.bind( self.__leaveTeam )
		self.__pyLeaveBtn.enable = False

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pyJoinBtn, "teammateinfo:teamInfoWindow", "joinBtn" )
		labelGather.setPyBgLabel( self.__pyKickBtn, "teammateinfo:teamInfoWindow", "kickBtn" )
		labelGather.setPyBgLabel( self.__pyFollowBtn, "teammateinfo:teamInfoWindow", "followBtn" )
		labelGather.setPyBgLabel( self.__pyCancelFollowBtn, "teammateinfo:teamInfoWindow", "cancelBtn" )
		labelGather.setPyBgLabel( self.__pyLeaveBtn, "teammateinfo:teamInfoWindow", "leaveBtn" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __joinTeam( self ) :
		"""
		�������ģʽ/�Խ�����
		"""
		player = BigWorld.player()
		if not player.isInTeam() :
			player.inviteJoinTeamNear( player )				# �����Լ������Խ�����
		else :
			player.prepareForTeamInvite()

	def __kickAway( self ) :
		"""
		�޳�ĳ���
		"""
		player = BigWorld.player()
		if not player.isCaptain() : return
		selTm = self.pyInfoPanel_.selItem
		if selTm is None : return
		player.teamDisemploy( selTm[3] )

	def __follow( self ) :
		"""
		�ӳ������Ա����
		"""
		player = BigWorld.player()
		if not player.isCaptain() : return
		player.team_leadTeam()

	def __cancelFollow( self ) :
		"""
		ȡ������
		"""
		player = BigWorld.player()
		if player.isTeamLeading() :
			player.team_cancelFollow( csstatus.TEAM_CANCEL_FOLLOW )

	def __leaveTeam( self ) :
		"""
		�뿪����
		"""
		player = BigWorld.player()
		if player.isInTeam() :
			player.leaveTeam()

	def __enableButtons( self ) :
		"""
		������ҵ�״̬�仯��ʹ�ܸ������ܰ�ť
		"""
		player = BigWorld.player()
		isTeamLeading = player.isTeamLeading()
		isCaptain = player.isCaptain()
		self.__pyFollowBtn.enable = isCaptain
		self.__pyFollowBtn.visible = not isCaptain or not isTeamLeading
		self.__pyCancelFollowBtn.visible = isCaptain and isTeamLeading
		self.__pyKickBtn.enable = isCaptain
		self.__pyLeaveBtn.enable = player.isInTeam()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onSelected_( self ) :
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onMemberJoinIn( self, teammate ) :
		"""
		�¶�Ա����
		"""
		metier = csconst.g_chs_class[ teammate.raceclass ]			# ְҵת��Ϊ����
		tmInfo = ( teammate.name, metier, teammate.level, teammate.objectID )
		self.pyInfoPanel_.addItem( tmInfo )
		if teammate.objectID == BigWorld.player().captainID :		# ����ӽ������Ƕӳ�
			for tm in self.pyInfoPanel_.items :						# �Ѷӳ��ŵ���һ��λ��
				if tm[3] == teammate.objectID : break
				self.pyInfoPanel_.removeItem( tm )
				self.pyInfoPanel_.addItem( tm )

	def onRejoin( self, oldEntityID, newEntityID ) :
		"""
		��Ա���ߺ�����
		"""
		tmMembers = self.pyInfoPanel_.items
		for index, tm in enumerate( tmMembers ) :
			if tm[3] == oldEntityID :
				newInfo = ( tm[0], tm[1], tm[2], newEntityID )
				self.pyInfoPanel_.updateItem( index, newInfo )
				break

	def onMemberLeft( self, teammateID ) :
		"""
		��Ա���
		"""
		tmMembers = self.pyInfoPanel_.items
		for index, tm in enumerate( tmMembers ) :
			if tm[3] == teammateID :
				self.pyInfoPanel_.removeItemOfIndex( index )
				break
		self.__enableButtons()

	def onTeamDisbanded( self ) :
		"""
		�����ɢ
		"""
		self.clearPanel()
		self.__enableButtons()

	def onTMLevelChanged( self, teammateID, level ) :
		"""
		��Ա�ȼ��ı�
		"""
		tmMembers = self.pyInfoPanel_.items
		for index, tm in enumerate( tmMembers ) :
			if tm[3] == teammateID :
				newInfo = ( tm[0], tm[1], level, tm[3] )
				self.pyInfoPanel_.updateItem( index, newInfo )
				break

	def onTMNameChanged( self, teammateID, name ) :
		"""
		��Ա���ָı�
		"""
		tmMembers = self.pyInfoPanel_.items
		for index, tm in enumerate( tmMembers ) :
			if tm[3] == teammateID :
				newInfo = ( name, tm[1], tm[2], tm[3] )
				self.pyInfoPanel_.updateItem( index, newInfo )
				break

	def onCaptainChanged( self, captainID ) :
		"""
		�ӳ��ı䣬���ڶӳ�Ҫ�����ڵ�һ���������Ҫ��������
		"""
		for tm in self.pyInfoPanel_.items :
			if tm[3] == captainID : break
			self.pyInfoPanel_.removeItem( tm )
			self.pyInfoPanel_.addItem( tm )
		self.__enableButtons()

	def onFollowStateChanged( self ):
		"""
		����״̬�����仯
		"""
		self.__enableButtons()

	# -------------------------------------------------
	def reset( self ) :
		"""
		���ý��湤���ڴ˽���
		"""
		self.clearPanel()
		self.__pyFollowBtn.enable = False
		self.__pyFollowBtn.visible = True
		self.__pyCancelFollowBtn.visible = False
		self.__pyKickBtn.enable = False
		self.__pyLeaveBtn.enable = False
