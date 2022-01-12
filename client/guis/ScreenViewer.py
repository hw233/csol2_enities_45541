# -*- coding: gb18030 -*-

"""
��Ļ��ʼ��
"""

import re
import Math
import csol
import csdefine
import Const
import csconst
import utils
import StringFormat
import event.EventCenter as ECenter
from AbstractTemplates import Singleton
from Function import Functor
from cscustom import Rect
from Helper import uiopHelper, pixieHelper
from guis import *
from guis.common.RootGUI import RootGUI
from guis.tooluis.CSRichText import CSRichText
from guis.common.PyGUI import PyGUI
from Weaker import WeakList
import Define
import config.client.labels.GUIFacade as lbDatas
# --------------------------------------------------------------------
# ��Ļ UI ������
# --------------------------------------------------------------------
class ScreenViewer( Singleton ) :
	def __init__( self ) :
		# ��/�ر����н���
		self.__isEmptyScreen = False				# �Ƿ�������״̬

		# ����ʱ���ԵĴ���
		self.__pyRootsResistHidden = WeakList()

		# �����̼��ƶ���ɫ��ʾ
		self.__rolePos = Math.Vector3()				# ��ɫ��һ����λ��
		self.__pyWalkGuiders = None					# ����ָʾ��
		self.__roleMoveTriggers = {}

		# ���ѡ��Ŀ����ʾ
		self.__entityFocusTipID = 0x0060			# ѡ�� entity �Ĳ�����ʾ
		self.__entityFocusTriggers = {}				# ѡ�� entity ����Ҫ�ĸ����¼�

		# ��ι���Ŀ����ʾ
		self.__attackTipID = 0x0061					# ������ʾ id
		self.__attackTriggers = {}					# ���� entity ����ĸ����¼�
		self.__moveAttickTipCBID = 0				# �ƶ�������ʾ��Ļص� id

		# ʰȡ����������ʾ
		self.__pickupTipID = 0x0070					# ʰȡ��ʾ id
		self.__pickupTriggers = {}					# ʰȡ��ʾ����¼�
		self.__droppedBoxID = 0 					# �������ӵ� id
		self.__movePickupTipCBID = 0				# �ƶ�������ʾ��Ļص� id

		# ������ʾ
		self.__scenaioShowTime = 2.0				# ÿһ����ʾ����ʱ
		self.__scenaioHideTime = 3.0				# ��ʾ��Ϻ󣬶��������ʧ
		self.__rtScenaio = None						# ��һ������Ϊ���ڶ�������Ϊ
		self.__rtScenaio2 = None					# ������ʾ��ʽ2
		self.__rtScenaio3 = None					# ȫ��Ļ��Ļ����
		self.__cb	  = None					#�ص�

		self.__rtScenaio4 = None
		self.__cb4 = None

		self.__rtScenaio5 = []
		self.__cb5 = None

		self.__pyScreenFader = None					# ��Ļalpha˥����
		self.__pyDangerWarning = None				# ��Ļ��˸����
		self.__scenarioTriggers = {}				# ������ʾ����¼�
		self.__pyChangeUIEffect = None				# ��Ļ��UIЧ�����
		self.__registerScenarioEvents()
		self.__hideByShortCut = False  #��ݼ����� ����CTR+G
