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
	__cc_dpi = 2 * math.pi									# ���� 2�У���Ϊ���õ�

	"""
	ģ�� UI ���񣨼���ģ����ԭ�㣩
	"""
	def __init__( self, uiRender ) :
		if isDebuged :
			assert type( uiRender ) is GUI.Simple or type( uiRender ) is GUI.Circle, "ui render must be a GUI.Simple! or GUI.Circle"
		PyGUI.__init__( self, uiRender )
		self.__initialize( uiRender )
		self.__uiRender = uiRender

		# -----------------------------------
		# ģ��λ�����
		# -----------------------------------
		self.__offset = Math.Vector3( 0, 0, 0 )				# ģ��λ��ƫ��
		self.__yaw = 0.0									# ģ��ת��
		self.__pitch = 0.0									# ģ��ǰ����б
		self.__roll = 0.0									# ģ��������б

		# -----------------------------------
		# �������
		# -----------------------------------
		self.__action = "stand"								# ��ǰ���ڲ��ŵĶ���

		# -----------------------------------
		# �¼����
		# -----------------------------------
		self.__events = []									# �¼��б�
		self.generateEvents_()								# �����¼�

		self.materialFX = "SOLID"						# ���úͱ����Ļ��ģʽ

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
		self.__mdRender.lookFrom = ( 0, 0, 1 )				# ����Ĭ�ϵ����λ��
		self.__mdRender.lookAt = ( 0, 0, -1 )				# ����Ĭ�ϵĹ۲�����
		self.__mdRender.backgroundTextureName = ""			# ������ͼ
		self.__mdRender.enableDrawModel = False				# Ĭ�ϲ��򿪻�����


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def createEvent_( self, ename ) :
		event = ControlEvent( ename, self )
		self.__events.append( event )
		return event

	def generateEvents_( self ) :
		self.__onModelChanged = self.createEvent_( "onModelChanged" )	# ģ�͸���ʱ������

	@property
	def onModelChanged( self ) :
		return self.__onModelChanged


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onModelChanged_( self, oldModel ) :
		"""
		ģ�͸ı�ʱ������
		"""
		self.onModelChanged( oldModel )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setModel( self, model ) :
		"""
		����ģ��
		@type				model	 : BigWorld.Model
		@param				model	 : Ҫ�󶨸� UI ��ģ�ͣ������ None���������ǰʹ�õ�ģ�ͣ�
		@type				viewSite : flaot
		@viewSit			viewSite : ƽ��ģ��ʱ���ӵ�����ģ���ϵ�λ�ã�0.0 ��ʾ��(��)����0.5 ��ʾģ���м䣬1.0 ��ʾͷ����
		@return						 : None
		"""
		oldModel = self.model
		if model is None :															# Ϊ None ʱ�������ǰ���ӵ�ģ��
			self.__mdRender.models = []												# �����ɫģ��
			self.__uiRender.texture = None											# �������
			self.onModelChanged_( oldModel )										# ����ģ�ͱ����Ϣ
		elif not model.attached :
			self.__mdRender.models = [model]										# ����ģ��
			self.__mdRender.render()												# ��Ⱦģ��
			self.__uiRender.texture = self.__mdRender.texture						# ����ģ����ͼ
			self.autoAdapt()														# Ĭ���Զ�����
			self.__offset = Math.Vector3( model.position )							# ����ģ����Ĭ������µ�λ��ƫ��
			self.__action = "stand"													# ��������Ĭ�϶���
			self.playAction()														# ����stand����
			self.onModelChanged_( oldModel )										# ����ģ�ͱ����Ϣ
		else :																		# ģ���Ѿ������ӵ������Ⱦ��
			ERROR_MSG( "attach model fail, because the model has been attached!" )

	# ---------------------------------------
	def autoAdapt( self ) :
		"""
		�Զ�����
		"""
		model = self.model
		if not model : return
		self.__yaw = 0.0
		self.__pitch = 0.0
		self.__roll = 0.0
		model.straighten()
		matrix = Math.Matrix( model.bounds )
		mwidth = matrix.get( 0, 0 )								# ģ�Ϳ��
		mheight = matrix.get( 1, 1 )							# ģ�͸߶�
		mthick = matrix.get( 2, 2 )								# ģ�ͺ��
		y = -mheight / 2										# ��Ϊ�۲���ڽ�
		z = y / math.tan( BigWorld.projection().fov / 2 )		# ����ģ�͸߶������� Z ��λ��
																# ���������Ǽ���߶ȱ���סΪǰ���
																# �������Ǳ���ģ�ͣ���������ò���
																# ��Ϊ�󲿷�ģ�Ͷ��ǡ��ߡ��͵ģ��������Ĭ�����������÷�ʽ
		model.position = 0.0, y, z

	# -------------------------------------------------
	def playAction( self, actionName = "stand" ) :
		"""
		����ָ����ģ�Ͷ���
		"""
		self.__action = actionName
		rds.actionMgr.playAction( self.model, actionName )

	def stopAction( self ) :
		"""
		ֹͣ����
		"""
		rds.actionMgr.stopAction( self.model, self.__action )

	# -------------------------------------------------
	def enableDrawModel( self ) :
		"""
		����ģ���ػ�
		"""
		self.__mdRender.enableDrawModel = True

	def disableDrawModel( self ) :
		"""
		�ر�ģ���ػ�
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
	# ������
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
	# ģ�����
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
	model = property( _getModel )											# ��ȡ���ӵ���Ⱦ����ģ��
	bgTexture = property( _getBGTexture, _setBGTexture )					# ������ͼ

	# ������
	lookFrom = property( _getLookFrom, _setLookFrom )						# ��ȡ/�������λ��
	lookAt = property( _getLookAt, _setLookAt )								# ��ȡ/��������۲�����

	# ģ�����
	modelPos = property( _getModelPos, _setModelPos )						# ��ȡ/����ģ��λ��
	modelX = property( _getModelX, _setModelX )								# ��ȡ/����ģ�� X λ��
	modelY = property( _getModelY, _setModelY )								# ��ȡ/����ģ�� Y λ��
	modelZ = property( _getModelZ, _setModelZ )								# ��ȡ/����ģ�� Z λ��
	yaw = property( _getYaw, _setYaw )										# ��ȡ/����ģ��ת��
	pitch = property( _getPitch, _setPitch )								# ��ȡ/����ģ��ǰ����б��
	roll = property( _getRoll, _setRoll )									# ��ȡ/����ģ��������б��
