# -*- coding: gb18030 -*-
#
# $Id : FlyText.py,v 1.1 2006/09/20 09 :02 :40 panguankong Exp $

"""
implement damage text class
-- 2007/jan/08 : created by huangyw
"""


import time
import BigWorld
import GUI
from bwdebug import *
from Function import Functor
from guis import *
import event.EventCenter as ECenter
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from guis.common.RootGUI import RootGUI
from AbstractTemplates import Singleton
from guis.common.PyGUI import PyGUI
from NPCModelLoader import NPCModelLoader
from guis.ScreenViewer import ScreenViewer
from guis.common.FrameEx import VFrameEx
g_npcmodel = NPCModelLoader.instance()
import Language

class PortraitBase( RootGUI ):
	
	def __init__( self, bg, type ):
		RootGUI.__init__( self, bg )
		self.focus = False
		self.type = type
		self.__pyStName = StaticText( bg.stName )
		self.__pyStName.text = ""
		
		self.__pyHeader = PyGUI( bg.header )
		self.__pyHeader.texture = ""
		
		body = bg.body
		self.__pyBody = PyGUI( body )
		self.__pyBody.texture = ""

		
		self.pyRtMgs_ = CSRichText( bg.rtMsg )
		self.pyRtMgs_.align = "L"
		self.pyRtMgs_.text = ""

		self.__pyVFrameEx = VFrameEx( bg.bg )

		self.fader_ = bg.fader
		self.fader_.speed = 0.5
		self.fader_.value = 0
		self.fader_.reset()
		
		self.lastTime_ = 0.0						#持续时间
		self.flyCBID_ = 0							#fly的cbid
		self.middle = BigWorld.screenHeight()*0.67
		self.delayCBID_ = 0
		self.delta_ = 30.0
		self.speed = 90.0
		self.offset = 0.0
		self.isBody = False
		self.viewHeight = self.height
		self.addToMgr()

	# ---------------------------------------------------------------
	# public:
	# ---------------------------------------------------------------
	def dispose( self ) :
		RootGUI.dispose( self )
	
	def startFly( self, nameText, headTexture, text, lastTime, isBody ):
		RootGUI.show( self )
		self.isBody = isBody
		self.pyRtMgs_.text = text
		if self.pyRtMgs_.height > 55.0:	# 文字超出范围
			self.__pyVFrameEx.height = self.pyRtMgs_.height + 30.0
			self.height = self.__pyVFrameEx.bottom
		self.__pyStName.text = nameText
		if isBody:
			self.offset = 40.0
			self.__pyBody.visible = True
			self.__pyHeader.visible = False
			self.__pyBody.texture = headTexture
			self.viewHeight = self.height
			if self.type == 0:
				self.__pyStName.left = self.__pyBody.right + 5.0
			else:
				self.__pyStName.right = self.__pyBody.left - 5.0
				body = self.__pyBody.gui
				mapping = body.mapping
				body.mapping = util.hflipMapping( mapping )
		else:
			self.offset = 60.0
			self.__pyBody.visible = False
			self.__pyHeader.visible = True
			self.__pyHeader.texture = ""
			self.viewHeight = self.height - self.__pyHeader.top + 5.0
			if self.type == 0:
				self.__pyStName.left = self.__pyHeader.right + 5.0
			else:
				header = self.__pyHeader.gui
				mapping = header.mapping
				header.mapping = util.hflipMapping( mapping )
				self.__pyStName.right = self.__pyHeader.left - 5.0
		self.lastTime_ = lastTime

	def cancelFly( self, callback ):
		BigWorld.cancelCallback( self.flyCBID_ )
		self.flyCBID_ = 0
		self.fader_.value = 1.0
		BigWorld.cancelCallback( self.delayCBID_ )
		self.delayCBID_ = BigWorld.callback( self.lastTime_, Functor( self.delay, callback ) )
		
	def delay( self, callback ) :
		self.fader_.value = 0
		self.delayCBID_ = BigWorld.callback( self.fader_.speed, Functor( self.hide, callback ) )

	def isMouseHit( self ) :
		return False

	def onLClick_( self,mods ):
		if not self.isMouseHit() : 
			return False
		RootGUI.onLClick_( self,mods )
		return True
	
	def hide( self, callback ):
		RootGUI.hide( self )
		self.dispose()
		self.lastTime_ = 0.0
		self.flyCBID_ = 0
		self.delayCBID_ = 0
		if callable( callback ):
			callback()
		rds.ruisMgr.portraitDriver.onHeadPortraiDisPosed( self )
	
	def onResolutionChanged( self, preReso ):
		"""
		"""
		pass

# -----------------------------------------------------------------------------
class PortraitLeft( PortraitBase ):
	"""
	头像在左边
	"""
	
	def __init__( self, bg, type ):
		PortraitBase.__init__( self, bg, type )
		self.right = 0.0
	
	def startFly( self, nameText, headTexture, text, lastTime, isBody, callback ):
		PortraitBase.startFly( self, nameText, headTexture, text, lastTime, isBody )
		self.flyCBID_ = BigWorld.callback( 0.0, Functor( self.__startFly, callback ) )
	
	def __startFly( self, callback ):
		dist = ( BigWorld.screenWidth()*0.5 - self.offset ) - self.center
		if dist <= self.speed:
			self.center = BigWorld.screenWidth()*0.5 - self.offset
			self.cancelFly( callback )
			return
		self.speed += self.delta_
		self.center += self.speed
		self.fader_.value += 0.1
		self.lastTime_ -= 0.01
		self.flyCBID_ = BigWorld.callback( 0.01, Functor( self.__startFly, callback ) )

	def onResolutionChanged( self, preReso ):
		"""
		"""
		self.center = BigWorld.screenWidth()*0.5 - self.offset

