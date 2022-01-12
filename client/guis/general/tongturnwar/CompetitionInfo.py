#-*- coding: gb18030 -*-

import GUI
import csol
import math
from guis.common.RootGUI import RootGUI
from guis.common.GUIBaseObject import GUIBaseObject
from guis.controls.StaticText import StaticText
from guis.controls.Control import Control
from guis.UIFixer import uiFixer
from LabelGather import labelGather
from event import EventCenter as ECenter
from AbstractTemplates import Singleton
from guis.ExtraEvents import ControlEvent
from gbref import rds
from guis import util
import csconst

COLOR_GRAY = (110,110,110,255)				# 灰色

class CompetitionInfoPanel( RootGUI, Singleton ):

	def __init__( self ):
		gui = GUI.load("guis/general/tongturnwar/competition_info/panel.gui")
		uiFixer.firstLoadFix(gui)
		RootGUI.__init__( self, gui )
		self.addToMgr()
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "TOP"
		self.escHide_ = False
		self.__score = [0,0]			# 保存比赛积分
		self.__losers = set()			# 保存对决失败的竞争者
		self.__pyCompetitors = []		# 所有比赛选手
		self.__initialize(gui)

	def __initialize( self, gui ):
		# 标题栏
		self.__pyRoller = Roller( gui.title )
		self.__pyRoller.onExtended.bind( self.__onExtended )
		self.__pyRoller.onFurled.bind( self.__onFurled )
		self.__rollerAsTitle()
		# 积分栏
		self.__pyScore = Content( gui.score )
		labelGather.setPyLabel( self.__pyScore.stext1, "tongturnwar:competition_info", "score" )

	def __onUpdateCompetitors( self, teammates, opponents ):
		"""
		更新竞赛选手
		"""
		self.__clearContent()
		bottom = self.__pyRoller.bottom + 5
		for order, (tm, op) in enumerate(zip(teammates, opponents)):
			pyComp = Content()
			pyComp.stext1.text = ""
			#pyComp.stext1.text = str(order+1)
			#pyComp.stext1.left = 10
			pyComp.stext2.text = tm
			if tm in self.__losers:
				pyComp.stext2.color = COLOR_GRAY
			pyComp.stext3.text = op
			if op in self.__losers:
				pyComp.stext3.color = COLOR_GRAY
			self.addPyChild(pyComp)
			pyComp.top = bottom
			bottom = pyComp.bottom + 5
			self.__pyCompetitors.append(pyComp)
		self.__pyScore.top = bottom
		self.height = self.__pyScore.bottom
		self.show()

	def __clearContent( self ):
		"""
		清空竞赛选手的信息
		"""
		for pyComp in self.__pyCompetitors:
			self.delPyChild(pyComp)
		self.__pyCompetitors = []
		self.__pyScore.stext2.text = "0"
		self.__pyScore.stext3.text = "0"

	def __onAddScore( self, ourwin ):
		"""
		一场对决结束，根据输赢更新积分
		"""
		if ourwin :
			self.__score[0] = csconst.TONG_TURN_WIN_POINT
			self.__pyScore.stext2.text = str(csconst.TONG_TURN_WIN_POINT)
		else:
			self.__score[1] = csconst.TONG_TURN_WIN_POINT
			self.__pyScore.stext3.text = str(csconst.TONG_TURN_WIN_POINT)
		if self.__pyRoller.isFurled():
			self.__rollerAsScorer()

	def __onComptitorLose( self, name ):
		"""
		对决玩家输了
		"""
		self.__losers.add(name)
		for pyComp in self.__pyCompetitors:
			if self.__signLoser(pyComp, name):
				break

	def __signLoser( self, pyComp, name ):
		"""
		标记出失败的玩家
		"""
		if pyComp.stext2.text == name:
			pyComp.stext2.color = COLOR_GRAY
			return True
		elif pyComp.stext3.text == name:
			pyComp.stext3.color = COLOR_GRAY
			return True
		else:
			return False

	def __onFurled( self ):
		"""
		收起界面
		"""
		self.height = self.__pyRoller.bottom
		self.__rollerAsScorer()

	def __onExtended( self ):
		"""
		展开界面
		"""
		self.height = self.__pyScore.bottom
		self.__rollerAsTitle()

	def __rollerAsTitle( self ):
		"""
		起子充当标题
		"""
		self.__pyRoller.stext1.text = ""		# 不显示出战顺序，并始终将当前对决的玩家放在第一行
		#labelGather.setPyLabel( self.__pyRoller.stext1, "tongturnwar:competition_info", "title_order" )
		labelGather.setPyLabel( self.__pyRoller.stext2, "tongturnwar:competition_info", "title_teammate" )
		labelGather.setPyLabel( self.__pyRoller.stext3, "tongturnwar:competition_info", "title_opponent" )

	def __rollerAsScorer( self ):
		"""
		起子充当记分器
		"""
		labelGather.setPyLabel( self.__pyRoller.stext1, "tongturnwar:competition_info", "score" )
		labelGather.setPyLabel( self.__pyRoller.stext2, "tongturnwar:competition_info", "selfScore", self.__score[0] )
		labelGather.setPyLabel( self.__pyRoller.stext3, "tongturnwar:competition_info", "enemyScore", self.__score[1] )

	def onLeaveWorld( self ):
		self.dispose()
		self.__class__.releaseInst()

	@classmethod
	def onEvent( CLS, evtMacro, *args ):
		if evtMacro == "EVT_ON_CLOSE_COPY_INTERFACE":
			if CLS.insted:
				CLS.inst.dispose()
				CLS.releaseInst()
		elif evtMacro == "EVT_ON_TURNWAR_UPDATE_COMPETITORS":
			CLS.inst.__onUpdateCompetitors( *args )
		elif evtMacro == "EVT_ON_TURNWAR_ADD_SCORE":
			if CLS.insted:
				CLS.inst.__onAddScore( *args )
		elif evtMacro == "EVT_ON_TURNWAR_COMPETITOR_LOSE":
			if CLS.insted:
				CLS.inst.__onComptitorLose( *args )