#		UIOSentinel().attach( 0x0002, self.__showWalkGuider )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerRoleMoveEvents( self ) :
		"""
		ע���ɫ�ƶ���ʾ����ĸ����¼�
		"""
		self.__roleMoveTriggers["EVT_ON_RESOLUTION_CHANGED"] = self.__onResolutionChangedForRoleMove
		for key in self.__roleMoveTriggers :
			ECenter.registerEvent( key, self )

	def __registerEntityFocusEvents( self ) :
		"""
		ע��ѡ�� entity ����ĸ����¼�
		"""
		self.__entityFocusTriggers["EVT_ON_ENTITY_GOT_FOCUS"] = self.__onEntityGotFocus
		self.__entityFocusTriggers["EVT_ON_TARGET_BINDED"] = self.__onEntityBindedForFocus
		for key in self.__entityFocusTriggers :
			ECenter.registerEvent( key, self )

	def __registerAttackEvents( self ) :
		"""
		ע�ṥ�� entity ��ʾ������¼�
		"""
		self.__attackTriggers["EVT_ON_TARGET_BINDED"] = self.__onEntityBinded
		self.__attackTriggers["EVT_ON_TARGET_UNBINDED"] = self.__onEntityUnbinded
		self.__attackTriggers["EVT_ON_ATTACK_STATE_CHANGTED"] = self.__onAttackStateChanged
		for key in self.__attackTriggers :
			ECenter.registerEvent( key, self )

	def __registerPickupEvents( self ) :
		"""
		ע��ʰȡ��ʾ�¼�
		"""
		self.__pickupTriggers["EVT_ON_ITEM_DROPPED"] = self.__onItemDropped
		self.__pickupTriggers["EVT_ON_ITEM_PICKUP"] = self.__onItemPickup
		for key in self.__pickupTriggers :
			ECenter.registerEvent( key, self )

	def __registerScenarioEvents( self ) :
		"""
		ע�������ʾ����¼�
		"""
		self.__scenarioTriggers["EVT_ON_SHOW_SCENARIO_TIPS"] = self.__onShowScenarioTips
		self.__scenarioTriggers["EVT_ON_SHOW_SCENARIO_TIPS2"] = self.__onShowScenarioTips2
		self.__scenarioTriggers["EVT_ON_INTERRUPT_SCENARIO_TIPS2"] = self.__onInterruptScenarioTips2
		self.__scenarioTriggers["EVT_ON_SHOW_SCENARIO_TIPS3"] = self.__onShowScenarioTips3	#ȫ����Ļ�¼�add by wuxo 2011-9-6
		self.__scenarioTriggers["EVT_ON_SHOW_SCENARIO_TIPS4"] = self.__onShowScenarioTips4	#��Ļ�·�������Ļ add by wuxo 2012-3-19
		self.__scenarioTriggers["EVT_ON_SHOW_SCENARIO_TIPS5"] = self.__onShowScenarioTips5	#��Ӱ��Ļ add by wuxo 2012-8-14
		self.__scenarioTriggers["EVT_ON_INTERRUPT_SCENARIO_TIPS4"] = self.__onInterruptScenarioTips4
		self.__scenarioTriggers["EVT_ON_INTERRUPT_SCENARIO_TIPS5"] = self.__onInterruptScenarioTips5
		self.__scenarioTriggers["EVT_ON_SCREENBLUR_END"]      = self.__onEndScreenBlur	     #����ȫ��ģ��
		self.__scenarioTriggers["EVT_ON_VISIBLE_ROOTUIS"] = self.__setRootsVisible
		self.__scenarioTriggers["EVT_ON_BRIGHTEN_SCREEN"] = self.__onBrightenScreen
		self.__scenarioTriggers["EVT_ON_BLACKEN_SCREEN"] = self.__onBlackenScreen     #��Ļ��ɫ�¼�
		self.__scenarioTriggers["EVT_ON_FLICKER_SCREEN"] = self.__onFlickerScreen     #��Ļ�ܱ���˸����
		self.__scenarioTriggers["EVT_ON_RESTORE_SCREEN"] = self.__onRestoreScreen     #��Ļ�ܱ���˸�ָ�
		self.__scenarioTriggers["EVT_ON_START_CHANGE_UI_EFFECT"] = self.__onStartChangeUIEffect		#��ʼ��Ļ��UIЧ��
		self.__scenarioTriggers["EVT_ON_STOP_CHANGE_UI_EFFECT"] = self.__onStopChangeUIEffect		#������UIЧ��

		for key in self.__scenarioTriggers :
			ECenter.registerEvent( key, self )

	# ---------------------------------------
	def __deregisterEvents( self, triggers ) :
		"""
		ע��ѡ�� entity ����ĸ����¼�
		"""
		for key in triggers :
			ECenter.unregisterEvent( key, self )
		triggers.clear()


	# -------------------------------------------------
	# ����
	# -------------------------------------------------
	def __setRootsVisible( self, visible ) :
		"""
		�������д����Ƿ�ɼ�
		"""
		if BigWorld.player().__class__.__name__ != "PlayerRole":
			return 
		self.__isEmptyScreen = visible
		self.__toggleAllRoots()
		BigWorld.player().pointReviveClew()

	def __toggleAllRoots( self ) :
		"""
		��ʾ/�������е�ǰ��ʾ�Ĵ���( ���� )
		"""
		for pyRoot in rds.ruisMgr.getVSRoots() :				# �������е�ǰ�ɼ��Ĵ���
			if pyRoot not in self.__pyRootsResistHidden:
				pyRoot.getGui().visible = self.__isEmptyScreen		# ������ɼ���
		self.__isEmptyScreen = not self.__isEmptyScreen
		return True

	def __toggleAllRootsByShortCut( self ):
		"""
		��ʾ/�������е�ǰ��ʾ�Ĵ���( ���� )��ݼ�����
		"""
		self.__hideByShortCut = not self.__isEmptyScreen
		for pyRoot in rds.ruisMgr.getVSRoots() :				# �������е�ǰ�ɼ��Ĵ���
			if pyRoot not in self.__pyRootsResistHidden:
				pyRoot.getGui().visible = self.__isEmptyScreen		# ������ɼ���
		self.__isEmptyScreen = not self.__isEmptyScreen
		BigWorld.player().pointReviveClew()
		if rds.statusMgr.isOffline():
			rds.statusMgr.changeStatus( Define.GST_OFFLINE )
		return True

	def getHideByShortCut( self ):
		return self.__hideByShortCut

	# -------------------------------------------------
	# ��Ϸ��ĻЧ������
	# -------------------------------------------------
	def __onBrightenScreen( self ) :
		"""
		ʹ��Ļ�ӱ�ɫ״̬�ָ�������״̬
		"""
		if not self.__pyScreenFader : return
		self.__pyScreenFader.fadeout()
		def callback() :
			if not self.__pyScreenFader : return
			self.__pyScreenFader.dispose()
			self.__pyScreenFader = None
		BigWorld.callback( self.__pyScreenFader.fadeSpeed, callback )

	def __onBlackenScreen( self, colour = None, time = -1 ) :
		"""
		ʹ��Ļ��ɫ,Ĭ��Ϊ���
		@type 	colour: list or tuple
		@param  colour: RGB(����alphaֵ��4λ)
		"""
		if self.__pyScreenFader : return							# �Ѿ����ڱ�ɫ״̬
		self.__pyScreenFader = ScreenFader()
		if colour != None :
			self.__pyScreenFader.gui.colour.set( colour )
		self.__pyScreenFader.fadein()
		if time > 0 :
			hold_time = self.__pyScreenFader.fadeSpeed + time
			BigWorld.callback( hold_time, self.__onBrightenScreen )

	def __onFlickerScreen( self, colour = None ) :
		"""
		��Ļ������˸,Σ�վ���
		"""
		if self.__pyDangerWarning : return
		self.__pyDangerWarning = DangerWarning()
		if colour != None :
			self.__pyDangerWarning.gui.colour.set( colour )
		self.__pyDangerWarning.fadein()

	def __onRestoreScreen( self ) :
		"""
		��Ļ��˸�ָ�
		"""
		if not self.__pyDangerWarning : return
		self.__pyDangerWarning.fadeout()
		if not self.__pyDangerWarning : return
		self.__pyDangerWarning.dispose()
		self.__pyDangerWarning = None

	def __onStartChangeUIEffect( self ):
		if self.__pyChangeUIEffect:return
		self.__isEmptyScreen = False
		self.__toggleAllRoots()

		self.__pyChangeUIEffect = ChangeUIEffect()
		self.__pyChangeUIEffect.show()

	def __onStopChangeUIEffect( self ):
		if not self.__pyChangeUIEffect:return
		self.__isEmptyScreen = True
		self.__toggleAllRoots()
		self.__pyChangeUIEffect.hide()
		self.__pyChangeUIEffect.dispose()
		self.__pyChangeUIEffect = None
	# -------------------------------------------------
	# �����ɫ�ƶ�������ʾ
	# -------------------------------------------------
	def __showWalkGuider( self, uioKey ) :
		"""
		��ʾ��ɫ�ƶ�ָʾ
		"""
		tTips = uiopHelper.getTips( 0x0001 )		# ��ǰ�ƶ���ʾ
		if tTips is None : return
		lTips = uiopHelper.getTips( 0x0002 )		# �����ƶ���ʾ
		bTips = uiopHelper.getTips( 0x0003 )		# �����ƶ���ʾ
		rTips = uiopHelper.getTips( 0x0004 )		# �����ƶ���ʾ
		pyLGuider = WalkGuider( "L", lTips.text )
		pyLGuider.left = 0
		pyLGuider.r_middle = 0
		pyRGuider = WalkGuider( "R", rTips.text )
		pyRGuider.r_right = 1
		pyRGuider.r_middle = 0
		pyTGuider = WalkGuider( "T", tTips.text )
		pyTGuider.top = 0
		pyTGuider.r_center = 0
		pyBGuider = WalkGuider( "B", bTips.text )
		pyBGuider.r_center = 0
		pyBGuider.r_bottom = -1
		self.__pyWalkGuiders = ( pyLGuider, pyRGuider, pyTGuider, pyBGuider )

		WalkGuider.flash()
		self.__detectRolePos()

	def __hideWalkGuider( self ) :
		"""
		���ؽ�ɫ�ƶ�ָʾ
		"""
		WalkGuider.unflash()
		if not self.__pyWalkGuiders : return
		for pyGuider in self.__pyWalkGuiders :
			pyGuider.dispose()
		self.__pyWalkGuiders = None
		self.__deregisterEvents( self.__roleMoveTriggers )

	def __detectRolePos( self ) :
		"""
		����ɫλ��
		"""
		rolePos = BigWorld.player().position
		if rolePos.distTo( self.__rolePos ) > 0.5 :					# ��ɫ�뿪ԭ�� 0.5 �ף�����Ϊ�������ƶ�
			BigWorld.callback( 3.0, self.__hideWalkGuider )
		else :
			BigWorld.callback( 1.0, self.__detectRolePos )

	def __onResolutionChangedForRoleMove( self, preReso ) :
		"""
		��Ļ�ֱ��ʸı�ʱ������
		"""
		if self.__pyWalkGuiders is None : return
		self.__pyWalkGuiders[0].r_middle = 0
		self.__pyWalkGuiders[1].r_right = 1
		self.__pyWalkGuiders[1].r_middle = 0
		self.__pyWalkGuiders[2].r_center = 0
		self.__pyWalkGuiders[2].r_top = 1
		self.__pyWalkGuiders[3].r_center = 0
		self.__pyWalkGuiders[3].r_bottom = -1

	# -------------------------------------------------
	# ��������ƶ��� entity ����ʱ����ʾ
	# -------------------------------------------------
	def __moveEntityGetFocusTips( self, dx, dy, dz ) :
		"""
		��������ƶ�ʵ���ý������ʾ
		"""
		mpos = Math.Vector2( csol.pcursorPosition() ) - ( 25, 25 )