class PortraitRight( PortraitBase ):
	"""
	头像在右边
	"""
	def __init__( self, bg, type ):
		PortraitBase.__init__( self, bg, type )
		self.left = BigWorld.screenWidth()

	def startFly( self, nameText, headTexture, text, lastTime, isBody, callback ):
		PortraitBase.startFly( self, nameText, headTexture, text, lastTime, isBody )
		self.flyCBID_ = BigWorld.callback( 0.0, Functor( self.__startFly, callback ) )

	def __startFly( self, callback ):
		dist = self.center - ( BigWorld.screenWidth()*0.5 + self.offset )
		if dist <= self.speed:
			self.center = BigWorld.screenWidth()*0.5 + self.offset
			self.cancelFly( callback )
			return
		self.speed += self.delta_
		self.center -= self.speed
		self.fader_.value += 0.1
		self.lastTime_ -= 0.01
		self.flyCBID_ = BigWorld.callback( 0.01, Functor( self.__startFly, callback ) )

	def onResolutionChanged( self, preReso ):
		"""
		"""
		self.center = BigWorld.screenWidth()*0.5 + self.offset
	
# --------------------------------------------------------------------
# implement receiver manager
# --------------------------------------------------------------------

class PortraitDriver( object ):
	
	__cc_receivers		= 2											# 消息窗口数量
	__cc_headbody_config = "config/client/HeadPortraitBody.xml"
	
	__CLS_MAP = {0:PortraitLeft, 1:PortraitRight}
	__HEAD_CONFIG = ""

	def __init__( self ):
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyPortraits = {}
		self.__modelNums = []
		section = Language.openConfigSection( self.__cc_headbody_config )
		if section:
			for key, subSect in section.items():
				modelNum = subSect["modelNumber"].asString
				if modelNum in self.__modelNums:continue
				self.__modelNums.append( modelNum )
		

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_SHOW_HEAD_PORTRAIT_AND_TEXT"] = self.__onShowHeadPortrail
		self.__triggers["EVT_ON_ROLE_LEAVE_WORLD"] = self.onLeaveWorld
		self.__triggers["EVT_ON_RESOLUTION_CHANGED"] = self.__onResolutionChanged
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )
	
	def __onShowHeadPortrail( self, type, monsterName, headTextureID, text, lastTime, callback = None ):
		"""
		显示头像
		"""
		path = "guis/otheruis/headportrait/%s.gui"
		CLS = self.__CLS_MAP.get( type, None )
		if type == 0:								#头像在左边
			path = path%"head_left"
		else:
			path = path%"head_right"
		item = GUI.load( path )
		uiFixer.firstLoadFix( item )
		if CLS is None:return
		pyPortrait = CLS( item, type )
		
		# 添加清屏例外窗口
		ScreenViewer().addResistHiddenRoot( pyPortrait )
		if type in self.__pyPortraits:
			self.__pyPortraits[type].append( pyPortrait )
		else:
			self.__pyPortraits[type] = [pyPortrait]
		headTexture = ""
		nameText = ""
		isBody = False
		player = BigWorld.player()
		if len( monsterName ) <= 0:
			nameText = player.getName()
		else:
			nameText = monsterName
		if len( headTextureID ) <= 0:						#玩家自己头像
			headTexture = player.getHeadTexture()
		else:
			headTexture = g_npcmodel.getHeadTexture( headTextureID )
			if headTextureID in self.__modelNums:
				isBody = True
				headTexture = "maps/npc_body/%s.dds"%headTextureID
		pyPortrait.startFly( nameText, headTexture, text, lastTime, isBody, callback )
		self.__layoutPortraits( pyPortrait )
	
	def __layoutPortraits( self, pyPortrait ):
		"""
		重新排序头像
		"""
		type = pyPortrait.type
		optype = 0
		if type == 0:
			optype = 1
		else:
			optype = 0
		portraits = self.__pyPortraits.get( type, [] )
		opPortraits = self.__pyPortraits.get( optype, [] )
		if opPortraits and len( opPortraits ) > 0:
			for opPortrait in opPortraits:
				if pyPortrait.top == opPortrait.top:
					pyPortrait.top -= pyPortrait.viewHeight
		if portraits and len( portraits ) > 1:
			pyPortrait.top -= ( len( portraits ) - 1 )*pyPortrait.viewHeight

	def __onResolutionChanged( self, preReso ):
		"""
		分辨率改变
		"""
		for type in self.__pyPortraits:
			pyPortraits = self.__pyPortraits.get( type, [] )
			for pyPortrait in pyPortraits:
				if not pyPortrait.visible:continue
				pyPortrait.onResolutionChanged( preReso )
	
	def onHeadPortraiDisPosed( self, headPortrait ):
		"""
		头像销毁时被调用
		"""
		type = headPortrait.type
		headPortraits = self.__pyPortraits.get( type, [] )
		if headPortraits and headPortrait in headPortraits:
			curIndex = headPortraits.index( headPortrait )
			bottom = headPortrait.bottom
			for index, pyPortrait in enumerate( headPortraits ):
				if index > curIndex:
					pyPortrait.bottom = bottom
					bottom = pyPortrait.top
			headPortraits.remove( headPortrait )
		if len( headPortraits ) <= 0:
			del self.__pyPortraits[type]

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )
	
	def onLeaveWorld( self, role ):
		if role != BigWorld.player() :
			return
