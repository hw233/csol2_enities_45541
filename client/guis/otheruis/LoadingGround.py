# -*- coding: gb18030 -*-
#
# $Id: LoadingGround.py,v 1.33 2008-08-26 02:21:16 huangyongwei Exp $

"""
implement loading background class
"""

import time
import random
import csdefine
import Define
import gbref
import event.EventCenter as ECenter
import GUIFacade
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.Frame import HFrame
from guis.common.RootGUI import RootGUI
from guis.controls.ProgressBar import HProgressBar
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from gbref import rds
from config.client.help import LoadingHints
from LoadingAnimation import loadingAnimation

class LoadingGround( RootGUI ) :
	__cc_fader_speed = 0.6

	__cc_backgrounds = {}
	__cc_backgrounds[( csdefine.GENDER_MALE, csdefine.CLASS_FIGHTER )]		= "nanzhanshi.dds"
	__cc_backgrounds[( csdefine.GENDER_FEMALE, csdefine.CLASS_FIGHTER )]	= "nvzhanshi.dds"
	__cc_backgrounds[( csdefine.GENDER_MALE, csdefine.CLASS_SWORDMAN )]		= "nanjianke.dds"
	__cc_backgrounds[( csdefine.GENDER_FEMALE, csdefine.CLASS_SWORDMAN )]	= "nvjianke.dds"
	__cc_backgrounds[( csdefine.GENDER_MALE, csdefine.CLASS_ARCHER )]		= "nangongshou.dds"
	__cc_backgrounds[( csdefine.GENDER_FEMALE, csdefine.CLASS_ARCHER )]		= "nvgongshou.dds"
	__cc_backgrounds[( csdefine.GENDER_MALE, csdefine.CLASS_MAGE )]			= "nanfashi.dds"
	__cc_backgrounds[( csdefine.GENDER_FEMALE, csdefine.CLASS_MAGE )]		= "nvfashi.dds"
	__cc_backgrounds[csdefine.ENTITY_CAMP_TAOISM] = "guis/loginuis/campselector/camp_bg_1.dds"
	__cc_backgrounds[csdefine.ENTITY_CAMP_DEMON]  = "guis/loginuis/campselector/camp_bg_2.dds"
	
	
	def __init__( self ) :
		wnd = GUI.load( "guis/otheruis/loadinggrounds/wnd.gui" )
		uiFixer.firstLoadFix( wnd ) #修正GUI的位置
		RootGUI.__init__( self, wnd )
		self.h_dockStyle = "HFILL"
		self.v_dockStyle = "VFILL"
		self.focus = True
		self.movable_ = False
		self.posZSegment = ZSegs.L3 #所在的层数
		self.activable_ = False
		self.escHide_ = False
		self.__initialize( wnd )
		self.__layout()

		self.__endCallback = None			# 临时变量，记录开始现实加载进度时传入的回调，在加载进度完毕后调用该回调
											# 因为进度条的进度是渐进的，所以实际进度值为 1 时，进度条的进度值还小于 1
											# 所以等到进度条的值为 1 时，再回调，告诉底层已经进度完毕，这样显得更加逼真
		self.__hideDelayCBID = 0			# 延时因此的 callbackID
		self.__triggers = {}

		#添加了场景切换信息提示 2008-08-02 spf
		self.__strTipInfos = []				#存放所有的信息提示(id,item)
		self.__lastTime = 0.0
		self.__registerTriggers()

	def __initialize( self, wnd ) :
		self.__fader = wnd.fader
		self.__fader.speed = self.__cc_fader_speed
		self.__fader.value = 0
		self.__fader.reset()

		self.__pyBg = PyGUI( wnd.bg )

		self.__pyBarBg = HFrame( wnd.bg.pbBg )
		self.__pyBarBg.h_dockStyle = "HFILL"
		self.__pyBarBg.v_dockStyle = "S_TOP"
		self.__pyPBar = DecorationProgerssBar( wnd.bg.pbBg.fb , wnd.bg.pbBg.pbPos  )
		self.__pyPBar.h_dockStyle = "HFILL"
		self.__pyPBar.speed = 10.0
		self.__pyPBar.reset( 0.0 )
		self.__pyPBar.onCurrentValueChanged.bind( self.__onPBCurrValueChanged )

		self.__pyLbPercent = StaticText( wnd.bg.pbBg.stProgress )
		self.__pyLbPercent.h_dockStyle = "CENTER"
		self.__pyLbPercent.text = "0%"

		self.__pyRTTips = CSRichText( wnd.bg.rtTips )
		self.__pyRTTips.top = self.__pyBarBg.top + 15
		self.__pyRTTips.center = self.width / 2
		self.__pyRTTips.h_dockStyle = "HFILL"
		self.__pyRTTips.v_dockStyle = "S_BOTTOM"
		self.__pyRTTips.align = "C"
		self.__pyRTTips.onTextChanged.bind( self.__onTipChanged )
		self.__lastTime = time.time()

		self.visible = False


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_RESOLUTION_CHANGED"] = self.__onResolutionChanged
		self.__triggers["EVT_ON_BEGIN_WORLD_LOADING"] = self.__onBeginLoading
		self.__triggers["EVT_ON_BEGIN_BACK_RS_LOADING"] = self.__onBeginLoading
		self.__triggers["EVT_ON_BREAK_LOADING"] = self.__onBreakLoading
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __layout( self ) :
		scSize = BigWorld.screenSize()							# 屏幕大小
		scScale = scSize[0] / scSize[1]							# 屏幕宽高比
		scale = self.__pyBg.width / self.__pyBg.height			# 宽高比
		if scScale < scale :
			self.__pyBg.width = scSize[0]
			self.__pyBg.height = scSize[0] / scale
		else :
			self.__pyBg.height = scSize[1]
			self.__pyBg.width = scSize[1] * scale
		self.__pyBg.center = scSize[0] / 2
		self.__pyBg.middle = scSize[1] / 2
		
	# -------------------------------------------------
	def __showProgress( self, progress ) :
		"""
		实时现实进度值
		"""
		self.__pyPBar.value = progress

	def __onPBCurrValueChanged( self, currValue ) :
		"""
		当进度条真实进度值改变时被调用
		"""
		self.__pyLbPercent.text = "%d%%" % ( currValue * 100 )
		if time.time() - self.__lastTime >= 8.0:
			self.__pyRTTips.text = self.__generateTipText()	#显示提示信息,每8秒变换一次 2008-08-01 spf
			self.__lastTime = time.time()
		if currValue < 1 : return
		if self.__endCallback is not None :
			self.__endCallback()
			self.__pyRTTips.text = ""
		self.__toggleVisible( False )

	# -------------------------------------------------
	def __onResolutionChanged( self, preReso ) :
		"""
		屏幕大小改变时，被调用
		"""
		self.__layout()

	def __onBeginLoading( self, resLoader, callback ) :
		"""
		开始加载
		"""
		self.__endCallback = callback
		self.__pyRTTips.text = self.__generateTipText()
		self.__lastTime = time.time()
		resLoader.setNotifier( self.__showProgress )
		rds.ccursor.lock( "wait" )							# 锁定鼠标
		self.show()

	def __onBreakLoading( self ) :
		if self.visible :
			self.__pyPBar.reset( self.__pyPBar.currValue )
			rds.ccursor.unlock( "wait", "normal" )			# 解除锁定鼠标

	# -------------------------------------------------
	def __toggleVisible( self, visible ) :
		if visible :
			self.show()
		else :
			self.__fader.value = 0
			self.__hideDelayCBID = BigWorld.callback( self.__cc_fader_speed, self.hide )

	# ---------------------------------------
	def __generateTipText( self ):	#随即生成不重复的信息提示 2008-08-020 spf
		if len(self.__strTipInfos)==0 :
			self.__strTipInfos = LoadingHints.Datas.values()				#存放所有的信息提示(id,item)
			random.shuffle( self.__strTipInfos)
		return self.__strTipInfos.pop()


	def __onTipChanged( self ) :
		"""
		当提示信息改变时被触发
		"""
		self.__pyRTTips.bottom = self.__pyBarBg.top + 18

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def afterStatusChanged( self, oldStatus, newStatus ) :
		if newStatus == Define.GST_LOGIN :
			self.__toggleVisible( False )

	# -------------------------------------------------
	def show( self ) :
		if loadingAnimation.isPlay:
			loadingAnimation.startLoadingAnimation()
			return
		BigWorld.cancelCallback( self.__hideDelayCBID )					# 如果在隐藏过程中，又显示，则取消隐藏
		self.__fader.value = 1
		self.__fader.reset()
		roleInfo = rds.gameMgr.getCurrRoleInfo()
		if roleInfo != None:
			self.__pyBg.size = 1024.0, 768.0
			gender = roleInfo.getGender()
			profession = roleInfo.getClass()
			if rds.statusMgr.isCurrStatus( Define.GST_SPACE_LOADING ) : 	# 如果是跳转，则加载另外的随机的图
				self.__pyBg.texture = "maps/teleport_grounds/g%02i.tga" % random.randint( 1, 21 )
			else:
				self.__pyBg.texture = "maps/loading_grounds/%s" % self.__cc_backgrounds[( gender, profession )]
		if rds.resLoader.isCreatorLoader():
			camp = rds.roleCreator.getCamp()
			self.__pyBg.size = 1280.0, 720.0
			self.__pyBg.texture = self.__cc_backgrounds[camp]
		util.setGuiState( self.__pyBg.gui, (1,1), (1,1) )
		self.__layout()
		RootGUI.show( self )

	def hide( self ) :
		rds.ccursor.unlock( "wait", "normal" )	# 设定鼠标为等待标志
		RootGUI.hide( self )
		self.__pyLbPercent.text = "0%"
		self.__pyPBar.reset( 0.0 )

# --------------------------------------------------------------------
# 带光点的进度条
# --------------------------------------------------------------------
class DecorationProgerssBar( HProgressBar ) :
	def __init__( self, pb, decoder ) :
		HProgressBar.__init__( self, pb )
		self.__pyDecoder = PyGUI( decoder )

	def onCurrProgressChanged_( self, value ) :
		HProgressBar.onCurrProgressChanged_( self, value )
		self.__pyDecoder.left = self.left + self.width * value - 50.0
