# -*- coding: gb18030 -*-

import time
import BigWorld
from guis import *
from guis.common.RootGUI import RootGUI
from AbstractTemplates import Singleton
from guis.controls.StaticText import StaticText

class CopyJueDiFanJiCount( RootGUI, Singleton ):

	__cg_bg = None

	def __init__( self ):
		Singleton.__init__( self )
		if CopyJueDiFanJiCount.__cg_bg is None :
			CopyJueDiFanJiCount.__cg_bg = GUI.load( "guis/general/spacecopyabout/spaceCopyJueDiFanJi/count.gui" )
		bg = util.copyGuiTree( CopyJueDiFanJiCount.__cg_bg )
		uiFixer.firstLoadFix( bg )
		RootGUI.__init__( self, bg )
		self.h_dockStyle = "CENTER"

		self.posZSegment = ZSegs.LMAX
		self.moveFocus = False
		self.escHide_ = False
		self.focus = False
		self.__stCount = bg.stCount
		self.__stCount.explicitSize = True
		self.__pyStCount = StaticText( self.__stCount )
		self.__pyStCount.focus = False
		self.__pyStCount.text = ""
		try :
			self.__pyStCount.font = "combtext.font"
		except :
			self.__pyStCount.font = "system_small.font"
			self.__pyStCount.font = "system_small.font"
		self.__unitSize = ( self.__stCount.width, self.__stCount.height )
		self.__primalSize = self.__unitSize
		self.__bgShader = bg.shader
		self.__bgShader.value = 1.0
		self.__textShader = self.__stCount.shader
		self.__textShader.value = 1.0
		self.__startTime = 0.0
		self.__lastTime = 0
		self.__textCBID = 0
		self.activable_ = False  # 窗口不被激活
		self.addToMgr()

	def showTimeCount( self, count ):
		"""
		开始连击
		"""
		self.__bgShader.value = 1.0
		BigWorld.cancelCallback( self.__textCBID )
		self.__textCBID = BigWorld.callback( 0.0, Functor( self.__flashText, count ) )
		self.visible = True

	def updatePosition_( self, passTime ) :
		"""
		"""
		if passTime < 0.4 :										# 缩放时缓慢上升
			self.bottom -= 10
		else :													# 回复后快速上升
			self.bottom -= 35 * 0.45 ** self.__delta
			self.__delta += 1

	def __updateColor( self, passTime ) :
		"""
		"""
		if passTime > self.__lastTime / 2 :
			self.__textShader.value *= 0.55
			self.__bgShader.value *= 0.55

	def __updateSize( self, passTime ) :
		"""
		"""
		# 先放大后缩小，在前面0.1秒放到最大，在随后的0.15秒内恢复回原始大小
		self.__stCount.width = linearScale( self.__primalSize[0], passTime )
		self.__stCount.height = linearScale( self.__primalSize[1], passTime )

	def __onUpdate( self ) :
		passTime = time.time() - self.__startTime
		if passTime >= self.__lastTime :
			self.__pyStCount.visible = False
			BigWorld.cancelCallback( self.__textCBID )
			self.__textCBID = 0
			self.visible = False
		else :
			self.__updateColor( passTime )
			self.__updateSize( passTime )
			self.__textCBID = BigWorld.callback( 0.06, self.__onUpdate )

	def __flashText( self, count ):
		"""
		当前连击数
		"""
		self.__startTime = time.time()
		self.__lastTime = 2.0
		self.__textShader.value = 1.0
		self.__pyStCount.text = str( count )
		units = len( str(count) )
		if units > 1:
			self.__pyStCount.font = "combtext.font"
		else:
			self.__pyStCount.font = "combtext_0.font"
		self.__primalSize = ( self.__unitSize[0]*units, self.__unitSize[1] )
		self.__pyStCount.visible = True
		self.__onUpdate()

def vx( va, vb, t, tx ):
	if tx <= t:
		return va + tx * (vb - va) / t
	else:
		return vb

def linearZoomOut( base, tx, t, maxScale ):
	"""
	线性缩小
	"""
	return vx(base * maxScale, base, t, tx)

def linearZoomIn( base, tx, t, maxScale ):
	"""
	线性放大
	"""
	return vx(base, base * maxScale, t, tx)

def linearScale( base, tx, zoomIn_t=0.12, zoomOut_t=0.15, maxScale=2.65 ):
	"""
	线性缩放，先放大然后恢复
	"""
	if tx <= zoomIn_t:
		return linearZoomIn(base, tx, zoomIn_t, maxScale)
	else:
		return linearZoomOut(base, tx-zoomIn_t, zoomOut_t, maxScale)