#		toolbox.infoTip.moveOperationTips( self.__entityFocusTipID, mpos )

	def __hideEntityGetFocusTips( self ) :
		"""
		����ʵ���ý�����ʾ
		"""
#		toolbox.infoTip.hideOperationTips( self.__entityFocusTipID )
		LastMouseEvent.detach( self.__moveEntityGetFocusTips )
		self.__deregisterEvents( self.__entityFocusTriggers )

	def __onEntityGotFocus( self, entID ) :
		"""
		����ƶ���ĳ�� entity ����ʱ����ʾ������ʾ
		"""
		entity = BigWorld.entity( entID )
		if entity.getEntityType() not in csconst.ENTITIES_CAN_BE_SELECTED or \
			entity is BigWorld.player() :
				return
		mx, my = csol.pcursorPosition()
		bound = Rect( ( mx - 25, my - 25 ), ( 50, 50 ) )
#		toolbox.infoTip.showOperationTips( self.__entityFocusTipID, bound = bound )
		LastMouseEvent.attach( self.__moveEntityGetFocusTips )
		BigWorld.callback( 5.0, self.__hideEntityGetFocusTips )

	def __onEntityBindedForFocus( self, target ) :
		"""
		ѡ��ĳ�� entity ʱ������
		"""
		self.__hideEntityGetFocusTips()

	# -------------------------------------------------
	# ����ѡ�й���ʱ��������ι�������ʾ
	# -----------------------------------------------

	def __onEntityBinded( self, target ) :
		"""
		ѡ��ĳ�� entity ʱ������
		"""
		pass

	def __onEntityUnbinded( self, target ) :
		"""
		ȡ��ѡ��ĳ�� entity ʱ������
		"""
		self.__hideAttackTips()

	def __onAttackStateChanged( self, state ) :
		"""
		��ɫ�Ĺ���״̬�ı�ʱ������
		"""
		if state != Const.ATTACK_STATE_NONE :
			self.__hideAttackTips()

	def __hideAttackTips( self ) :
		"""
		���ع���Ŀ�������ʾ
		"""
#		toolbox.infoTip.hideOperationTips( self.__attackTipID )
		BigWorld.cancelCallback( self.__moveAttickTipCBID )
		self.__deregisterEvents( self.__attackTriggers )
		self.__moveAttickTipCBID = 0

	def __onItemDropped( self, entity ) :
		"""
		entity ��������ʱ������
		"""
		pass

	def __onItemPickup( self, entity ) :
		"""
		entity �뿪����ʱ������
		"""
		if entity.id == self.__droppedBoxID :
			self.__hidePickupTips()

	def __hidePickupTips( self ) :
		"""
		����ʰȡ��ʾ
		"""
