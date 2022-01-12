# -*- coding: gb18030 -*-

from guis import *
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.common.Window import Window
from guis.controls.Control import Control
from LabelGather import labelGather
from guis.general.playerprowindow.TargetModelRenderRemote import TargetModelRenderRemote
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
import time
import csdefine
from config.client.msgboxtexts import Datas as mbmsgs

class HighDance( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/highdance/highDance.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_  = True

		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()
		
	def __initialize( self, wnd ):
		labelGather.setLabel( wnd.lbTitle, "HighDance:HighDance", "lbTitle" )
		
		self.__pyDancersPanel = DancersPanel( wnd.dancerPanel )
		self.__pyDancersPanel.onItemSelectChanged.bind( self.__onDancerSelectChanged )
		
		self.__modelRender = DancerModelRender( wnd.modelPanel.modelRender )#��Ⱦ����Ŀ�
		
		self.__pyStTips = StaticText( wnd.stNextTime )
		self.__pyStTips.text = ""
		
		self.__pyStRoleName = StaticText( wnd.modelPanel.stPlayerName )
		self.__pyStRoleName.text = ""
		
		self.__pyBtnChallenge = HButtonEx( wnd.btnChallenge )
		self.__pyBtnChallenge.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnChallenge.onLClick.bind( self.__onChallenge )
		self.__pyBtnChallenge.enable = False
		labelGather.setPyBgLabel( self.__pyBtnChallenge, "HighDance:HighDance", "btnChallenge")
		
		labelGather.setLabel( wnd.dancerPanel.goldenDancer.lbTitle.stTitle, "HighDance:HighDance", "goldenDancer" )
		labelGather.setLabel( wnd.dancerPanel.silverDancer.lbTitle.stTitle, "HighDance:HighDance", "silverDancer" )
		labelGather.setLabel( wnd.dancerPanel.copperDancer.lbTitle.stTitle, "HighDance:HighDance", "copperDancer" )
		labelGather.setLabel( wnd.dancerPanel.candidateDancer.lbTitle.stTitle, "HighDance:HighDance", "candidateDancer" )
		
	
	# -------------------------------------------------------------------
	# private
	#--------------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["UPDATE_WU_WANG_BANG"] = self.__onReceiveDancerInfo
		self.__triggers["WU_WANG_BANG_CHALLENGE_BUTTON"]	= self.__updateBtnState		
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )
		
	def __onDancerSelectChanged( self, roleInfo ):
		self.__setModeInfo()
		
	def __onChallenge( self ):
		"""
		��ս����
		"""
		player = BigWorld.player()
		playerName = player.playerName
		selIndex = self.__pyDancersPanel.selIndex
		if selIndex < 0:return
		playerIndex = self.__pyDancersPanel.getIndexByName( playerName )
		playerIndexState = self.__getIndexState( playerIndex )
		challengeIndex = self.__pyDancersPanel.selIndex
		challengeIndexState = self.__getIndexState( challengeIndex )
		if playerIndexState != csdefine.DANCER_NONE and playerIndexState < challengeIndexState:	#��ʾ��ս�ͼ���������Ҫ��������ȷ�Ͽ�
			def query( rs_id ):
				if rs_id == RS_OK:
					BigWorld.player().gotoDanceSpace( challengeIndex )	
			showMessage( mbmsgs[0x11a0] ,"", MB_OK_CANCEL, query )	
		else:
			BigWorld.player().gotoDanceSpace( selIndex )		
	
	def __updateDancersInfo( self,index, dancingKingInfos ):
		self.__pyDancersPanel.updateDancersInfo( index, dancingKingInfos )
		self.__updatePunishTime()
		
	def __updatePunishTime( self ):
		"""
		�����´���սʱ����ʾ
		"""
		punishTime = self.__getPunishTime()
		if punishTime > 0:
			self.__pyStTips.text = labelGather.getText( "HighDance:HighDance", "stNextChallengeTime" )% punishTime 
		else:
			self.__pyStTips.text = ""
			
	def __onReceiveDancerInfo( self, index, dancingKingInfo ):
		"""
		����������Ϣ
		"""
		self.__updateDancersInfo( index, dancingKingInfo )
		if index == self.__pyDancersPanel.selIndex:
			self.__pyDancersPanel.selIndex = -1		#ȡ��ѡ��
