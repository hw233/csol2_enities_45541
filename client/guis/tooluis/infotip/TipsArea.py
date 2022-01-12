# -*- coding: gb18030 -*-
#
# 由于这个脚本多处用到，因此单独抽出，方便共用
#
import GUI
import BigWorld
from guis.uidefine import ZSegs
from guis.common.RootGUI import RootGUI

# --------------------------------------------------------------------
# 提示区域
# --------------------------------------------------------------------
class TipsArea( RootGUI ) :
	def __init__( self, location, bound ) :
		tipsArea = GUI.Line( "guis/empty.dds" )
		tipsArea.innerColour = 255, 0, 0, 255
		tipsArea.edgeColour = 255, 0, 0, 255
		tipsArea.widthRelative = False
		tipsArea.heightRelative = False
		tipsArea.lineWidth = 1
		tipsArea.size = ( 0, 0 )
		RootGUI.__init__( self, tipsArea )
		self.addToMgr()
		self.posZSegment = ZSegs.L5
		self.movable_ = False
		self.activable_ = False
		self.hitable_ = False
		self.escHide_ = False
		self.focus = False

		self.__location = ( 0, 0 )
		self.__bound = bound
		self.relocate( location )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	bound = property( lambda self : self.__bound )
	location = property( lambda self : self.__location )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def relocate( self, location ) :
		"""
		创建指示区红色边框
		"""
		self.__location = location
		sw, sh = BigWorld.screenSize()
		bound = self.__bound
		minX = location[0] + bound.x - sw * 0.5
		minY = location[1] + bound.y - sh * 0.5
		maxX = bound.width + minX
		maxY = bound.height + minY
		tipsArea = self.gui
		tipsArea.clearNodes()
		tipsArea.pushNode( ( minX, -minY ) )
		tipsArea.pushNode( ( maxX, -minY ) )
		tipsArea.pushNode( ( maxX, -maxY ) )
		tipsArea.pushNode( ( minX, -maxY ) )
		tipsArea.pushNode( ( minX, -minY ) )
