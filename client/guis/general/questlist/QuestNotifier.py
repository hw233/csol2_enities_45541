# -*- coding: gb18030 -*-

#bigworld
import GUI
import BigWorld

#client
import GUIFacade
import event.EventCenter as ECenter
from LabelGather import labelGather
from guis.UIFixer import uiFixer
from guis.Toolbox import toolbox
from guis.common.RootGUI import RootGUI


class FlashMgr :

	def __init__( self ) :
		shader = GUI.AlphaShader()
		shader.value = 0
		shader.speed = 0.3
		self.__shader = shader
		self.__flash_cbid = 0
		self.__counter = 0

	def __flash( self ) :
		"""开始闪烁"""
		self.__stopFlash()
		cbtime, value = ( 0.5, 0 ) if self.__shader.value else ( 0.8, 1 )
		self.__shader.value = value
		self.__flash_cbid = BigWorld.callback( cbtime, self.__flash )

	def __stopFlash( self ) :
		"""停止闪烁"""
		if self.__flash_cbid :
			BigWorld.cancelCallback( self.__flash_cbid )
			self.__flash_cbid = 0

	def incCounter( self ) :
		"""计数器增加"""
		if self.__counter == 0 :
			self.__flash()
		self.__counter += 1

	def decCounter( self ) :
		"""计数器减少"""
		self.__counter -= 1
		if self.__counter == 0 :
			self.__stopFlash()
		elif self.__counter < 0 :
			self.__counter = 0

	def bindFlasher( self, guiObj ) :
		"""绑定闪光物件"""
		guiObj.addShader( self.__shader, "alphaShader" )

flashMgr = FlashMgr()


class NotifierBase( RootGUI ) :
	"""任务提示器"""

	def __init__( self, gui ) :
		RootGUI.__init__( self, gui )
		flashMgr.bindFlasher( gui )
		self.movable_ = False
		self.escHide_ = False
		self.crossFocus = True
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "BOTTOM"
		self.addToMgr()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def notify_( self ) :
		flashMgr.incCounter()
		self.show()

	def shutdown_( self ) :
		flashMgr.decCounter()
		self.hide()


class NewQuestNotifier( NotifierBase ) :
	"""任务提示器"""

	def __init__( self ) :
		gui = GUI.load( "guis/general/questlist/questnotifier/NewQuestNotifier.gui" )
		uiFixer.firstLoadFix( gui )
		NotifierBase.__init__( self, gui )
		self.__triggerId = None
		self.__triggers = []

	def __showNextTip( self ) :
		if len( self.__triggers ) == 0 :
			self.shutdown_()
			self.__triggerId = None
		else :
			triggerId = self.__triggers[0]
			self.__triggerId = triggerId

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------2
	def onMouseEnter_( self ) :
		"""鼠标进入"""
		tip = labelGather.getText( "QuestHelp:notify", "newQuest",\
			len( self.__triggers ) )
		toolbox.infoTip.showToolTips( self, tip )
		return NotifierBase.onMouseEnter_( self )

	def onMouseLeave_( self ) :
		"""鼠标离开"""
		toolbox.infoTip.hide()
		return NotifierBase.onMouseLeave_( self )

	def onLClick_( self, mode ) :
		"""左键点击"""
		NotifierBase.onLClick_( self, mode )
		BigWorld.player().cell.onQuestTrapTipClicked( self.__triggerId )
		self.shutdown( self.__triggerId )
		return True

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onLeaveWorld( self ) :
		"""离开游戏"""
		self.__triggerId = None
		self.__triggers = []
		self.shutdown_()

	def notify( self, triggerId ) :
		"""闪烁提示玩家"""
		if triggerId in self.__triggers : return
		self.__triggers.append( triggerId )
		if self.__triggerId is None :
			self.__triggerId = triggerId
			self.notify_()

	def shutdown( self, triggerId ) :
		"""关闭提示"""
		if triggerId not in self.__triggers : return
		self.__triggers.remove( triggerId )
		if self.__triggerId == triggerId :
			self.__showNextTip()


class CommitNotifier( NotifierBase ) :
	"""任务完成提示"""

	def __init__( self ) :
		gui = GUI.load( "guis/general/questlist/questnotifier/CommitNotifier.gui" )
		uiFixer.firstLoadFix( gui )
		NotifierBase.__init__( self, gui )
		self.__currQuestId = None
		self.__quests = []

	def __showNextTip( self ) :
		if len( self.__quests ) == 0 :
			self.shutdown_()
			self.__currQuestId = None
		else :
			questId = self.__quests.pop( 0 )
			self.__quests.append( questId )							# 循环显示
			self.__currQuestId = questId

	def onMouseEnter_( self ) :
		"""鼠标进入"""
		tip = labelGather.getText( "QuestHelp:notify", "commitQuest", \
			len( self.__quests ) )
		toolbox.infoTip.showToolTips( self, tip )
		return NotifierBase.onMouseEnter_( self )

	def onMouseLeave_( self ) :
		"""鼠标离开"""
		toolbox.infoTip.hide()
		return NotifierBase.onMouseLeave_( self )

	def onLClick_( self, mode ) :
		"""左键点击"""
		NotifierBase.onLClick_( self, mode )
		GUIFacade.setQuestLogSelect( self.__currQuestId )
		ECenter.fireEvent( "EVT_ON_SHOW_QUEST_WINDOW" )
		self.__showNextTip()
		return True

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onLeaveWorld( self ) :
		"""离开游戏"""
		self.__currQuestId = None
		self.__quests = []
		self.shutdown_()

	def notify( self, questId ) :
		"""闪烁提示玩家"""
		if questId in self.__quests : return
		self.__quests.append( questId )
		if self.__currQuestId is None :
			self.__currQuestId = questId
			self.notify_()

	def shutdown( self, questId ) :
		"""关闭提示"""
		if questId not in self.__quests : return
		self.__quests.remove( questId )
		if self.__currQuestId == questId :
			self.__showNextTip()