#		if not self.visible:
#			self.show()
		
	def __updateBtnState( self, index, result ):
		"""
		������ս��ť״̬�Լ�����ģ��
		"""
		if index != self.__pyDancersPanel.selIndex:return
		persistent = self.__getPunishTime()
		if result in [ csdefine.DANCE_CAN_CHALLENGE, csdefine.DANCE_CHALLENGE_LOWER_LEVEL_DANCER, csdefine.DANCE_POSITION_IS_EMPTY ] and persistent <= 0:
			self.__pyBtnChallenge.enable = True
		else:
			self.__pyBtnChallenge.enable = False
		self.__pyDancersPanel.pyItems[index].updateState( result )
		
		self.__setModeInfo()	#ˢ��һ��ģ����Ϣ
		
	def __getPunishTime( self ):
		"""
		��ȡ��ȴ��սʱ��
		"""
		persistent = -1
		for buffItem in BigWorld.player().attrBuffItems:
			if buffItem.baseItem.getBuffID() == "022137":
				persistent =  buffItem.leaveTime
		return persistent
	
	def __setModeInfo( self ):
		"""
		����ģ����Ϣ
		"""
		selIndex = self.__pyDancersPanel.selIndex
		if selIndex < 0:
			self.__pyStRoleName.text = ""
			self.__modelRender.clearModel()
		else:
			kingInfo = self.__pyDancersPanel.pyItems[selIndex].kingInfo
			roleModelInfo = kingInfo["modelInfo"]
			if roleModelInfo is None:
				self.__pyStRoleName.text = ""
				self.__modelRender.clearModel()	
				return
			fashionNum = roleModelInfo["fashionNum"]
			self.__modelRender.resetModel( roleModelInfo, fashionNum )	
			roleName = roleModelInfo["roleName"]	
			self.__pyStRoleName.text = roleName
			
	def __getIndexState( self, index ):
		if index == 1:
			return csdefine.DANCER_GOLDEN
		elif index in [2, 3, 4]:
			return csdefine.DANCER_SILVER
		elif index in [5,6,7,8,9]:
			return csdefine.DANCER_COPPER
		elif index >= 10 and index <= 19:
			return csdefine.DANCER_CANDIDATE
		else:
			return csdefine.DANCER_NONE
		
	def allClear(self ):
		"""
		���ģ��
		"""
		self.__modelRender.clearModel()
	
	def show( self ):
		self.__modelRender.enableDrawModel()
		self.__setModeInfo()
		Window.show( self )
	
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )
		
	def hide( self ):
		self.__modelRender.disableDrawModel()
		self.allClear()
		Window.hide( self )
		
	def onLeaveWorld( self ) :
		self.hide()
		