ECenter.registerEvent("EVT_ON_TURNWAR_ADD_SCORE", CompetitionInfoPanel)
ECenter.registerEvent("EVT_ON_CLOSE_COPY_INTERFACE", CompetitionInfoPanel)
ECenter.registerEvent("EVT_ON_TURNWAR_UPDATE_COMPETITORS", CompetitionInfoPanel)
ECenter.registerEvent("EVT_ON_TURNWAR_COMPETITOR_LOSE", CompetitionInfoPanel)


class Content( GUIBaseObject ):

	def __init__( self, gui=None ):
		if gui is None:
			gui = GUI.load("guis/general/tongturnwar/competition_info/content.gui")
			uiFixer.firstLoadFix(gui)
		GUIBaseObject.__init__( self, gui )
		self.__pySText1 = StaticText(gui.st_content1)
		self.__pySText2 = StaticText(gui.st_content2)
		self.__pySText3 = StaticText(gui.st_content3)

	@property
	def stext1(self):
		return self.__pySText1

	@property
	def stext2(self):
		return self.__pySText2

	@property
	def stext3(self):
		return self.__pySText3


class Roller( Content, Control ):

	def __init__( self, gui ):
		Content.__init__(self, gui)
		Control.__init__(self, gui)
		self.focus = True
		self.moveFocus = True
		self.crossFocus = True
		self.__isFurled = False
		self.__mouseDownPos = (0,0)
		self.__mouseDownScreenPos = (0,0)
		# extra events
		self.__onExtended = ControlEvent("onExtended", self)
		self.__onFurled = ControlEvent("onFurled", self)

	def onLClick_( self, mod ):
		x1, y1 = self.__mouseDownScreenPos
		x2, y2 = csol.pcursorPosition()
		if math.fabs(x1 - x2) > 3.0 or math.fabs(y1 - y2) > 3.0:
			return True
		Control.onLClick_(self, mod)
		self.__isFurled = not self.__isFurled
		if self.__isFurled:
			self.onFurled_()
		else:
			self.onExtended_()
		return True

	def onLMouseDown_( self, mods ) :
		Control.onLMouseDown_( self, mods )
		if self.isMouseHit():
			rds.uiHandlerMgr.capUI( self )
			self.__mouseDownPos = self.pyParent.mousePos		# 记录下鼠标在父UI上的像素位置
			self.__mouseDownScreenPos = csol.pcursorPosition()
		return True

	def onLMouseUp_( self, mods ):
		Control.onLMouseUp_( self, mods )
		rds.uiHandlerMgr.uncapUI( self )						# 鼠标提起时释放 cap
		if rds.worldCamHandler.fixed() :
			rds.worldCamHandler.unfix()

	def onMouseMove_( self, dx, dy ) :
		if rds.uiHandlerMgr.getCapUI() == self :
			mx, my = csol.pcursorPosition()						# 获取鼠标屏幕上的像素位置
			self.pyParent.left = mx - self.__mouseDownPos[0]	# (水平方向窗口移到鼠标位置，不是鼠标移动的前后位置差)
			self.pyParent.top = my - self.__mouseDownPos[1]		#（垂直方向窗口移到鼠标位置，不是鼠标移动的前后位置差)
			Control.onMouseMove_( self, dx, dy )
			return True
		return Control.onMouseMove_( self, dx, dy )

	def onMouseEnter_( self ) :
		Control.onMouseEnter_(self)
		rds.ccursor.set("hand")

	def onMouseLeave_( self ):
		Control.onMouseLeave_(self)
		rds.ccursor.normal()

	def onFurled_( self ):
		self.onFurled()
		furlFlag = self.gui.furlflag
		furlFlag.size = (16, 8)
		util.setGuiState(furlFlag, (2,1), (1,1))
		furlFlag.size *= 2

	def onExtended_( self ):
		self.onExtended()
		furlFlag = self.gui.furlflag
		furlFlag.size = (16, 8)
		util.setGuiState(furlFlag, (2,1), (2,1))
		furlFlag.size *= 2

	def isFurled( self ):
		return self.__isFurled

	@property
	def onExtended( self ):
		return self.__onExtended

	@property
	def onFurled( self ):
		return self.__onFurled
