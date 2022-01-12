# -*- coding: gb18030 -*-
#
# $Id: ModelPanel.py,fangpengjun Exp $

"""
implement ModelPanel
"""
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.SelectableButton import SelectableButton
from NPCModelLoader import NPCModelLoader
g_npcmodel = NPCModelLoader.instance()

class ModelPanel( Control ):
	def __init__( self, index, panel ):
		Control.__init__( self, panel )
		self.index = index
		self.__selected = False
		self.__turnModelCBID = 0
		self.__pyModelBg = PyGUI( panel.modelBg )

		self.__pyModelRender = CommisRender( panel.modelRender )

		self.__pyStModelName = StaticText( panel.stModelName )
		self.__pyStModelName.text = ""

		self.__pyLeftBtn = Button( panel.leftBtn )
		self.__pyLeftBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyLeftBtn.onLMouseDown.bind( self.__turnLeft )

		self.__pyRightBtn = Button( panel.rightBtn )
		self.__pyRightBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyRightBtn.onLMouseDown.bind( self.__turnRight )

		self.__pySelectBtn = SelectableButton( panel.selectBtn )
		self.__pySelectBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pySelectBtn.onLClick.bind( self.__onSelected )

	def __turnLeft( self ):
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( False )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __turnRight( self ):
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( True )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __onLastKeyUpEvent( self, key, mods ) :
		if key != KEY_LEFTMOUSE : return
		BigWorld.cancelCallback( self.__turnModelCBID )
		LastKeyUpEvent.detach( self.__onLastKeyUpEvent )

	def __turnModel( self, isRTurn ) :
		"""
		turning model on the mirror
		"""
		self.__pyModelRender.yaw += ( isRTurn and -0.1 or 0.1 )
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) :
			self.__turnModelCBID = BigWorld.callback( 0.1, Functor( self.__turnModel, isRTurn ) )

	def __onSelected( self ):
		if self.selected:return
		ECenter.fireEvent( "EVT_ON_COMMISSION_MODEL_SELECTED", self.index )

	def setModel( self, modelNum ):
		self.__pyModelRender.resetModel( modelNum, False )

	def enableDrawModel( self ):
		"""
		����ģ����Ⱦ
		"""
		self.__pyModelRender.enableDrawModel( )

	def disableDrawModel( self ):
		"""
		�ر�ģ����Ⱦ
		"""
		self.__pyModelRender.disableDrawModel( )

	def _getSelected( self ):
		return self.__selected

	def _setSelected( self, selected ):
		self.__selected = selected
		self.__pySelectBtn.selected = selected
		if selected:
			util.setGuiState( self.__pyModelBg.getGui(), ( 1, 3 ), ( 1, 2 ) )
		else:
			util.setGuiState( self.__pyModelBg.getGui(), ( 1, 3 ), ( 1, 1 ) )

	selected = property( _getSelected, _setSelected )

# --------------------------------------------------------------------
from guis.controls.AdjModelRender import AdjModelRender
from TongBeastData import TongBeastData
tongBeastData = TongBeastData.instance()

class CommisRender( AdjModelRender ) :
	__cc_config = "config/client/uimodel_configs/commission.py"

	def __init__( self, mirror ) :
		AdjModelRender.__init__( self, mirror, -1, self.__cc_config )
		self.bgTexture = ""						# ������ͼguis/general/tongabout/shenshoubeckon/modelbg.tga
		self.cfgKey_ = "" #ģ��id

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onModelCreated( self, modelNumber, model ) :
		"""
		����ģ�ͻص�
		"""
		if model is None :
			self.cfgKey_ = ""
			# "����ģ��ʧ�ܣ�"
			showMessage( 0x0281, "", MB_OK, pyOwner = self )
		self.setModel( model )
#		self.enableDrawModel()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def resetModel( self, modelNumber, bgCreate = True ) :
		"""
		��������ģ��
		@type			modelNumber : INT32
		@param			modelNumber : ģ�� ID
		@type			bgCreate	: bool
		@param			bgCreate	: �Ƿ��ں�̨����ģ��
		@return					 	: None
		"""
		if self.cfgKey_ == modelNumber :
			return
		else:
			self.cfgKey_ = modelNumber
			self.__pyStModelName = g_npcmodel.getModelName( self.cfgKey_ )
		if bgCreate :
			rds.npcModel.createDynamicModelBG( modelNumber, Functor( self.__onModelCreated, modelNumber ) )
		else :
			try :
				model = rds.npcModel.createDynamicModel( modelNumber )
			except :
				model = None
#			if self.cfgKey_ != modelNumber :
#				return
			self.__onModelCreated ( modelNumber, model )

	# -------------------------------------------------
	def getViewInfos( self ) :
		"""
		��ȡ����ģ����Ϣ
		"""
		modelName = g_npcmodel.getModelName( self.cfgKey_ )
		pos = self.modelPos
		pitch = self.pitch
		yaw = self.yaw
		modelInfo = self.creatModelInfo_( self.cfgKey_, modelName, pos, pitch, yaw )
		return [modelInfo]											# ֻ������ǰְҵ

