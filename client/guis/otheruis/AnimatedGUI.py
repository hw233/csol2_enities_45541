# -*- coding: gb18030 -*-

# ǰ����FlashFlag��
# ����ʵ������˸�ؼ����ɼ̳���Control��Ϊ�̳���GUIBaseObject
# Ĭ�����������ؼ���������Ϣ���������Ҫ������Ϣ����˸�ؼ���
# ����ɴ��ټ̳г�һ���µ��ࡣ
# written by ganjinxing 2010-07-15

from guis import *
from guis.common.GUIBaseObject import GUIBaseObject


class AnimatedGUI( GUIBaseObject ) :

	def __init__( self, gui ) :
		GUIBaseObject.__init__( self, gui )

		self.__loopAmount = -1							# ѭ����˸���ٴκ��Զ�ֹͣ(Ϊ��������ѭ��)
		self.__loopSpeed = 1.0							# ÿ֡��ʱ�䣨��λ���룩
		self.__loopCounter = 0							# ��¼��ѭ�����ٴ�
		self.__frameAmount = 0							# �ܹ�����֡
		self.__frameIndex = 0							# ��ǰ�ǵڼ�֡
		self.__framesMapping = []						# ��¼ÿһ֡��mappingֵ
		self.__loopCBID = 0								# ѭ��timerID

	def __del__( self ) :
		if Debug.output_del_AnimatedGUI :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __loop( self ) :
		"""
		ѭ����˸
		"""
		if self.__frameIndex >= self.__frameAmount :	# ѭ����һȦ
			loopAmount = self.__loopAmount
			if loopAmount > 0 :							# ����趨��ѭ������
				self.__loopCounter += 1
				if self.__loopCounter >= loopAmount :	# ѭ�������ѵ�
					self.reset_()						# ѭ������
					self.stopPlay_()
					return
			self.__frameIndex = 0						# ���»ص���һ֡
		self.mapping = self.__framesMapping[self.__frameIndex]
		self.__frameIndex += 1
		self.__loopCBID = BigWorld.callback( self.__loopSpeed, self.__loop )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def stopPlay_( self ) :
		"""
		ֹͣ��˸
		"""
		if self.__loopCBID :
			BigWorld.cancelCallback( self.__loopCBID )
			self.__loopCBID = 0
			
	def reset_( self ) :
		"""
		���趯��������
		"""
		self.__frameIndex = 0							# ���»ص���һ֡
		self.__loopCounter = 0							# ����ѭ������
		self.visible = False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def playAnimation( self ) :
		"""
		���Ŷ��������ṩ�ֶ��������ŵĽӿڣ���Ҫ��ʼ��
		ʱ�����趨�ö����Ĳ��Ŵ�����ÿ֡���ٶȡ�
		"""
		self.stopPlay_()
		self.reset_()
		self.visible = True
		self.__loop()
		
	def initAnimation( self, loopAmount, frameAmount, mappingMode, orderStyle = "Z" ) :
		"""
		���ö�������
		@param		loopAmount	: ѭ��������Ϊ��������ѭ����
		@type		loopAmount	: int
		@param		frameAmount : ÿ��ѭ����֡��
		@type		frameAmount : int
		@param		mappingMode : ��ͼ��mappingģʽ
		@type		mappingMode : tuple with two elements
		@param		orderStyple : mapping��˳�򣨡�Z�����ߡ�N�����Σ�
		@type		orderStyple : character of "Z" or "N"( in upper case )
		"""
		self.__loopAmount = loopAmount
		self.__frameAmount = frameAmount
		util.setGuiState( self.gui, mappingMode )
		uiSize = self.size
		row, col = mappingMode
		self.__framesMapping = []
		orderStyle = orderStyle.upper()
		if orderStyle == "Z" :
			for i in xrange( 1, row + 1 ) :
				for j in xrange( 1, col + 1 ) :
					if frameAmount <= 0 : return
					frameAmount -= 1
					mapping = util.getStateMapping( uiSize, mappingMode, ( i, j ) )
					self.__framesMapping.append( mapping )
		elif orderStyle == "N" :
			for j in xrange( 1, col + 1 ) :
				for i in xrange( 1, row + 1 ) :
					if frameAmount <= 0 : return
					frameAmount -= 1
					mapping = util.getStateMapping( uiSize, mappingMode, ( i, j ) )
					self.__framesMapping.append( mapping )
		else :
			ERROR_MSG( "Error order style: %s! orderStyle must be \"Z\" or \"N\"." % orderStyle )
		self.reset_()


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getSpf( self ) :
		"""
		��ȡһ֡���ٶ�
		"""
		return self.__loopSpeed

	def _setSpf( self, spf ) :
		"""
		����һ֡���ٶ�
		"""
		self.__loopSpeed = spf

	def _getCycle( self ) :
		"""
		��ȡ����
		"""
		return self.__loopSpeed * self.__frameAmount

	def _setCycle( self, cycle ) :
		"""
		��������
		"""
		self.__loopSpeed = float( cycle ) / self.__frameAmount


	spf = property( _getSpf, _setSpf )					# ��ȡ/����ÿ֡��ʱ��( second per frame )
	cycle = property( _getCycle, _setCycle )			# ��ȡ/�������ڣ�ѭ��һ�ε�ʱ�䣩