#		toolbox.infoTip.hideOperationTips( self.__pickupTipID )
		self.__deregisterEvents( self.__pickupTriggers )
		BigWorld.cancelCallback( self.__movePickupTipCBID )
		self.__movePickupTipCBID = 0

	# -------------------------------------------------
	# ��ʾ������ʾ
	# -------------------------------------------------
	def __onShowScenarioTips( self, tips, visible ) :
		"""
		�յ�������ʾ�����������ʾ�ı�λ����Ļ�м䣩
		visible ���Ƿ�������ҽ��棬False�����أ�True����
		"""
		if tips == "" : return
		if not rds.statusMgr.isInWorld() : return
		if not self.__rtScenaio :
			self.__rtScenaio = RTScenario()

		def callback() :
			self.__rtScenaio = None
			if self.__isEmptyScreen :
				if not visible:									# ��������ҽ���
					self.__toggleAllRoots()						# ����

		if not self.__isEmptyScreen :							# ����
			self.__toggleAllRoots()

		self.__rtScenaio.show( tips, self.__scenaioShowTime, \
			self.__scenaioHideTime, callback )

	def __onShowScenarioTips2( self, tips, cb=None) :
		"""
		����Ļ�·��ľ�����ʾ����ɫ����
		"""
		if tips == "" : return
		if not rds.statusMgr.isInWorld() : return
		if not self.__rtScenaio2 :
			self.__rtScenaio2 = RTScenario2()
		self.__cb = cb

		def callback() :
			self.__rtScenaio2 = None
			if callable(cb):	#add by wuxo 2011-9-29
				cb()
			self.__cb = None
		tips = StringFormat.format( tips )
		self.__rtScenaio2.show( tips, 3, 5, callback )			# ÿ�м��3�룬�������5����ʧ

	def __onInterruptScenarioTips2(self):
		"""
		�ж���Ļ�·���Ļ���ţ�����ESC
		"""
		def callback() :
			self.__rtScenaio2 = None
			self.__cb = None
		if self.__rtScenaio2:
			self.__rtScenaio2.hide(callback)


	def __onShowScenarioTips3( self, tips,showTimes,color ) :
		"""
		ȫ����Ļ���ţ���ɫ����
		showTimes���ÿ�в���ʱ����
		"""
		if tips == "" : return
		if not rds.statusMgr.isInWorld() : return
		if not self.__rtScenaio3 :
			self.__rtScenaio3 = RTScenario3( color )

		def callback() :
			self.__rtScenaio3 = None

		tips = StringFormat.format( tips )
		self.__rtScenaio3.show( tips, showTimes, 1, callback )	# ÿ�м����Ӧ�룬�������1����ʧ

	def __onShowScenarioTips4( self, tips, showTimes, cb=None) :
		"""
		����Ļ�·��ľ�����ʾ����ɫ����
		"""
		if tips == "" : return
		#if not rds.statusMgr.isInWorld() : return #��½���̿��ܻ��õ� ����ע�͵�����ж�
		if not self.__rtScenaio4 :
			self.__rtScenaio4 = RTScenario4()
		self.__cb4 = cb
		def callback() :
			self.__rtScenaio4 = None
			if callable( cb ):
				cb()
			self.__cb4 = None
		tips = StringFormat.format( tips )
		self.__rtScenaio4.show( tips, showTimes, 0, callback )

	def __onInterruptScenarioTips4(self):
		"""
		�ж���Ļ�·���Ļ���ţ�����ESC
		"""
		def callback() :
			self.__rtScenaio4 = None
			self.__cb4 = None
		if self.__rtScenaio4:
			self.__rtScenaio4.hide(callback)


	def __onShowScenarioTips5( self, tips, showTimes, cb=None) :
		"""
		���¼�������Ļ����ɫ����
		"""
		if tips == "" : return
		if not rds.statusMgr.isInWorld() : return
		if not self.__rtScenaio5 :
			self.__rtScenaio5.append( RTScenario4() )
			self.__rtScenaio5.append( RTScenario5() )

		self.__cb5 = cb

		def callback() :
			self.__rtScenaio5 = []
			if callable(cb):
				cb()
			self.__cb5 = None
		tips = StringFormat.format( tips )
		self.__rtScenaio5[1].show()
		self.__rtScenaio5[0].show( tips, showTimes, 0, callback )

	def __onInterruptScenarioTips5(self):
		"""
		�ж����¼�������Ļ������ESC
		"""
		def callback() :
			self.__rtScenaio5 = []
			self.__cb5 = None
		if self.__rtScenaio5:
			self.__rtScenaio5[1].hide()
			self.__rtScenaio5[0].hide(callback)

	def __onEndScreenBlur(self):
		"""
		����ȫ��ģ�� add by wuxo 2011-10-17
		"""
		BigWorld.setGraphicsSetting("BLOOM_FILTER", True)
		BigWorld.switchScreenBlur(-1)


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addResistHiddenRoot(self, pyRoot):
		"""�������ʱ���ԵĴ���"""
		if pyRoot not in self.__pyRootsResistHidden:
			self.__pyRootsResistHidden.append(pyRoot)

	def removeResistHiddenRoot(self, pyRoot):
		"""�������ʱ���ԵĴ���"""
		if pyRoot in self.__pyRootsResistHidden:
			self.__pyRootsResistHidden.remove(pyRoot)

	def isResistHiddenRoot(self, pyRoot):
		"""�Ƿ�������ʱ���ԵĴ���"""
		return pyRoot in self.__pyRootsResistHidden

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, eventName, *args ) :
		if eventName in self.__roleMoveTriggers :
			self.__roleMoveTriggers[eventName]( *args )
		if eventName in self.__entityFocusTriggers :
			self.__entityFocusTriggers[eventName]( *args )
		if eventName in self.__attackTriggers :
			self.__attackTriggers[eventName]( *args )
		if eventName in self.__pickupTriggers :
			self.__pickupTriggers[eventName]( *args )
		if eventName in self.__scenarioTriggers :
			self.__scenarioTriggers[eventName]( *args )

	# -------------------------------------------------
	def onEnterWorld( self ) :
		self.__rolePos = Math.Vector3( BigWorld.player().position )
		BigWorld.callback( 0.2, Functor( pixieHelper.triggerTopic, 101 ) )
		rds.shortcutMgr.setHandler( "UI_TOGGLE_ALL_UIS", self.__toggleAllRootsByShortCut )

#		if uiopHelper.hasTips( 0x0001 ) :						# ע���ɫ�ƶ�������ʾ�¼�
#			self.__registerRoleMoveEvents()
#		if uiopHelper.hasTips( self.__entityFocusTipID ) :		# ע��ѡ��Ŀ�������ʾ�¼�
			#self.__registerEntityFocusEvents()					# ��Ϊ��ʾ��������ƶ����о���Ť���߻�Ҫ��ȡ������ʾ��2010.05.05��
#			pass
#		if uiopHelper.hasTips( self.__attackTipID ) :			# ע�ṥ��Ŀ�������ʾ�¼�
#			self.__registerAttackEvents()
#		if uiopHelper.hasTips( self.__pickupTipID ) :			# ע��ʰȡ������ʾ�¼�
#			self.__registerPickupEvents()

	def onLeaveWorld( self ) :
		self.__hideWalkGuider()
		self.__hideEntityGetFocusTips()
		self.__hidePickupTips()
		self.__isEmptyScreen = False
		if self.__rtScenaio :
			self.__rtScenaio.dispose()
		if self.__rtScenaio2 :
			self.__rtScenaio2.dispose()
		if self.__rtScenaio3 :
			self.__rtScenaio3.dispose()

	def isEmptyScreen( self ):
		return self.__isEmptyScreen

