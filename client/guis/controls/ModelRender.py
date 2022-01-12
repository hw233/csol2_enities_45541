# -*- coding: gb18030 -*-
#
# $Id: ModelRender.py,v 1.6 2008-08-28 03:53:55 huangyongwei Exp $

"""
implement model render gui

2008/07/29: writen by huangyongwei
"""

"""
composing :
	GUI.Simple

"""

import math
import csarithmetic
from guis import *
from guis.common.PyGUI import PyGUI
from gbref import rds

class ModelRender( PyGUI ) :
	__cc_dpi = 2 * math.pi									# 保存 2π，因为常用到

	"""
	模型 UI 镜像（假设模型在原点）
	"""
	def __init__( self, uiRender ) :
		if isDebuged :
			assert type( uiRender ) is GUI.Simple or type( uiRender ) is GUI.Circle, "ui render must be a GUI.Simple! or GUI.Circle"
		PyGUI.__init__( self, uiRender )
		self.__initialize( uiRender )
		self.__uiRender = uiRender

		# -----------------------------------
		# 模型位置相关
		# -----------------------------------
		self.__offset = Math.Vector3( 0, 0, 0 )				# 模型位置偏移
		self.__yaw = 0.0									# 模型转向
		self.__pitch = 0.0									# 模型前后倾斜
		self.__roll = 0.0									# 模型左右倾斜

		# -----------------------------------
		# 动作相关
		# -----------------------------------
		self.__action = "stand"								# 当前正在播放的动作

		# -----------------------------------
		# 事件相关
		# -----------------------------------
		self.__events = []									# 事件列表
		self.generateEvents_()								# 生成事件

		self.materialFX = "SOLID"						# 设置和背景的混合模式

	def __del__( self ) :
		if Debug.output_del_ModelRender :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, uiRender ) :
		uiRender.tiled = False
		width = 2 ** math.ceil( math.log( self.width, 2 ) )
		height = 2 ** math.ceil( math.log( self.height, 2 ) )
		mleft = ( width - self.width ) / 2
		mtop = ( height - self.height ) / 2
		mright = width - mleft
		mbottom = height - mtop
		uiRender.mapping = util.getGuiMapping( ( width, height ), mleft, mright, mtop, mbottom )

		self.__mdRender = BigWorld.PyModelNoAlphaRenderer( int( width ), int( height ) )
		self.__mdRender.dynamic = True
		self.__mdRender.lookFrom = ( 0, 0, 1 )				# 设置默认的相机位置
		self.__mdRender.lookAt = ( 0, 0, -1 )				# 设置默认的观察向量
		self.__mdRender.backgroundTextureName = ""			# 背景贴图
		self.__mdRender.enableDrawModel = False				# 默认不打开画操作


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def createEvent_( self, ename ) :
		event = ControlEvent( ename, self )
		self.__events.append( event )
		return event

	def generateEvents_( self ) :
		self.__onModelChanged = self.createEvent_( "onModelChanged" )	# 模型更换时被触发

	@property
	def onModelChanged( self ) :
		return self.__onModelChanged


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onModelChanged_( self, oldModel ) :
		"""
		模型改变时被调用
		"""
		self.onModelChanged( oldModel )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setModel( self, model ) :
		"""
		设置模型
		@type				model	 : BigWorld.Model
		@param				model	 : 要绑定给 UI 的模型（如果是 None，则清除当前使用的模型）
		@type				viewSite : flaot
		@viewSit			viewSite : 平视模型时，视点落在模型上的位置（0.0 表示脚(底)部，0.5 表示模型中间，1.0 表示头部）
		@return						 : None
		"""
		oldModel = self.model
		if model is None :															# 为 None 时，清除当前附加的模型
			self.__mdRender.models = []												# 清除着色模型
			self.__uiRender.texture = None											# 清除贴面
			self.onModelChanged_( oldModel )										# 触发模型变更消息
		elif not model.attached :
			self.__mdRender.models = [model]										# 设置模型
			self.__mdRender.render()												# 渲染模型
			self.__uiRender.texture = self.__mdRender.texture						# 设置模型贴图
			self.autoAdapt()														# 默认自动适配
			self.__offset = Math.Vector3( model.position )							# 设置模型在默认情况下的位置偏移
			self.__action = "stand"													# 重新设置默认动作
			self.playAction()														# 播放stand动作
			self.onModelChanged_( oldModel )										# 触发模型变更消息
		else :																		# 模型已经被附加到别的渲染器
			ERROR_MSG( "attach model fail, because the model has been attached!" )

	# ---------------------------------------
	def autoAdapt( self ) :
		"""
		自动适配
		"""
		model = self.model
		if not model : return
		self.__yaw = 0.0
		self.__pitch = 0.0
		self.__roll = 0.0
		model.straighten()
		matrix = Math.Matrix( model.bounds )
		mwidth = matrix.get( 0, 0 )								# 模型宽度
		mheight = matrix.get( 1, 1 )							# 模型高度
		mthick = matrix.get( 2, 2 )								# 模型厚度
		y = -mheight / 2										# 因为观察点在脚
		z = y / math.tan( BigWorld.projection().fov / 2 )		# 根据模型高度来设置 Z 轴位置
																# 这种做法是假设高度被遮住为前提的
																# 因此如果是扁形模型，则这个设置不对
																# 因为大部分模型都是“高”型的，因此这里默认用这种设置方式
		model.position = 0.0, y, z

	# -------------------------------------------------
	def playAction( self, actionName = "stand" ) :
		"""
		播放指定的模型动作
		"""
		self.__action = actionName
		rds.actionMgr.playAction( self.model, actionName )

	def stopAction( self ) :
		"""
		停止动作
		"""
		rds.actionMgr.stopAction( self.model, self.__action )

	# -------------------------------------------------
	def enableDrawModel( self ) :
		"""
		开启模型重画
		"""
		self.__mdRender.enableDrawModel = True

	def disableDrawModel( self ) :
		"""
		关闭模型重画
		"""
		self.__mdRender.enableDrawModel = False


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getModel( self ) :
		if len( self.__mdRender.models ) :
			return self.__mdRender.models[0]
		return None

	# -------------------------------------------------
	# 相机相关
	# -------------------------------------------------
	def _getLookFrom( self ) :
		return self.__mdRender.lookFrom

	def _setLookFrom( self, lookFrom ) :
		self.__mdRender.lookFrom = lookFrom

	def _getLookAt( self ) :
		return self.__mdRender.lookAt

	def _setLookAt( self, lookAt ) :
		self.__mdRender.lookAt = lookAt


	# -------------------------------------------------
	# 模型相关
	# -------------------------------------------------
	def _getModelPos( self ) :
		model = self.model
		if not model : return Math.Vector3( 0, 0, 0 )
		return model.position - self.__offset

	def _setModelPos( self, pos ) :
		model = self.model
		if not model : return
		model.position = pos + self.__offset

	def _getModelX( self ) :
		model = self.model
		if not model : return 0.0
		return model.position.x - self.__offset.x

	def _setModelX( self, newx ) :
		model = self.model
		if not model : return
		x, y, z = self.modelPos
		self.modelPos = newx, y, z

	def _getModelY( self ) :
		model = self.model
		if not model : return 0.0
		return model.position.y - self.__offset.y

	def _setModelY( self, newy ) :
		model = self.model
		if not model : return
		x, y, z = self.modelPos
		self.modelPos = x, newy, z

	def _getModelZ( self ) :
		model = self.model
		if not model : return 0.0
		return model.position.z - self.__offset.z

	def _setModelZ( self, newz ) :
		model = self.model
		if not model : return
		x, y, z = self.modelPos
		self.modelPos = x, y, newz

	# ---------------------------------------
	def _getYaw( self ) :
		return self.__yaw

	def _setYaw( self, yaw ) :
		model = self.model
		if not model : return
		self.__yaw = yaw % self.__cc_dpi
		model.yaw = self.__yaw

	def _getPitch( self ) :
		return self.__pitch

	def _setPitch( self, pitch ) :
		model = self.model
		if not model : return
		pitch %= self.__cc_dpi
		delta = pitch - self.__pitch
		self.__pitch = pitch
		model.rotate( delta, ( 1, 0, 0 ) )

	def _getRoll( self ) :
		return self.__roll

	def _setRoll( self, roll ) :
		model = self.model
		if not model : return
		roll %= self.__cc_dpi
		delta = roll - self.__roll
		self.__roll = roll
		model.rotate( delta, ( 0, 0, 1 ) )

	# ------------------------------------------------
	def _getBGTexture( self ):
		return self.__mdRender.backgroundTextureName

	def _setBGTexture( self, bgTexturePath ):
		self.__mdRender.backgroundTextureName = bgTexturePath


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	model = property( _getModel )											# 获取附加到渲染器的模型
	bgTexture = property( _getBGTexture, _setBGTexture )					# 背景贴图

	# 相机相关
	lookFrom = property( _getLookFrom, _setLookFrom )						# 获取/设置相机位置
	lookAt = property( _getLookAt, _setLookAt )								# 获取/设置相机观察向量

	# 模型相关
	modelPos = property( _getModelPos, _setModelPos )						# 获取/设置模型位置
	modelX = property( _getModelX, _setModelX )								# 获取/设置模型 X 位置
	modelY = property( _getModelY, _setModelY )								# 获取/设置模型 Y 位置
	modelZ = property( _getModelZ, _setModelZ )								# 获取/设置模型 Z 位置
	yaw = property( _getYaw, _setYaw )										# 获取/设置模型转向
	pitch = property( _getPitch, _setPitch )								# 获取/设置模型前后倾斜度
	roll = property( _getRoll, _setRoll )									# 获取/设置模型左右倾斜度