class DancersPanel( Control ):
	def __init__( self, panel ):
		Control.__init__( self, panel )
		self.__selIndex = -1	
		self.__pyItems = {}
		self.__mouseUpSelect = False			# �������ʱѡ��ѡ��
		self.__initialize( panel )
		
	def __initialize( self, panel ):
		for name, item in panel.children:
			if name.startswith("item_"):
				index = name.split("item_")[1]
				index = int( index )
				pyItem = Header( index + 1, item, self )	#����λ��������1��ʼ
				self.__pyItems[index+1] = pyItem
				
	def updateDancersInfo( self, index, dancingKingInfos ):
		"""
		���¸�����������Ϣ
		"""
		pyItem = self.__pyItems[index]
		pyItem.update( dancingKingInfos )
	
	def getIndexByName( self, roleName ):
		"""
		����������ֻ�ȡ����������λ������
		"""
		index = 0
		for pyItem in self.pyItems.itervalues():
			modelInfo = pyItem.kingInfo["modelInfo"]
			if modelInfo is not None and modelInfo["roleName"] == roleName:
				index = pyItem.itemIndex
		return index	
	
				
	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����¼�
		"""
		Control.generateEvents_( self )
		self.__onItemSelectChanged = self.createEvent_( "onItemSelectChanged" )	
		
	@property
	def onItemSelectChanged( self ) :							# ĳ��ѡ��ѡ��ʱ������
		return self.__onItemSelectChanged
		
	# ----------------------------------------------------------------
	# friend methods of ViewItem
	# ----------------------------------------------------------------
	def onViewItemLMouseDown_( self, pyItem, mods ) :
		"""
		��������ĳ��ѡ���ϰ���ʱ������
		"""
		if  not self.__mouseUpSelect :
			self.selIndex = pyItem.itemIndex
		return Control.onLMouseDown_( self, mods )

	def onViewItemLMouseUp_( self, pyItem, mods ) :
		"""
		��������ĳѡ��������ʱ������
		"""
		if self.__mouseUpSelect :
			self.selIndex = pyItem.itemIndex
		return Control.onLMouseUp_( self, mods )
		
	def onViewItemLClick_( self, pyItem, mods ):
		BigWorld.player().base.canChallengeDanceKing( pyItem.itemIndex )
		return Control.onLClick_( self, mods )
		
	def onItemSelectChanged_( self, index ) :
		"""
		��ǰѡ��ѡ��ı�ʱ������
		"""
		self.onItemSelectChanged( index )	
	#--------------------------------------------------------	
	def __selItem( self, index ):
		oldIndex = self.__selIndex
		if oldIndex > 0:
			self.__pyItems[oldIndex].setCommonLight()	#ȡ��ѡ�б���
		self.__selIndex = index
		try:
			self.__pyItems[index].setHighLight()	#�����µ�ѡ�б���
		except:
			pass
	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------	
	def _getSelIndex( self ) :
		return self.__selIndex

	def _setSelIndex( self, index ) :
		if index > self.itemCount :
			raise IndexError( "index %i is out of range!" % index )
		if index == self.__selIndex : return
		self.__selItem( index )
		self.onItemSelectChanged_( index )
		
	def _getItemCount( self ) :
		return len( self.__pyItems )
		
	def _getPyItems( self ):
		return self.__pyItems
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	selIndex = property( _getSelIndex, _setSelIndex )	
	itemCount = property( _getItemCount )
	pyItems = property( _getPyItems )		

class Header( Control ) :

	def __init__( self, index, header, pyPanel ) :
		Control.__init__( self, header )
		self.__pyPanel = pyPanel
		self.__insideCircle = header.inside_circle
		self.focus = True
		self.crossFocus = False
		
		self.kingInfo = {'isChallenge': False, 'modelInfo': None, 'Time': 0}
		self.__itemIndex = index	#����λ������
		self.__selected = False
		self.__state = 0	
		self.__pyRoleName = StaticText( header.st_name )
		self.__pyRoleName.text = ""		

	# ----------------------------------------------------------------
	# private
	def __setHeadTx( self, headTextureID ) :
		"""
		����ͷ��
		"""
		if headTextureID is not None:
			headTexturePath = rds.iconsSound.getHeadTexturePath( headTextureID )
			self.gui.header.textureName = headTexturePath
		else:
			self.gui.header.textureName = ""
		
	def __getDurationStr( self, duration ):
		"""
		��ʽ��ʱ��
		"""
		timeStr = ""
		hours = 0
		mins = 0
		if duration > 0:
			hours = duration / 3600.0
			mins = ( duration - hours *3600 )/60.0
		timeStr = labelGather.getText("HighDance:HighDance", "timeStr" )%( hours, mins )
		return timeStr	
	
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, dancingKingInfos ) :
		"""
		��������
		"""
		self.kingInfo = dancingKingInfos
		modelInfo = self.kingInfo["modelInfo"]
		if modelInfo is None:
			self.__pyRoleName.text = ""
			self.__setHeadTx( None )
		else:
			roleName = modelInfo.get("roleName")
			headTextureID = modelInfo.get("headTextureID")
			self.__pyRoleName.text = roleName
			self.__setHeadTx( headTextureID )
		self.crossFocus = self.kingInfo["modelInfo"] is not None
		
	def updateState( self, state ):
		self.__state = state
		
	def setCommonLight( self ):
		self.__insideCircle.mapping = util.getStateMapping( ( 64, 64 ), ( 1, 2 ),(1,1 ) )
		
	def setHighLight( self ):
		self.__insideCircle.mapping = util.getStateMapping( ( 64, 64 ), ( 1, 2 ),(1,2 ) )

	# -------------------------------------------------
	def onLMouseDown_( self, mods ) :
		return self.pyPanel.onViewItemLMouseDown_( self, mods )

	def onLMouseUp_( self, mods ) :
		return self.pyPanel.onViewItemLMouseUp_( self, mods )

	def onLClick_( self, mods ) :
		return self.pyPanel.onViewItemLClick_( self, mods )
		
	def onMouseEnter_( self ) :
		if self.kingInfo is None:return
		startTime = self.kingInfo["Time"]	#���迪ʼʱ��
		duration = time.time() - startTime
		durationStr = self.__getDurationStr( duration )
		dsp = self.kingInfo["modelInfo"].get("roleName")
		dsp += PL_NewLine.getSource()
		dsp += labelGather.getText("HighDance:HighDance", "goldenDancer")
		dsp += PL_NewLine.getSource()
		dsp += labelGather.getText("HighDance:HighDance", "dancerInfoTips")%( durationStr )
		toolbox.infoTip.showToolTips( self, dsp )
		self.setHighLight()
		return True			

	def onMouseLeave_( self ) :
		toolbox.infoTip.hide()
		if self.__itemIndex != self.pyPanel.selIndex:
			self.setCommonLight()
		return True

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getItemIndex( self ) :
		return self.__itemIndex

	def _getSelected( self ) :
		return self.__itemIndex == self.pyPanel.selIndex

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyPanel = property( lambda self : self.__pyPanel ) 		# ��ȡ�������б����
	itemIndex = property( _getItemIndex )					# ��ȡ��Ӧѡ�����б�����е�����
	selected = property( _getSelected )						# ��ȡ��ѡ���Ƿ��Ǳ�ѡ��ѡ��
	
class DancerModelRender( TargetModelRenderRemote ):
	def onModelCreated_( self, model ):
		self.modelZ = -1
		rds.actionMgr.playAction( model, "dance" )