# --------------------------------------------------------------------
# ��ɫ�ƶ���ʾ����
# --------------------------------------------------------------------
class WalkGuider( RootGUI ) :
	__cc_path = "guis/screenviewer/walkguider/guider.gui"
	__cc_fader = GUI.AlphaShader()
	__cc_fader.speed = 6
	__cg_flashCBID = 0

	def __init__( self, direct, text ) :
		gui = GUI.load( self.__cc_path )
		gui.bg.addShader( self.__cc_fader )
		RootGUI.__init__( self, gui )
		self.posZSegment = ZSegs.L2
		self.movable_ = False
		self.activable_ = False
		self.hitable_ = False
		self.escHide_ = False
		self.focus = False
		self.addToMgr()

		self.__pyRich = CSRichText( gui.rtTips )
		self.__pyRich.autoNewline = False
		self.__pyRich.widthAdapt = True
		edgeSpace = 4
		if direct == "L" :
			gui.bg.mapping = util.ccwRotateMapping90( gui.bg.mapping )
			gui.size = gui.bg.size = gui.size[1], gui.size[0]
			self.__pyRich.align = "R"
			self.__pyRich.text = text
			self.__pyRich.middle = self.height * 0.5
			self.__pyRich.right = gui.width - edgeSpace
		elif direct == "R" :
			gui.bg.mapping = util.cwRotateMapping90( gui.bg.mapping )
			gui.size = gui.bg.size = gui.size[1], gui.size[0]
			self.__pyRich.align = "L"
			self.__pyRich.text = text
			self.__pyRich.middle = self.height * 0.5
			self.__pyRich.left = edgeSpace
		elif direct == "T" :
			self.__pyRich.align = "C"
			self.__pyRich.text = text
			self.__pyRich.center = self.width * 0.5
			self.__pyRich.bottom = self.height - edgeSpace
		elif direct == "B" :
			gui.bg.mapping = util.cwRotateMapping180( gui.bg.mapping )
			self.__pyRich.align = "C"
			self.__pyRich.text = text
			self.__pyRich.center = self.width * 0.5
			self.__pyRich.top = edgeSpace
		self.show()

	def __del__( self ) :
		if Debug.output_del_ScreenViewerWaklGuider :
			INFO_MSG( str( self ) )
		RootGUI.__del__( self )

	# -------------------------------------------------
	# public
	# -------------------------------------------------
	def isMouseHit( self ) :
		"""
		���� False��ʹ��������͸��
		"""
		return False

	# --------------------------------------
	@classmethod
	def flash( SELF ) :
		"""
		��˸
		"""
		if SELF.__cc_fader.currentAlpha >= 1.0 :
			SELF.__cc_fader.value = 0.2
		elif SELF.__cc_fader.currentAlpha <= 0.2 :
			SELF.__cc_fader.value = 1.0
		BigWorld.cancelCallback( SELF.__cg_flashCBID )
		SELF.__cg_flashCBID = BigWorld.callback( 0.1, SELF.flash )

	@classmethod
	def unflash( SELF ) :
		BigWorld.cancelCallback( SELF.__cg_flashCBID )


class ScreenFader( RootGUI ) :
	"""��Ļalpha˥����"""
	def __init__( self ) :
		gui = GUI.load( "guis/screenviewer/screenfader/fader.gui" )
		RootGUI.__init__( self, gui )
		self.setToDefault()
		self.movable_ = False
		self.escHide_ = False
		self.posZSegment = ZSegs.L1
		self.__fade_cbid = 0
		self.addToMgr()
		self.__layout()
		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

	def __layout( self ) :
		self.size = BigWorld.screenSize()
		self.pos = 0, 0

	def __onResolutionChanged( self, preRes ) :
		""""""
		self.__layout()

	def fadein( self ) :
		"""����"""
		BigWorld.cancelCallback( self.__fade_cbid )
		self.show()
		self.gui.fader.value = 1

	def fadeout( self ) :
		"""����"""
		self.gui.fader.value = 0
		self.__fade_cbid = BigWorld.callback( self.gui.fader.speed, self.hide )

	def onEvent( self, evtMacro, *args ) :
		"""�¼�����"""
		self.__onResolutionChanged( *args )

	@property
	def fadeSpeed( self ) :
		return self.gui.fader.speed
# --------------------------------------------------------------------
# Ѫ����ʱ,��Ļ��˸Σ�վ���
# --------------------------------------------------------------------
class DangerWarning( RootGUI ):
	def __init__( self ) :
		gui = GUI.load( "guis/screenviewer/screenfader/danger.gui" )
		RootGUI.__init__( self, gui )
		self.setToDefault()
		self.movable_ = False
		self.escHide_ = False
		self.focus = False
		self.crossFocus = False
		self.moveFocus = False
		self.activable_ = False
		self.hitable_ = False
		self.posZSegment = ZSegs.L1
		self.__fade_cbid = 0

		self.addToMgr()
		self.__layout()
		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

	def __layout( self ) :
		self.size = BigWorld.screenSize()
		self.pos = 0, 0

	def __onResolutionChanged( self, preRes ) :
		""""""
		self.__layout()

	def fadein( self ) :
		"""����"""
		BigWorld.cancelCallback( self.__fade_cbid )
		self.show()
		self.gui.fader.value = 1
		self.flicker()

	def flicker( self ) :
		"""��˸"""
		#��ʾ
		if self.gui.fader.alpha == 0:
			self.gui.fader.speed = 0.25
			self.gui.fader.alpha = 1
			self.temp = True
		#����
		elif self.gui.fader.alpha == 1:
			self.gui.fader.speed = 1
			self.gui.fader.alpha = 0
		BigWorld.callback( 1, self.flicker )

	def fadeout( self ) :
		"""����"""
		self.gui.fader.value = 0
		self.__fade_cbid = BigWorld.callback( self.gui.fader.speed, self.hide )

	def onEvent( self, evtMacro, *args ) :
		"""�¼�����"""
		self.__onResolutionChanged( *args )

	@property
	def fadeSpeed( self ) :
		return self.gui.fader.speed

