# -*- coding: gb18030 -*-
#
# $Id: BigMap.py,v 1.28 2008-08-27 09:04:26 huangyongwei Exp $

"""
implement full map class

2008.01.03 : wirten by huangyongwei
"""

import csstatus
from event.Timer import Timer
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.FlexExWindow import HVFlexExWindow
from guis.common.FrameEx import HVFrameEx
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.controls.ODComboBox import ODComboBox
from guis.controls.ProgressBar import HProgressBar
from MapPanel import MapPanel
from NPCLister import NPCLister
from Helper import courseHelper
from LabelGather import labelGather

from bwdebug import *


class BigMap( HVFlexExWindow ) :
	def __init__( self ) :
		wnd = GUI.load( "guis/general/bigmap/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		HVFlexExWindow.__init__( self, wnd )
		self.h_dockStyle = "HFILL"									# ˮƽ��������ֱ��ʸı���ı��С
		self.v_dockStyle = "VFILL"									# ��ֱ��������ֱ��ʸı���ı��С
		self.foacus = False
		self.moveFocus = False										# �������ƶ�
		self.posZSegment = ZSegs.L3									# always on top
		self.activable_ = True										# ���Ա�����
		self.escHide_ 		 = True									# ���԰� esc ������
		self.__areaList = []											# ���еĵ��� Combobx ѡ��
		self.__ignWhAreas = {}										# ��������ʾ��ȫ��ͼ����,key:(spaceLabel,isSky)
		self.__currArea = None										# ��¼��ǰ���ڵ���
		self.__updateTimer = Timer( self.__update )					# ʵʱ���µ� timer
		self.__updateTimer.interval = 0.05
		

		self.__initialize( wnd )

		self.__triggers = {}
		self.__registerTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		self.__pyHPBar = HProgressBar( wnd.hpBg.bar )							# Ѫ��

		self.__pyTopBar = PyGUI( wnd.topBar )									# ���ϲ���ť�İ���
		self.__pyTopBar.h_dockStyle = "RIGHT"
		self.__pyDownBar = PyGUI( wnd.downBar )									# ���²�����İ���
		self.__pyDownBar.h_dockStyle = "CENTER"
		self.__pyDownBar.v_dockStyle = "BOTTOM"
		
		self.__pyBgFrame = HVFrameEx( wnd.bgFrame )
		self.__pyBgFrame.h_dockStyle = "HFILL"
		self.__pyBgFrame.v_dockStyle = "VFILL"		

		self.__pyMapPanel = MapPanel( wnd.mapPanel )							# ��ʾ��ͼ�İ���
		self.__pyMapPanel.h_dockStyle = "HFILL"
		self.__pyMapPanel.v_dockStyle = "VFILL"
		self.__pyMap = self.__pyMapPanel.pyMap
		self.__pyMap.onMouseMove.bind( self.__onMapMouseMove )
		self.__pyMap.onWorldAreaClick.bind( self.__onWorldAreaClick )
		
		self.__pySTTips = StaticText( wnd.stTips )
		self.__pySTTips.text = ''

		self.__pyCBAreas = ODComboBox( wnd.topBar.cbAreas )						# �����б���Ͽ�
		self.__pyCBAreas.viewCount = 16
		self.__pyCBAreas.onItemSelectChanged.bind( self.__onAreaSelected )
		self.__pyCBAreas.autoSelect = False
		self.__loadAllAreas()

		self.__pyBtnToggleNP = HButtonEx( wnd.topBar.btnToggleNPC )				# ��ʾ/�������� NPC
		self.__pyBtnToggleNP.text = labelGather.getText( "BigMap:main", "btnHideNPC" )
		self.__pyBtnToggleNP.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnToggleNP.onLClick.bind( self.__toggleNPCs )

		self.__pySearchNPCBtn = HButtonEx( wnd.topBar.btnSearchNPC )				# ���� NPC
		self.__pySearchNPCBtn.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pySearchNPCBtn.onLClick.bind( self.__showNPCLister )

		self.__pyShowAllMapsBtn = HButtonEx( wnd.topBar.btnWorld )					# ��ʾ�����ͼ��ť
		self.__pyShowAllMapsBtn.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyShowAllMapsBtn.onLClick.bind( self.__showWholeArea )

		self.__pySTPSeat = StaticText( wnd.downBar.stPSeat )					# ��ʾ������ڵص�
		self.__pySTPPos = StaticText( wnd.downBar.stPPos )						# ��ʾ��ҵ�ǰ����
		self.__pySTMPos = StaticText( wnd.downBar.stMPos )						# ��ʾ��굱ǰ����

		self.__pyScaleBtnsPanel = PyGUI( wnd.mapPanel.scaleBtnsPanel )			# ���Ű�ť�İ���
		self.__pyScaleBtnsPanel.h_dockStyle = "RIGHT"
		self.__pyScaleBtnsPanel.v_dockStyle = "MIDDLE"
		self.__pyPlusBtn = Button( wnd.mapPanel.scaleBtnsPanel.plusBtn )		# �Ŵ�ť
		self.__pyPlusBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyPlusBtn.onLClick.bind( self.__pyMapPanel.orginMapSize )
		self.__pyMinusBtn = Button( wnd.mapPanel.scaleBtnsPanel.minusBtn )		# ��С��ť
		self.__pyMinusBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyMinusBtn.onLClick.bind( self.__pyMapPanel.adaptMapSize )

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pySearchNPCBtn, "BigMap:main", "btnSearchNPC" )
		labelGather.setPyBgLabel( self.__pyShowAllMapsBtn, "BigMap:main", "btnWorldMap" )
		labelGather.setPyLabel( self.__pySTTips, "BigMap:main", "stTips" )
		labelGather.setPyLabel( self.__pySTPSeat, "BigMap:main", "stPSeat" )
		labelGather.setLabel( wnd.downBar.stMSeat, "BigMap:main", "stMSeat" )
		labelGather.setLabel( wnd.topBar.lbArea, "BigMap:main", "stArea" )
	


	def __loadAllAreas( self ) :
		"""
		������������ѡ��
		"""
		areas = rds.mapMgr.getAreas()
		for idx, area in enumerate( areas ) :
			if area.ignore:
				wholeArea = area.wholeArea
				isSkyArea = wholeArea.isSkyArea
				if wholeArea.ignore:
					spaceLabel = wholeArea.spaceLabel
					if not ( spaceLabel, isSkyArea ) in self.__ignWhAreas:
						self.__ignWhAreas[( spaceLabel, isSkyArea )] = wholeArea
				continue					# ���Ը�����
			self.__pyCBAreas.addItem( area.fullName )
			self.__areaList.append( area )

	# -------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_BIGMAP"] = self.__toggleVisible
		self.__triggers["EVT_ON_ROLE_ENTER_AREA"] = self.__onEnterArea
		self.__triggers["EVT_ON_ROLE_HP_CHANGED"] = self.__onUpdateHP
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	def __toggleVisible( self ) :
		"""
		��ʾ/���ش��ͼ
		"""
		self.visible = not self.visible
		return True

	# -------------------------------------------------
	def __resetArea( self, area ) :
		"""
		������ʾ����
		"""
		self.__pyMapPanel.setArea( area )
		player = BigWorld.player()
		currArea = player.getCurrArea()
		if currArea == area or area == currArea.wholeArea :					# ��ɫ�����õ�������
			point = area.worldPoint2TexturePoint( player.position )
			self.__pyMapPanel.scrollToPoint( point )
		elif area.isWholeArea() or area.hasTexture() :
			self.__pyMapPanel.scrollToPoint( ( 0, 0 ) )
		else :
			worldBound = area.worldBound
			x = worldBound.x + worldBound.width * 0.5
			y = worldBound.y + worldBound.height / 2
			point = area.wholeArea.worldPoint2TexturePoint( ( x, y ) )
			self.__pyMapPanel.scrollToPoint( point )

	def __selectCurrArea( self ) :
		"""
		�򿪵�ͼ���������ʱ��ѡ�е�ǰ����
		"""
		if self.__currArea in self.__areaList :							# ����б��д��ڵ�ǰ����
			index = self.__areaList.index( self.__currArea )
			self.__pyCBAreas.selIndex = index							# ��ѡ�е�ǰ����
			return
		wholeArea = self.__currArea.wholeArea							# ѡ������ĸ�����
		if wholeArea in self.__areaList :
			index = self.__areaList.index( wholeArea )					# ����������
			if self.__currArea.hasTexture() :							# �����ǰ��������ͼ
				self.__pyCBAreas.onItemSelectChanged.shield()
				self.__pyCBAreas.selIndex = index						# ѡ�и����򣬵�������ѡͼ
				self.__pyCBAreas.onItemSelectChanged.unshield()
				self.__resetArea( self.__currArea )						# ������ʾ�Լ��������ͼ
			elif self.__pyCBAreas.selIndex == index :					# �����ǰ����û����ͼ( �����Ѿ�ѡ���˵�ǰ��ͼ������������ )
				self.__resetArea( wholeArea )							# �����õ�ͼΪ�������ͼ
			else :
				self.__pyCBAreas.selIndex = index						# ����ѡ�и��������ͼ

	def __update( self ) :
		"""
		���µ�ͼ
		"""
		player = BigWorld.player()
		self.__pyMap.update( player )
		pos = player.position
		self.__pySTPPos.text = "%d:%d" % ( pos.x, pos.z )

	# -------------------------------------------------
	def __onEnterArea( self, newArea ) :
		"""
		����ɫ����ĳ����ʱ��������newArea ����Ϊ None��
		"""
		self.__setIgnoreArea( newArea )
		self.__currArea = newArea
		# "�㵱ǰ��λ���ǣ�%s"
		name = labelGather.getText( "BigMap:main", "stPSeat" ) % self.__currArea.spaceName
		if self.__currArea.isSubArea() :
			name = name + ", %s" % ( self.__currArea.name )
		self.__pySTPSeat.text = name
		self.__pyMap.onEnterArea( self.__currArea )
		if self.visible :											# �����ͼ�ɼ�
			self.__selectCurrArea()									# ��ѡ�е�ǰ������Ϊ�򿪵�ͼʱ�����ᴥ��һ�Σ�

	def __onUpdateHP( self, entityID, hp, hpMax ) :
		"""
		����Ѫ��
		"""
		if BigWorld.player().id != entityID:
			return
		if hpMax <= 0 :
			self.__pyHPBar.value = 0
		else :
			self.__pyHPBar.value = float( hp ) / hpMax
	
	def __setIgnoreArea( self, newArea ):
		if self.__currArea:				#ԭ���������Ǻ��Եģ������������ɾ��
			wholeArea = self.__currArea.wholeArea
			spaceLabel = wholeArea.spaceLabel
			isSkyArea = wholeArea.isSkyArea
			if ( spaceLabel, isSkyArea ) in self.__ignWhAreas:
				fullName = self.__currArea.fullName
				if fullName in self.__pyCBAreas.items:
					self.__pyCBAreas.removeItem( fullName )
					if wholeArea in self.__areaList:
						self.__areaList.remove( wholeArea )
		if newArea :					#�½���������Ǻ��Եģ���ӽ������б�
			wholeArea = newArea.wholeArea
			spaceLabel = wholeArea.spaceLabel
			isSkyArea = wholeArea.isSkyArea
			if ( spaceLabel, isSkyArea ) in self.__ignWhAreas:
				fullName = newArea.fullName
				if not fullName in self.__pyCBAreas.items:
					self.__pyCBAreas.addItem( fullName )
					if not wholeArea in self.__areaList:
						self.__areaList.append( wholeArea )
	# -------------------------------------------------
	def __onAreaSelected( self, index ) :
		"""
		��ѡ��һ������ʱ������
		"""
		NPCLister.hide()
		if index >= 0 :
			area = self.__areaList[index]
			self.__resetArea( area )
		self.__pyMapPanel.adaptMapSize()

	def __toggleNPCs( self, pyBtn ) :
		"""
		��ʾ/���� NPC
		"""
		showNPCText = labelGather.getText( "BigMap:main", "btnShowNPC" )
		if pyBtn.text == showNPCText :
			pyBtn.text = labelGather.getText( "BigMap:main", "btnHideNPC" )
			self.__pyMap.showNPCs()
		else :
			pyBtn.text = showNPCText
			self.__pyMap.hideNPCs()

	def __showNPCLister( self ) :
		"""
		��ʾ NPC ��������
		"""
		area = self.__pyMap.viewArea
		if area.isSubArea() :
			area = area.wholeArea
		NPCLister.show( self, area )

	def __showWholeArea( self ) :
		"""
		��ʾȫ��ͼ�������ͼ��
		"""
		self.__resetArea( rds.mapMgr.worldArea )
		self.__pyCBAreas.selIndex = -1
		self.__pyMapPanel.orginMapSize()

	# -------------------------------------------------
	def __onMapMouseMove( self, dx, dy ) :
		"""
		������ڵ�ͼ���ƶ�ʱ������
		"""
		self.__pySTMPos.text = "%d:%d" % tuple( self.__pyMap.getMouseInWorldPoint() )

	def __onWorldAreaClick( self, area ) :
		"""
		ѡ��ĳ������ʱ������
		"""
		if area is None :
			# "�õ�ͼ��ʱû���ţ�"
			showMessage( 0x0201, "", MB_OK, pyOwner = self )
			return
		if area in self.__areaList :
			self.__pyCBAreas.selIndex = self.__areaList.index( area )
		else :
			self.__pyCBAreas.selIndex = -1
			self.__resetArea( area )
		self.__pyMapPanel.adaptMapSize()


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def afterStatusChanged( self, oldStatus, newStatus ) :
		"""
		��״̬���ı�ʱ������
		"""
		if oldStatus == Define.GST_BACKTO_ROLESELECT_LOADING :
			self.hide()

	def onLeaveWorld( self ) :
		"""
		��ɫ�뿪����ʱ������
		"""
		self.hide()
		self.__pyMap.onLeaveWorld()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self ) :
		"""
		��ʾ����
		"""
		currArea = self.__currArea
		if currArea.texture == "" and \
			currArea.wholeArea.texture == "" :						# ���������ĵ�ͼ���ܲ鿴����ֱ�ӷ���
				# "�㵱ǰ���ڵ���������鿴��ͼ"
				showMessage( 0x0202, "", MB_OK, pyOwner = self )
				return
		self.__selectCurrArea()										# �򿪵�ͼʱ����ʾ��ǰ����
		player = BigWorld.player()
		self.__onUpdateHP( player.id, player.getHP(), player.getHPMax() )
		self.__updateTimer.start()
		self.__pyMapPanel.adaptMapSize()
		HVFlexExWindow.show( self )
		self.__pyMap.onWindowShowed()
		rds.worldCamHandler.disable()
		rds.helper.courseHelper.openWindow( "ditu_chuangkou" )
		showNPCText = labelGather.getText( "BigMap:main", "btnShowNPC" )	
		if self.__pyBtnToggleNP.text == showNPCText :
			self.__pyMap.hideNPCs()
		else :
			self.__pyMap.showNPCs()

	def hide( self ) :
		"""
		���ش���
		"""
		HVFlexExWindow.hide( self )
		self.__pyMap.onWindowHidded()
		self.__updateTimer.stop()
		rds.worldCamHandler.enable()

	# -------------------------------------------------
	def showNPC( self, npc ) :
		"""
		��������ת��ָ���� NPC ��
		"""
		selIndex = self.__pyCBAreas.selIndex
		if selIndex < 0 : return
		area = self.__areaList[selIndex]
		point = area.worldPoint2TexturePoint( npc.getPosition( self.__pyMap.viewArea.spaceLabel ) )
		self.__pyMapPanel.scrollToPoint( point )
		self.__pyMap.highlightNPC( npc )
