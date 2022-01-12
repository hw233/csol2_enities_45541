#-*- coding: gb18030 -*-

# implement circle health point gui, HP reduces clockwise
# and increases anticlockwise.
# written by gjx 2013-4-1

import GUI
from guis.UIFixer import uiFixer
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from guis.controls.CircleShader import CircleShader
from AbstractTemplates import Singleton
import event.EventCenter as ECenter


class Light:

	def __init__(self, gui, threshold):
		self._gui = gui
		self._fader = GUI.AlphaShader()
		self._fader.speed = 0.5
		self._gui.addShader(self._fader)
		self._threshold = threshold

	def light(self):
		self._fader.value = 1.0

	def fade(self):
		self._fader.value = 0.0

	def update(self, value):
		if value < self._threshold:
			self.fade()
		else:
			self.light()


class CircleHPBar( Window, Singleton ):

	def __init__( self ):
		gui = GUI.load("guis/otheruis/circlehpbar/circlehpbar.gui")
		uiFixer.firstLoadFix(gui)
		Window.__init__( self, gui )
		#self.movable_ = False
		self.escHide_ = False
		self.v_dockStyle = "TOP"
		self.h_anchor = "LEFT"
		self.__fires = []
		self.__initialize(gui)
		self.__onHPChanged(1.0)
		self.addToMgr()

	def __initialize( self, gui ):
		self.__fires.append(Light(gui.fire_100p, 100))		# 100%处有一个火源
		self.__fires.append(Light(gui.fire_75p, 75))		# 75%处有一个火源
		self.__fires.append(Light(gui.fire_50p, 50))		# 50%处有一个火源
		self.__fires.append(Light(gui.fire_25p, 25))		# 25%处有一个火源
		self.__pySTRemain = StaticText(gui.st_remain)
		self.__pySTRemain.font = "blueitalic.font"
		self.__pySTRemain.charSpace = -17
		self.__pyHPBar = CircleShader(gui.hp_ring)

	def __onHPChanged( self, hpPercent ):
		for light in self.__fires:
			light.update(hpPercent)
		self.__pyHPBar.value = min(0.999, hpPercent/100.0)		# Circle有个bug，当值是1时，ui会看不到
		self.__pySTRemain.text = "%d:" % hpPercent

	def onLeaveWorld( self ):
		self.__class__.cls_trigger(False)

	@classmethod
	def cls_update( CLS, hpPercent ):
		if CLS.insted:
			CLS.inst.__onHPChanged( hpPercent )

	@classmethod
	def cls_trigger( CLS, visible ):
		if visible:
			if not CLS.inst.visible:
				CLS.inst.visible = True
		elif CLS.insted:
			CLS.inst.dispose()
			CLS.releaseInst()