class ChangeUIEffect( RootGUI ):
	def __init__( self ):
		gui = GUI.load( "guis/screenviewer/screenfader/changeUIEffect.gui" )
		RootGUI.__init__( self, gui )
		self.setToDefault()
		self.movable_ = False
		self.escHide_ = False
		self.focus = False
		self.crossFocus = False
		self.moveFocus = False
		self.activable_ = False
		self.hitable_ = False
		self.posZSegment = ZSegs.L1

		self.addToMgr()
		self.__layout()
		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

	def __layout( self ) :
		self.size = BigWorld.screenSize()
		self.pos = 0, 0

	def __onResolutionChanged( self, preRes ) :
		""""""
		self.__layout()

	def onEvent( self, evtMacro, *args ) :
		"""�¼�����"""
		self.__onResolutionChanged( *args )


# --------------------------------------------------------------------
# ������ʾ�� RichText
# --------------------------------------------------------------------
class RTScenario( RootGUI, CSRichText ) :
	def __init__( self ) :
		CSRichText.__init__( self )
		gui = CSRichText.getGui( self )
		RootGUI.__init__( self, gui )
		self.posZSegment = ZSegs.L4
		self.movable_ = False
		self.activable_ = False
		self.hitable_ = False
		self.escHide_ = False
		self.focus = False
		self.addToMgr()

		self.autoNewline = False
		self.widthAdapt = True
		self.align = "C"

		self.__cbids = []

		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

		# ����������ⴰ��
		ScreenViewer().addResistHiddenRoot(self)

	def dispose( self ) :
		self.__clear()
		ECenter.unregisterEvent( "EVT_ON_RESOLUTION_CHANGED", self )
		RootGUI.dispose( self )
		CSRichText.dispose( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __lineByLineShow( self, fader ) :
		"""
		�����ı���
		"""
		fader.value = 1

	def __clear( self ) :
		"""
		�����ǰ������ʾ�ı�
		"""
		for cbid in self.__cbids :
			BigWorld.cancelCallback( cbid )
		self.clear()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		RootGUI.generateEvents_( self )
		CSRichText.generateEvents_( self )

	def locate_( self ) :
		"""
		�ڷ���ʾλ��
		"""
		self.r_center = 0
		self.r_middle = 0.3
		if self.top < 0 :
			self.r_top = 0.8


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, preReso ) :
		"""
		��Ļ�ֱ��ʸı�ʱ������
		"""
		self.locate_()

	# -------------------------------------------------
	def show( self, text, showTime, hideTime, callback ) :
		self.__clear()
		self.text = text
		self.locate_()

		delayTime = 0
		for idx, elemInfo in enumerate( self.lineInfos_ ) :
			fader = GUI.AlphaShader()							# ���� Shader
			fader.value = 0
			fader.speed = 1.5
			fader.reset()
			for pyElem in elemInfo[1] :							# �����е�ÿ��Ԫ�����һ������ shader
				pyElem.gui.addShader( fader )
			func = Functor( self.__lineByLineShow, fader )
			cbid = BigWorld.callback( delayTime, func )			# ���ý��� callback
			self.__cbids.append( cbid )
			delayTime += showTime
		hideTime += delayTime
		func = Functor( self.hide, callback )
		cbid = BigWorld.callback( hideTime, func )				# ��ʱ����
		self.__cbids.append( cbid )
		RootGUI.show( self )

	def hide( self, callback ) :
		RootGUI.hide( self )
		self.dispose()
		callback()


class RTScenario2( RTScenario ) :


	def __init__( self ) :
		RTScenario.__init__( self )
		self.texture = "guis/empty.dds"
		self.color = ( 20, 20, 20, 250 )
		self.align = "L"


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def locate_( self ) :
		screenSIze = BigWorld.screenSize()
		self.gui.height = 75
		self.gui.width = screenSIze[0]
		self.bottom = screenSIze[1]
		self.left = 0


class RTScenario3( RootGUI, CSRichText ) :
	"""
	��Ļ����text
	add by wuxo 2011-9-6
	"""
	def __init__( self,color = (20,20,20,255) ) :
		CSRichText.__init__( self )
		gui = CSRichText.getGui( self )
		RootGUI.__init__( self, gui )
		self.posZSegment = ZSegs.L4

		win = GUI.Window("guis/empty.dds")
		self.parentUI = PyGUI(win)
		self.parentUI.setToDefault()
		self.parentUI.color = color

		self.movable_ = False
		self.activable_ = False
		self.hitable_ = False
		self.escHide_ = False
		self.focus = False
		self.addToMgr()

		self.autoNewline = False
		self.widthAdapt = True
		self.align = "C"

		self.__cbids = []

		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

		# ����������ⴰ��
		ScreenViewer().addResistHiddenRoot(self)

	def dispose( self ) :
		self.__clear()
		ECenter.unregisterEvent( "EVT_ON_RESOLUTION_CHANGED", self )
		RootGUI.dispose( self )
		CSRichText.dispose( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __lineByLineShow( self, fader ) :
		"""
		�����ı���
		"""
		fader.value = 1

	def __clear( self ) :
		"""
		�����ǰ������ʾ�ı�
		"""
		for cbid in self.__cbids :
			BigWorld.cancelCallback( cbid )
		self.clear()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		RootGUI.generateEvents_( self )
		CSRichText.generateEvents_( self )

	def locate_( self ) :
		"""
		�ڷ���ʾλ��
		"""
		self.parentUI.size = BigWorld.screenSize()
		self.parentUI.gui.position = (-1,1,0.5)
		self.posZ = 1

		self.r_center = 0
		self.r_middle = 0.3
		if self.top < 0 :
			self.r_top = 0.8


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, preReso ) :
		"""
		��Ļ�ֱ��ʸı�ʱ������
		"""
		self.locate_()

	# -------------------------------------------------
	def show( self, text, showTimes, hideTime, callback) :
		"""
		��Ļ����,ÿ�в���ʱ�������ñ����
		"""
		GUI.addRoot(self.parentUI.gui)

		self.__clear()
		self.text = text
		self.locate_()

		delayTime = 0
		count = 0
		for idx, elemInfo in enumerate( self.lineInfos_ ) :
			fader = GUI.AlphaShader()							# ���� Shader
			fader.value = 0
			fader.speed = 1.5
			fader.reset()
			for pyElem in elemInfo[1] :							# �����е�ÿ��Ԫ�����һ������ shader
				pyElem.gui.addShader( fader )
			func = Functor( self.__lineByLineShow, fader )
			cbid = BigWorld.callback( delayTime, func )			# ���ý��� callback
			self.__cbids.append( cbid )
			if len(showTimes) > count:		#�������ñ����ÿ����ʾʱ��
				delayTime += showTimes[count]
			else:
				delayTime += 3   #Ĭ��Ϊ3��
			count += 1
		hideTime += delayTime
		func = Functor( self.hide, callback )
		cbid = BigWorld.callback( hideTime, func )				# ��ʱ����
		self.__cbids.append( cbid )
		RootGUI.show( self )

	def hide( self, callback ) :
		GUI.delRoot( self.parentUI.gui )
		RootGUI.hide( self )
		self.dispose()
		self.parentUI.dispose()
		del self.parentUI
		callback()


