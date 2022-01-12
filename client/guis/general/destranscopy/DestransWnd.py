# -*- coding: gb18030 -*-
# $Id: DestransWnd.py, fangpengjun Exp $

from guis import *
from LabelGather import labelGather
from guis.common.RootGUI import RootGUI
from guis.common.PyGUI import PyGUI
from guis.controls.RichText import RichText
from guis.controls.Button import Button
from guis.common.FlexExWindow import HVFlexExWindow
from guis.controls.StaticText import StaticText
from config.client.msgboxtexts import Datas as mbmsgs
from DestransDatasLoader import destransDatasLoader
from ChessBoardData import Datas as boardDatas
from PieceItem import PieceItem
from MarkItem import MarkItem
from DiceAnim import DiceAnim
from TeamateHead import TeamateHead
from MsgBox import MsgBox
from Function import Functor
from event import EventCenter as ECenter
import Language
import GUIFacade
import csdefine
import csconst
import Timer
from Time import Time
import Font
import random

class DestransWnd( RootGUI ):
	"""
	�����ֻظ���
	"""
	_destans_msgs = { csdefine.DESTINY_TRANS_FAILED_GATE: "ͨ��ʧ��",
					csdefine.DESTINY_TRANS_FINISH_GATE: "ͨ�سɹ�",
					csdefine.DESTINY_TRANS_FIRST_NAME: "ͨ�ص�һ��",
					}
	
	def __init__( self ):
		wnd = GUI.load( "guis/general/destranscopy/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.focus = False
		self.h_dockStyle = "HFILL"
		self.v_dockStyle = "VFILL"
		self.posZSegment = ZSegs.L2
		self.escHide_ = False
		self.__pyPieces = {}				#���Ӽ���
		self.__roleMarks = {}				#��Ҳ���
		self.__teamHeads = {}				#����ͷ��
		self.__markMovecbids = {}			#����ƶ��ص�
		self.__cdTimId = 0				#����ʱcbid
		self.__boardNum = -1			#��ǰ���̱��
		self.__dicepoint = 0			#ɫ�ӵ���
		self.__delaycbid = 0			#�ӳ���ʾ����
		self.__lastTime = 0.0
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()
	
	def __initialize( self, wnd ):
		self.__pyTeamPanel = PyGUI( wnd.teamPanel )
		
		board = wnd.cboard							#�������
		self.__pyBoard = PyGUI( board )
		self.__pyMsgBox = MsgBox()
		self.__pyMsgBox.hide()
		
		self.__pyStCount = StaticText( board.stCount )	#����ʱ
		self.__pyStCount.text = ""
		self.__pyStCount.font = "STXINWEI.TTF"
		self.__pyStCount.fontSize = 40
		self.__pyStCount.limning = Font.LIMN_OUT
		self.__pyStCount.color = 255, 0, 0
		
		self.__pyBtnCast = Button( board.btnCast )		#Ͷ��ɫ��
		self.__pyBtnCast.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnCast.onLClick.bind( self.__onCast )
		
		self.__pyAnimDice = DiceAnim( board.dices )
		self.__pyAnimDice.ponit = 0
		
		pcsPanel = board.piecsPanel
		self.__pyPcsPanel = PyGUI( pcsPanel )
		for name, item in pcsPanel.children:
			if not name.startswith( "piece_" ):continue
			index = int( name.split( "_" )[-1] )
			pyPiece = PieceItem( item, index, self )
			pyPiece.resetPiece()
			self.__pyPieces[index] = pyPiece

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_DESTINYTRANS_INTERFACE_SHOW"] = self.__onDestransWndShow
		self.__triggers["EVT_ON_ROLE_DESTINYTRANS_COUNTDOWN"] = self.__onDestransCountDown
		self.__triggers["EVT_ON_ROLE_DESTINYTRANS_SIEVE_POINT"] = self.__onDestransSievePoint
		self.__triggers["EVT_ON_ROLE_DESTINYTRANS_MOVE_CHESS"] = self.__onDestransMoveChess
		self.__triggers["EVT_ON_ROLE_DESTINYTRANS_MOVE_TO_START"] = self.__onDestransToStart
		self.__triggers["EVT_ON_ROLE_DESTINYTRANS_LIVE_POINT_CHANGED"] = self.__onLivePointChanged
		self.__triggers["EVT_ON_ROLE_DESTINYTRANS_INTERFACE_CLOSE"] = self.__onDestransWndClose
		self.__triggers["EVT_ON_ROLE_DESTINYTRANS_DESTRANS_MSGS"] = self.__onDestransMsgs
		self.__triggers["EVT_ON_TEAM_MEMBER_LEFT"] = self.__onMemberLeft
		self.__triggers["EVT_ON_RESOLUTION_CHANGED"] = self.__onResolutionChanged
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )
	# ----------------------------------------------------------------
	def __onDestransWndShow( self, boardNum, gateInfo, livePointInfo ):
		"""
		��ʾ����
		"""
		if self.__boardNum != boardNum:					#���̱�Ų�ͬ�����¼���
			self.__boardNum = boardNum
			pieces = destransDatasLoader.getPieces( boardNum )
			if pieces is None:return
			for index, pyPiece in self.__pyPieces.items():
				piece = pieces.get( index, None )
				pyPiece.setPieceInfo( piece )
				pyPiece.onMouseEnter.bind( self.__onMouseEnter )
				pyPiece.onMouseLeave.bind( self.__onMouseLeave )
		for dbid, step in gateInfo.items():
			roleMark = None
			if dbid in self.__roleMarks:
				roleMark = self.__roleMarks[dbid]
			else:
				roleMark = MarkItem( dbid )
				self.__roleMarks[dbid] = roleMark
				self.__pyPcsPanel.addPyChild( roleMark )
			if roleMark is None:continue
			pieceInfo = destransDatasLoader.getPieceInfo( self.__boardNum, step[0] )
			if pieceInfo is None:continue
			pos = self.__getPicePos( pieceInfo[0] )
			if pos is None:continue
			roleMark.setStep( step[0] )
			roleMark.center = pos[0]
			roleMark.bottom = pos[1]
		for dbid, livePoint in livePointInfo.items():
			pyHead = None
			if dbid in self.__teamHeads:
				pyHead = self.__teamHeads[dbid]
			else:
				item = None
				if dbid == BigWorld.player().databaseID:
					item = GUI.load( "guis/general/destranscopy/rolehead.gui" )
				else:
					item = GUI.load( "guis/general/destranscopy/matehead.gui" )
				if item is None:continue
				uiFixer.firstLoadFix( item )
				pyHead = TeamateHead( item, dbid )
				self.__teamHeads[dbid] = pyHead
				self.__pyTeamPanel.addPyChild( pyHead )
			if pyHead is None:continue
			pyHead.setLivePoint( livePoint )
		self.__layoutTeamHead()
		self.__pyBtnCast.enable = True
		self.__dicepoint = random.randint( 1, 6)
		self.__pyAnimDice.point = self.__dicepoint
		self.__pyAnimDice.stop()
		self.show()

	def __getPicePos( self, index ):
		"""
		��ȡ����λ��
		"""
		pyPiece = self.__pyPieces.get( index )
		if pyPiece is None:return
		return ( pyPiece.center, pyPiece.middle + 5.0 )
	
	def __layoutTeamHead( self ):
		"""
		�������ͷ��
		"""
		player = BigWorld.player()
		if len( self.__teamHeads ) <= 0:return
		roleHead = self.__getRoleHead()
		if roleHead is None:
			roleHead = self.__teamHeads.values()[0]
		roleHead.left = 5.0
		roleHead.top = 5.0
		top = 0.0
		teamHeads = [teamHead for teamHead in self.__teamHeads.values() if teamHead.dbid != player.databaseID]
		pyLastHead = roleHead
		if  len( teamHeads ) > 0:
			for index, pyHead in enumerate( teamHeads ):
				if index == 0:
					pyHead.top = roleHead.bottom
				else:
					aboveHead = teamHeads[index-1]
					pyHead.top = top + aboveHead.height
				pyHead.left = roleHead.left
				top = pyHead.top
			pyLastHead = teamHeads[-1]
		self.__pyTeamPanel.height = pyLastHead.bottom
	
	def __getRoleHead( self ):
		"""
		��ȡ����Լ���ͷ��
		"""
		for dbid, pyHead in self.__teamHeads.items():
			if dbid == BigWorld.player().databaseID:
				return pyHead
	
	def __onDestransCountDown( self, time ):
		"""
		����ʱ
		"""
		self.__cancelcdTimer()
		self.__lastTime = time
		self.__cdTimId = Timer.addTimer( 0.0, 1.0, self.__countDown )
	
	def __countDown( self ):
		"""
		"""
		self.__lastTime -= 1.0
		if self.__lastTime > 0.0:
			self.__pyStCount.text = "%d"%int( self.__lastTime )
		else:
			self.__pyStCount.text = ""
			self.__cancelcdTimer()
	
	def __onDestransSievePoint( self, ponit ):
		"""
		ɫ�ӵ���
		"""
		self.__dicepoint = ponit
		self.__pyAnimDice.play()				#����ɫ�Ӷ���
		self.__pyBtnCast.enable = False
		if self.__delaycbid > 0:
			BigWorld.cancelCallback( self.__delaycbid )
		self.__delaycbid = BigWorld.callback( 3.0, Functor( self.__delaySetPoint, ponit ) )
	
	def __delaySetPoint( self, point ):
		"""
		��ʱ����ɫ�ӵ���
		"""
		player = BigWorld.player()
		self.__pyAnimDice.point = point
		self.__pyAnimDice.stop()
		player.endPlaySieveAnimation()
	
	def __onDestransMoveChess( self, dbid, step ):
		"""
		�ƶ���Ϣ
		"""
		roleMark = self.__roleMarks.get( dbid )
		if roleMark is None:return
		player = BigWorld.player()
		curStep = roleMark.step
		self.__cancelMoveCbid( dbid )
		if step == 0:							#�ص����,˲�䴫��ȥ
			pieceInfo = destransDatasLoader.getPieceInfo( self.__boardNum, step )
			if pieceInfo is None:return
			index = pieceInfo[0]
			pos = self.__getPicePos( index )
			roleMark.center = pos[0]
			roleMark.bottom = pos[1]
			roleMark.setStep( step )
			if dbid == player.databaseID:
				player.endMoveChess()
				self.__showMsg( index )
		else:
			self.__markMovecbids[dbid] = BigWorld.callback( 1.0, Functor( self.__moveToDestPiece, dbid, curStep, step ) )
	
	def __cancelMoveCbid( self, dbid ):
		"""
		ȡ��ĳ����һص�
		"""
		movecbid = self.__markMovecbids.get( dbid, 0 )
		if movecbid > 0:
			BigWorld.cancelCallback( movecbid )
			self.__markMovecbids[dbid] = 0
	
	def __moveToDestPiece( self, dbid, curStep, step ):
		"""
		�ƶ���Ŀ������
		"""
		roleMark = self.__roleMarks.get( dbid )
		if roleMark is None:return
		player = BigWorld.player()
		oldInfo = destransDatasLoader.getPieceInfo( self.__boardNum, curStep )
		if oldInfo is None:return
		oldPos = self.__getPicePos( oldInfo[0] )
		if curStep != step:
			if curStep > step:		#����
				curStep -= 1
			else:		#ǰ��
				curStep += 1
			newInfo = destransDatasLoader.getPieceInfo( self.__boardNum, curStep )
			newPos = self.__getPicePos( newInfo[0] )
			direction = self.__getMoveDirection( oldInfo[1], curStep )
			hdist = abs( newPos[0] - oldPos[0] )
			vdist = abs( newPos[1] - oldPos[1] )
			if direction == "left":
				roleMark.left -= hdist
			elif direction == "right":
				roleMark.left += hdist
			elif direction == "top":
				roleMark.top -= vdist
			else:
				roleMark.top += vdist
		else:					#����Ŀ��
			pieceInfo = destransDatasLoader.getPieceInfo( self.__boardNum, step )
			if pieceInfo is None:return
			index = pieceInfo[0]
			pos = self.__getPicePos( index )
			roleMark.center = pos[0]
			roleMark.bottom = pos[1]
			if dbid == player.databaseID:
				player.endMoveChess()
				self.__showMsg( index )
			roleMark.setStep( step )
			self.__cancelMoveCbid( dbid )
			return
		self.__markMovecbids[dbid] = BigWorld.callback( 1.0, Functor( self.__moveToDestPiece, dbid, curStep, step ) )
	
	def __getMoveDirection( self, piece, step ):
		"""
		����ƶ�����
		"""
		pieceInfo = destransDatasLoader.getPieceInfo( self.__boardNum, step )
		for dctFlag in ["left", "right", "top", "bottom"]:
			if piece[dctFlag] == 0:continue
			if pieceInfo[0] == piece[dctFlag]:
				return dctFlag
	
	def __onDestransToStart( self, dbid ):
		"""
		�ص����
		"""
		player = BigWorld.player()
		startStep = self.__getStartStep()
		pieceInfo = destransDatasLoader.getPieceInfo( self.__boardNum, startStep )
		if dbid == player.databaseID:
			player.endMoveChess()
			if pieceInfo:
				self.__showMsg( pieceInfo[0] )
		if startStep is None:return
		roleMark = self.__roleMarks.get( dbid )
		if roleMark is None:return
		if pieceInfo is None:return
		pos = self.__getPicePos( pieceInfo[0] )
		roleMark.center = pos[0]
		roleMark.bottom = pos[1]
	
	def __showMsg( self, index ):
		"""
		��ʾ��Ļ��Ϣ
		"""
		pyPiece = self.__pyPieces.get( index )
		if pyPiece is None:return
		evtid = pyPiece.evtid
		if evtid < 0:return
		describe = destransDatasLoader.getDescribe( self. __boardNum, index )
		if len(describe) < 0:return
		self.__pyMsgBox.showMsg( describe )
	
	def __onLivePointChanged( self, dbid, livePoint ):
		"""
		ʣ��������
		"""
		player = BigWorld.player()
		pyHead = self.__teamHeads.get( dbid, None )
		if pyHead is None:return
		pyHead.setLivePoint( livePoint )
		if dbid == player.databaseID:
			self.__pyBtnCast.enable = livePoint > 0
	
	def __onDestransWndClose( self, dispose ):
		"""
		�رս���
		"""
		if dispose:				#ȫ��ͨ�أ���������
			self.__resetPieceBoard()
		self.hide()
	
	def __onDestransMsgs( self, msgType ):
		"""
		ͨ����Ϣ
		"""
		msg = self._destans_msgs.get( msgType, "" )
		if msg == "":return
		self.__pyMsgBox.showMsg( msg, (255, 0, 0) )
	
	def __onMemberLeft( self, teammateID ):
		"""
		��Ա���
		"""
		player = BigWorld.player()
		if teammateID == player.id:return
		for dbid, roleMark in self.__roleMarks.items():
			if roleMark.entityID == teammateID:
				del self.__roleMarks[dbid]
				self.__pyPcsPanel.delPyChild( roleMark )
		for dbid, teamHead in self.__teamHeads.items():
			if teamHead.entityID == teammateID:
				del self.__teamHeads[dbid]
				self.__pyTeamPanel.delPyChild( teamHead )
	
	def __onResolutionChanged( self, preReso ):
		"""
		�ֱ��ʸı�
		"""
		self.__pyBoard.center = self.width/2.0
		self.__pyBoard.middle = self.height/2.0

	def __onCast( self, pyBtn ):
		if pyBtn is None:return
		player = BigWorld.player()
		self.__cancelcdTimer()
		self.__pyStCount.text = ""
		self.__lastTime = 0.0
		player.throwSieve()
	
	def __getStartStep( self ):
		"""
		��ȡ��ʼ����
		"""
		for index, pyPiece in self.__pyPieces.items():
			if pyPiece.evtid == 0:
				return index
	
	def __cancelcdTimer( self ):
		if self.__cdTimId > 0:
			Timer.cancel( self.__cdTimId )
			self.__cdTimId = 0
	
	def __onMouseEnter( self, pyPiece ):
		if pyPiece.evtid < 0:
			return
		describe = destransDatasLoader.getDescribe( self. __boardNum, pyPiece.index )
		toolbox.infoTip.showToolTips( pyPiece, describe )
	
	def __onMouseLeave( self, pyPiece ):
		if pyPiece is None:return
		toolbox.infoTip.hide()
	
	def __resetPieces( self ):
		"""
		��������
		"""
		for pyPiece in self.__pyPieces.values():
			pyPiece.resetPiece()
			pyPiece.onMouseEnter.unbind( self.__onMouseEnter )
			pyPiece.onMouseLeave.unbind( self.__onMouseLeave )
	
	def __resetPieceBoard( self ):
		"""
		��������
		"""
		self.__boardNum = -1
		for dbid in self.__roleMarks.keys():
			roleMark = self.__roleMarks.pop( dbid )
			self.__pyPcsPanel.delPyChild( roleMark )
		self.__roleMarks = {}				#��Ҳ���
		for dbid in self.__teamHeads.keys():
			pyHead = self.__teamHeads.pop( dbid )
			self.__pyTeamPanel.delPyChild( pyHead )
		self.__teamHeads = {}				#����ͷ��
		self.__cancelcdTimer()
		self.__resetPieces()
	# ----------------------------------------------------------------------
	# public
	# ----------------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )
	
	def onLeaveWorld( self ):
		self.__resetPieceBoard()
		self.hide()
	
	def onEnterWorld( self ):
		pass

	def show( self ):
		self.__pyBoard.center = self.width/2.0
		self.__pyBoard.middle = self.height/2.0
		RootGUI.show( self )
	
	def hide( self ):

		RootGUI.hide( self )