class RTScenario4( RootGUI, CSRichText ):
	def __init__( self ) :
		CSRichText.__init__( self )
		gui = CSRichText.getGui( self )
		RootGUI.__init__( self, gui )
		self.posZSegment = ZSegs.L4
		self.movable_ = False
		self.activable_ = False
		self.hitable_ = False
		self.escHide_ = False
		self.focus = False
		self.addToMgr()

		self.autoNewline = True
		self.maxWidth = BigWorld.screenWidth()
		self.widthAdapt = False
		self.align = "L"
		self.__cbids = []

		win = GUI.Window("guis/empty.dds")
		self.parentUI = PyGUI(win)
		self.parentUI.setToDefault()
		#self.parentUI.align = "L"
		self.parentUI.color = ( 20, 20, 20, 255 )
		self.realheight = 0.0
		self.alreadyAdd = False

		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

		# ����������ⴰ��
		ScreenViewer().addResistHiddenRoot(self)

	def dispose( self ) :
		self.__clear()
		ECenter.unregisterEvent( "EVT_ON_RESOLUTION_CHANGED", self )
		RootGUI.dispose( self )
		CSRichText.dispose( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __lineByLineShow( self, fader, num ) :
		"""
		�����ı���
		"""
		if self.alreadyAdd and num ==1:
			self.bottom += self.realheight/2
			self.alreadyAdd = False
		if not self.alreadyAdd and num == 2:
			self.bottom -= self.realheight/2
			self.alreadyAdd = True
		fader.value = 1

	def __clear( self ) :
		"""
		�����ǰ������ʾ�ı�
		"""
		for cbid in self.__cbids :
			BigWorld.cancelCallback( cbid )
		self.clear()

	def __locate( self ):
		screenSIze = BigWorld.screenSize()
		self.parentUI.size = screenSIze
		self.parentUI.gui.position = ( -1, -1 + 2*100/screenSIze[1], 0.5 )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		RootGUI.generateEvents_( self )
		CSRichText.generateEvents_( self )

	def onEvent( self, macroName, preReso ) :
		"""
		��Ļ�ֱ��ʸı�ʱ������
		"""
		if "@B" in self.text:
			self.__locate()
		else:
			self.maxWidth = BigWorld.screenWidth()
			self.locate_()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def locate_( self ) :
		screenSIze = BigWorld.screenSize()
		self.gui.height = 800
		self.gui.width = screenSIze[0]
		self.bottom = screenSIze[1] + 800 - 60
		if len( self.lineInfos_ ) > 1 and not "@B" in self.text:
			self.bottom -= self.realheight/2
		self.left = 0

		self.parentUI.size = screenSIze
		self.parentUI.gui.position = (-1,-1 + 2*100/screenSIze[1] ,0.5)
		self.posZ = 1

	def show( self, text, showTimes, hideTime, callback) :
		"""
		��Ļ����,ÿ�в���ʱ�������ñ����
		��һ���ֺܶ�ʱ,��ֱ����¿�����ʾ����������С�ֱ�����ʾ������ʱ
		С�ֱ�����Ļʹ��2������ʾ����
		RichText�ؼ��ڳ�ʼ��ʱ���������������С���иߡ��п����Ϣ
		һ�н���������E��ʾ
		"""
		GUI.addRoot(self.parentUI.gui)
		self.__clear()
		text = text.replace("@B","E@B")
		self.text = text
		self.locate_()

		displayTime =0				# ����ʾʱ��
		delayTime = 0				# �н���ʱ��
		count = 0
		splitFalg = False			# �Ѿ�����ֱ��
		preCount = 0
		for idx, elemInfo in enumerate( self.lineInfos_ ) :
			fader = GUI.AlphaShader()							# ���� Shader
			fader.value = 0
			fader.speed = 1.5
			fader.reset()
			num = 1
			for pyElem in elemInfo[1] :							# �����е�ÿ��Ԫ�����һ������ shader
				pyElem.gui.addShader( fader )
				self.realheight = pyElem.height
				if not pyElem.text.endswith("E"):		# ����ֵ�һ�е�ǰ��Σ���E�������ж�
					num = 2
					splitFalg = True
				else:
					pyElem.text = pyElem.text.rstrip("E")
					if splitFalg:							# ����ֵ�һ�еĺ���
						num = 0
					splitFalg = 0
			func = Functor( self.__lineByLineShow, fader, num )
			cbid = BigWorld.callback( displayTime, func )			# ���ý��� callback
			self.__cbids.append( cbid )
			if len(showTimes) > preCount:		#�������ñ����ÿ����ʾʱ��
				delayTime = displayTime + showTimes[preCount]
			else:
				delayTime =  displayTime + 3    #Ĭ��Ϊ3��
			if num >1:
				x=0
			else:
				x=1
				displayTime = delayTime
			fun = Functor( self.scroll, count, num )
			cbid = BigWorld.callback( delayTime, fun )
			self.__cbids.append( cbid )
			count += 1
			preCount += x
		hideTime += delayTime
		func = Functor( self.hide, callback )
		cbid = BigWorld.callback( hideTime, func )				# ��ʱ����
		self.__cbids.append( cbid )
		RootGUI.show( self )

	def scroll( self, count, num = 1 ):
		pyElems = []
		if len( self.lineInfos_ ) > count:
			text, pyElems = self.lineInfos_[count]
		for i in pyElems:
			i.visible = False
		self.bottom -= num * ( self.realheight + self.spacing )

	def hide( self, callback ) :
		callback()
		GUI.delRoot( self.parentUI.gui )
		RootGUI.hide( self )
		self.dispose()
		self.parentUI.dispose()
		del self.parentUI

class RTScenario5( RootGUI, CSRichText ):
	"""
	���ں�RTScenario4���ɵ�Ӱ����
	"""
	def __init__( self ) :
		CSRichText.__init__( self )
		gui = CSRichText.getGui( self )
		RootGUI.__init__( self, gui )
		self.posZSegment = ZSegs.L4
		self.movable_ = False
		self.activable_ = False
		self.hitable_ = False
		self.escHide_ = False
		self.focus = False
		self.addToMgr()

		self.autoNewline = False
		self.widthAdapt = True
		self.align = "L"
		self.__cbids = []

		win = GUI.Window("guis/empty.dds")
		self.parentUI = PyGUI(win)
		self.parentUI.setToDefault()
		#self.parentUI.align = "L"
		self.parentUI.color = ( 20, 20, 20, 255 )

		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

		# ����������ⴰ��
		ScreenViewer().addResistHiddenRoot(self)

	def dispose( self ) :
		self.__clear()
		ECenter.unregisterEvent( "EVT_ON_RESOLUTION_CHANGED", self )
		RootGUI.dispose( self )
		CSRichText.dispose( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __lineByLineShow( self, fader ) :
		"""
		�����ı���
		"""
		fader.value = 1

	def __clear( self ) :
		"""
		�����ǰ������ʾ�ı�
		"""
		for cbid in self.__cbids :
			BigWorld.cancelCallback( cbid )
		self.clear()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		RootGUI.generateEvents_( self )
		CSRichText.generateEvents_( self )

	def onEvent( self, macroName, preReso ) :
		"""
		��Ļ�ֱ��ʸı�ʱ������
		"""
		self.locate_()
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def locate_( self ) :
		screenSIze = BigWorld.screenSize()
		self.gui.height = 75
		self.gui.width = screenSIze[0]
		self.bottom = 75
		self.left = 0

		self.parentUI.size = screenSIze
		self.parentUI.gui.position = (-1,  3 - 2*100 / screenSIze[1]  ,0.5)
		self.posZ = 1

	def __lineByLineShow( self, fader ) :
		"""
		�����ı���
		"""
		fader.value = 1

	def show( self ) :
		"""
		��Ļ����,ÿ�в���ʱ�������ñ����
		"""
		GUI.addRoot(self.parentUI.gui)
		self.__clear()
		self.locate_()
		RootGUI.show( self )


	def hide( self ) :
		GUI.delRoot( self.parentUI.gui )
		RootGUI.hide( self )
		self.dispose()
		self.parentUI.dispose()
		del self.parentUI

class RTScenario6( RootGUI, CSRichText ):
	"""
	����ESC������ʾ
	"""
	def __init__( self ) :
		CSRichText.__init__( self )
		gui = CSRichText.getGui( self )
		RootGUI.__init__( self, gui )
		self.posZSegment = ZSegs.L1
		self.movable_ = False
		self.activable_ = False
		self.hitable_ = False
		self.escHide_ = False
		self.focus = False
		self.fontSize = 18
		self.addToMgr()

		self.autoNewline = False
		self.widthAdapt = True
		self.align = "L"

		#win = GUI.Window("guis/empty.dds")
		#self.parentUI = PyGUI(win)
		#self.parentUI.setToDefault()
		#self.parentUI.color = ( 0, 0, 0, 0 )
		self.__clear()
		self.text = lbDatas.CAMERA_ESC
		self.locate_()
		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

		# ����������ⴰ��
		ScreenViewer().addResistHiddenRoot(self)

	def dispose( self ) :
		self.__clear()
		ECenter.unregisterEvent( "EVT_ON_RESOLUTION_CHANGED", self )
		RootGUI.dispose( self )
		CSRichText.dispose( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __lineByLineShow( self, fader ) :
		"""
		�����ı���
		"""
		fader.value = 1

	def __clear( self ) :
		"""
		�����ǰ������ʾ�ı�
		"""
		self.clear()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		RootGUI.generateEvents_( self )
		CSRichText.generateEvents_( self )

	def onEvent( self, macroName, preReso ) :
		"""
		��Ļ�ֱ��ʸı�ʱ������
		"""
		self.locate_()
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def locate_( self ) :
		screenSIze = BigWorld.screenSize()
		self.gui.height = 40.0
		self.gui.width = 200.0
		self.bottom = 40.0
		self.left = screenSIze[0]/2.0 - 200/2.0

		#self.parentUI.size = ( 40.0, 200.0 )
		#self.parentUI.gui.position = (-200.0/screenSIze[0],  -40.0 / screenSIze[1]  , 1 )
		#self.posZ = 1

	def show( self ) :
		"""
		��ʾ
		"""
		#GUI.addRoot(self.parentUI.gui)
		RootGUI.show( self )


	def hide( self ) :
		#GUI.delRoot( self.parentUI.gui )
		RootGUI.hide( self )
		#self.dispose()
		#self.parentUI.dispose()
		#del self.parentUI




class UIOSentinel( Singleton ) :
	"""
	�û�������ʾ��ת����
	"""
	def __init__( self ) :
		self.__consigner = {}
		ECenter.registerEvent( "EVT_ON_IMPLEMENT_UI_OPERATION", self )

	def attach( self, uioKey, handler ) :
		"""
		"""
		handlers = self.__consigner.get( uioKey )
		if handlers is not None :
			handlers.append( handler )
		else :
			self.__consigner[uioKey] = [ handler ]

	def detach( self, uioKey, handler ) :
		"""
		"""
		handlers = self.__consigner.get( uioKey )
		if handlers is None : return
		if handler in handlers :
			handlers.remove( handler )
		if len( handlers ) == 0 :
			del self.__consigner[ uioKey ]

	def implement( self, uioKey ) :
		"""
		"""
		handlers = self.__consigner.get( uioKey )
		if handlers is None : return
		for handler in handlers :
			handler( uioKey )
		print "UI operations( ids: %s ) commits!" % str( uioKey )

	def onEvent( self, evtMacro, *args ) :
		"""
		"""
		if evtMacro == "EVT_ON_IMPLEMENT_UI_OPERATION" :
			self.implement( *args )
