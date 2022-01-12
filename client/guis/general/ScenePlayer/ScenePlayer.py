# -*- coding: gb18030 -*-

import sys
import GUI
import time
import math
import Math
import BigWorld
import Language
from gbref import rds
from bwdebug import ERROR_MSG
from Function import Functor
from event import EventCenter as ECenter
from AbstractTemplates import MultiLngFuncDecorator
labelGather = sys.modules["LabelGather"].labelGather

from guis.UIFixer import uiFixer
from guis.uidefine import ZSegs, UIState
from guis.ExtraEvents import ControlEvent
from guis.controls.ButtonEx import HButtonEx
from guis.common.RootGUI import RootGUI
from guis.common.GUIBaseObject import GUIBaseObject
from guis.tooluis.CSRichText import CSRichText
from guis.ScreenViewer import ScreenViewer

VIEW_SIZE = ( 1024.0, 768.0 )						# 默认在此分辨率下配置剧情
PIECE_SIZE = 512.0									# 碎片的尺寸（长宽相等）
PRV_TIME = 0.5										# 预先加载0.5秒后将会出现的贴图


class FadingObject( object ) :
	"""alpha衰减器"""

	def __init__( self, gui ) :
		self.__fader = gui.fader

	def fadeout( self ) :
		self.__fader.value = 0

	def fadein( self ) :
		self.__fader.value = 1

	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getFader( self ) :
		return self.__fader

	def _getFadeSpeed( self ) :
		return self.__fader.speed

	def _setFadeSpeed( self, speed ) :
		self.__fader.speed = speed

	fader = property( _getFader )
	fadeSpeed = property( _getFadeSpeed, _setFadeSpeed )


class deco_initContent( MultiLngFuncDecorator ) :
	@staticmethod
	def locale_big5( SELF, font, size ) :
		"""
		"""
		deco_initContent.originalFunc( SELF, "MSJHBD.ttf", 24 )


class ScenePlayer( FadingObject, RootGUI ) :
	"""剧情播放器"""
	__cc_inst = None

	def __init__( self, gui = None ) :
		assert ScenePlayer.__cc_inst is None, "Invoke the getInst method, please!"
		if gui is None :
			gui = GUI.load( "guis/general/scenarioplayer/wnd.gui" )
			uiFixer.firstLoadFix( gui )
		FadingObject.__init__( self, gui )
		RootGUI.__init__( self, gui )
		self.movable_ = False
		self.escHide_ = False
		self.posZSegment = ZSegs.L1
		self.fadeout()
		self.__fadeinCbids = []
		self.__fadeoutCbids = []
		self.addToMgr()
		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

		self.__pyFresco = Fresco( gui.fresco )
		self.__motor = Motor( self.__pyFresco )					# 这里存在交叉引用，通过调用destroy来解除
		self.__motor.onArrive.bind( self.__onNodeArrive )

		self.__pyContent = FadingText( gui.rtx_content )		# 剧情文本
		self.__pyContent.align = "C"
		self.__pyContent.h_dockStyle = "CENTER"
		self.__pyContent.v_dockStyle = "BOTTOM"
		self.__initContent( "STXINWEI.TTF", 28 )

		self.__pyBtnHide = HButtonEx( gui.btn_hide )				# 关闭按钮
		self.__pyBtnHide.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnHide.onLClick.bind( self.__onHide )
		self.__pyBtnHide.h_dockStyle = "RIGHT"
		self.__pyBtnHide.v_dockStyle = "BOTTOM"
		self.__pyBtnHide.visible = False
		labelGather.setPyBgLabel( self.__pyBtnHide, "ScenePlayer:main", "btnHide" )

		self.__layout()

		# 添加清屏例外窗口
		ScreenViewer().addResistHiddenRoot(self)

	# -------------------------------------------------
	# private
	# -------------------------------------------------
	@deco_initContent
	def __initContent( self, font, fontSize ) :
		""""""
		self.__pyContent.font = font
		self.__pyContent.fontSize = fontSize

	def __browseFresco( self ) :
		"""浏览壁画"""
		self.__onNodeArrive( sceneLoader.getVertexs()[0] )

	def __onNodeArrive( self, dst_pos ) :
		"""已经到达到目标节点
		@param	dst_pos : 目标点坐标"""
		node = sceneLoader.getNode( dst_pos )
		if node is None :
			self.fadeaway()										# 找不到后续节点，结束
		else :
			if node.dwell_time > 0 :
				func = Functor( self.__motor.move,
								node.src_pos,
								node.dst_pos,
								node.duration )
				BigWorld.callback( node.dwell_time, func )
			else :
				self.__motor.move( node.src_pos,
									node.dst_pos,
									node.duration )
			if node.speech :
				rds.soundMgr.switchVoice( node.speech )			# 切换语音
			if node.content == "EOF" :							# 配置设置为隐藏文本
				self.__pyContent.fadeout()
			elif node.content :									# 如果有提示文本
				self.__pyContent.text = node.content
				self.__pyContent.fadein()

	def __layout( self ) :
		"""游戏分辨率改变"""
		global VIEW_SIZE
		self.size = BigWorld.screenSize()
		self.pos = 0, 0
		scale = max( self.width / VIEW_SIZE[0], self.height / VIEW_SIZE[1] )
		self.__pyFresco.zoom( scale )							# 按照大的比例进行缩放
		spacing = self.__pyBtnHide.left
		self.__pyContent.maxWidth = spacing - 40				# 自动调整文本显示的最大宽度
		self.__pyContent.left = ( spacing - self.__pyContent.maxWidth ) * 0.5

	def __onHide( self ) :
		"""点击按钮退出"""
		self.__pyBtnHide.visible = False
		self.fadeaway()

	def __cancelCallback( self, cbids ) :
		"""取消回调"""
		for cbid in cbids :
			BigWorld.cancelCallback( cbid )

	# -------------------------------------------------
	# public
	# -------------------------------------------------
	def play( self ) :
		"""播放剧情"""
		self.__cancelCallback( self.__fadeoutCbids )
		self.__fadeoutCbids = []
		self.__pyFresco.draw( sceneLoader.getTextureInfo() )
		self.__pyFresco.pos = sceneLoader.getVertexs()[0]
		ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", False )
		self.show()
		self.fadein()
		rds.soundMgr.lockBgPlay( False )						# 解锁背景音乐播放
		rds.soundMgr.stopMusic()								# 停止游戏音乐
		def callback() :
			if self.disposed : return							# 已经销毁
			self.__browseFresco()								# 浏览壁画
			rds.soundMgr.lockBgPlay( False )					# 解锁背景音乐播放（因为这个是callback，为防止意外，这里再解锁一次）
			bgMusic = sceneLoader.getBgMusic()
			rds.soundMgr.switchMusic( bgMusic )					# 播放背景音乐
			rds.soundMgr.lockBgPlay( True )						# 锁定背景音乐播放
			self.__pyBtnHide.visible = True
			self.__pyFresco.fadein()
		self.__fadeinCbids.append( \
			BigWorld.callback( self.fadeSpeed + 2, callback ) )

	def fadeaway( self ) :
		"""消逝，退出"""
		self.__cancelCallback( self.__fadeinCbids )
		self.__fadeinCbids = []
		rds.soundMgr.stopVoice()								# 停止旁白语音
		rds.soundMgr.lockBgPlay( False )						# 解锁背景音乐播放
		player = BigWorld.player()
		if player and player.isPlayer() :
			currArea = player.getCurrArea()
			music = ""
			if currArea :
				music = currArea.getMusic()
			rds.soundMgr.switchMusic( music )					# 音乐重设为玩家当前所在区域的音乐
		self.__pyFresco.fadeout()
		ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", True )		# 重新显示所有窗口
		def callback() :
			self.destroy()										# 销毁自身的实例
		self.__fadeoutCbids.append( \
			BigWorld.callback( self.__pyFresco.fadeSpeed * 0.5, self.fadeout ) )
		self.__fadeoutCbids.append( \
			BigWorld.callback( self.fadeSpeed + self.__pyFresco.fadeSpeed * 0.5, callback ) )

	def destroy( self ) :
		"""销毁播放器"""
		self.dispose()
		ECenter.unregisterEvent( "EVT_ON_RESOLUTION_CHANGED", self )
		self.__pyFresco.dispose()
		self.__motor.destroy()
		sceneLoader.clear()
		self.__class__.__cc_inst = None

	def __del__( self ) :
		RootGUI.__del__( self )
		print ">>>> Finally! I melt..."

	# -------------------------------------------------
	# class methods
	# -------------------------------------------------
	@classmethod
	def getInst( CLS ) :
		"""创建/获取实例"""
		return CLS.__cc_inst

	@classmethod
	def instance( CLS ) :
		"""创建/获取实例"""
		if CLS.__cc_inst is None :
			CLS.__cc_inst = CLS()
		return CLS.__cc_inst

	@classmethod
	def onDisplay( CLS, sceneId ) :
		"""
		"""
		if not sceneLoader.load( sceneId ) : return
		CLS.instance().play()

	@classmethod
	def registerEvents( CLS ) :
		"""注册触发事件"""
		ECenter.registerEvent( "EVT_ON_DISPLAY_SCENE", CLS )

	@classmethod
	def onEvent( CLS, evtMacro, *args ) :
		if evtMacro == "EVT_ON_RESOLUTION_CHANGED" :			# 分辨率改变的事件
			if CLS.__cc_inst :
				CLS.getInst().__layout()
		elif evtMacro == "EVT_ON_DISPLAY_SCENE" :
			CLS.onDisplay( *args )


class Fresco( FadingObject, GUIBaseObject ) :
	"""背景图画"""

	def __init__( self, gui ) :
		FadingObject.__init__( self, gui )
		GUIBaseObject.__init__( self, gui )
		self.fadeout()
		self.__moveSpeed = ( 0, 0 )					# 移动速度（获取碎片时需要）
		self.__orgn_size = gui.size					# 原始尺寸
		self.__scale = 1.0							# 缩放比例（按长宽比不变进行缩放）
		self.__txFolder = ""						# 贴图碎片的存放目录
		self.__pyIdleElem = []
		self.__pyElemMap = {}

	def dispose( self ) :
		GUIBaseObject.dispose( self )
		self.__pyIdleElem = []
		self.__pyElemMap = {}

	def draw( self, textureInfo ) :
		"""绘制图画"""
		self.__releasePieces( self.__pyElemMap.keys() )
		self.__orgn_size = textureInfo.size
		self.__txFolder = textureInfo.textureFolder
		self.size = textureInfo.size
		self.zoom( self.__scale )
		self.update( self.pos )

	def zoom( self, scale ) :
		"""缩放图画"""
		pos = self.pos								# 保存缩放前的位置
		self.width = self.__orgn_size[0] * scale
		self.height = self.__orgn_size[1] * scale
		self.__scale = scale
		self.pos = pos								# 重设位置
		self.__layout()

	def update( self, pos ) :
		"""更新壁画"""
		new_pieces = self.measurePieces( pos )
		old_pieces = self.__pyElemMap.keys()
		if new_pieces == old_pieces : return				# 需要显示的碎片没变
		pieces_out = set( old_pieces ) - set( new_pieces )
		self.__releasePieces( pieces_out )
		pieces_add = set( new_pieces ) - set( old_pieces )
		self.__combine( pieces_add )

	def measurePieces( self, pos ) :
		"""测量出所需加载的贴图碎片"""
		global VIEW_SIZE, PIECE_SIZE, PRV_TIME
		h_speed, v_speed = self.__moveSpeed
		view_top = pos[1] - VIEW_SIZE[1] * 0.5
		view_left = pos[0] - VIEW_SIZE[0] * 0.5
		view_right = view_left + VIEW_SIZE[0]
		view_bottom = view_top + VIEW_SIZE[1]
		t_pcount = int( ( view_top ) / PIECE_SIZE )						# 顶端的碎片数量
		l_pcount = int( ( view_left ) / PIECE_SIZE )					# 左边的碎片数量
		v_pright = l_pcount * PIECE_SIZE
		h_count = int( math.ceil( ( view_right - v_pright ) / PIECE_SIZE ) )
		h_pbottom = t_pcount * PIECE_SIZE
		v_count = int( math.ceil( ( view_bottom - h_pbottom ) / PIECE_SIZE ) )
		# 以下部分代码是根据移动速度的大小和方向来计算出需预加载的碎片
		if h_speed > 0 :												# 水平速度向右
			prv_dist = view_right + PRV_TIME * h_speed - PIECE_SIZE * ( l_pcount + h_count )
			if prv_dist > 0 :
				h_count += int( math.ceil( prv_dist / PIECE_SIZE ) )
		elif h_speed < 0 :												# 水平速度向左
			prv_dist = v_pright - view_left - PRV_TIME * h_speed
			if prv_dist > 0 :
				inc_count = int( math.ceil( prv_dist / PIECE_SIZE ) )
				h_count += inc_count
				l_pcount -= inc_count
		if v_speed > 0 :												# 垂直速度向下
			prv_dist = view_bottom + PRV_TIME * v_speed - PIECE_SIZE * ( t_pcount + v_count )
			if prv_dist > 0 :
				v_count += int( math.ceil( prv_dist / PIECE_SIZE ) )
		elif v_speed < 0 :												# 垂直速度向上
			prv_dist = h_pbottom - view_top - PRV_TIME * v_speed
			if prv_dist > 0 :
				inc_count = int( math.ceil( prv_dist / PIECE_SIZE ) )
				v_count += inc_count
				t_pcount -= inc_count
		# 以上部分代码是根据移动速度的大小和方向来计算出需预加载的碎片
		result = []
		for i in xrange( v_count ) :
			for j in xrange( h_count ) :
				result.append( ( t_pcount + i, l_pcount + j ) )
		return result

	def updateSpeed( self, speed ) :
		"""由外界通知速度更新"""
		self.__moveSpeed = speed

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __combine( self, pieces ) :
		"""将碎片拼合成完整的贴图"""
		path_fmt = self.__txFolder + "/p_%.2i.dds"
		colAmount = int( math.ceil( self.__orgn_size[0] / PIECE_SIZE ) )
		for piece in pieces :
			cb = Functor( self.__loadPieceCb, piece )
			BigWorld.fetchTexture( path_fmt % ( piece[0] * colAmount + piece[1] + 1 ), cb )

	def __loadPieceCb( self, piece, elem ) :
		"""碎片加载回调"""
		self.__pyElemMap[ piece ] = elem
		self.gui.addElement( elem, "p%i%i" % ( piece[0], piece[1] ) )
		elem.size.x = PIECE_SIZE * self.__scale
		elem.size.y = PIECE_SIZE * self.__scale
		elem.position.x = piece[1] * PIECE_SIZE * self.__scale
		elem.position.y = piece[0] * PIECE_SIZE * self.__scale

	def __getPieceElem( self ) :
		""""""
		if len( self.__pyIdleElem ) :
			return self.__pyIdleElem.pop()
		return GUI.Texture("")

	def __releasePieces( self, pieces ) :
		""""""
		for piece in pieces :
			elem = self.__pyElemMap.pop( piece )
			if elem is None : return
			self.gui.removeElement( elem )
			#self.__pyIdleElem.append( elem )

	def __layout( self ) :
		"""重新排列贴图的位置"""
		for ( i, j ), elem in self.__pyElemMap.iteritems() :
			elem.size.x = PIECE_SIZE * self.__scale
			elem.size.y = PIECE_SIZE * self.__scale
			elem.position.x = j * PIECE_SIZE * self.__scale
			elem.position.y = i * PIECE_SIZE * self.__scale

	# -------------------------------------------------
	# property
	# -------------------------------------------------
	def _setLeft( self, left ) :
		"""保持pos位于父窗口的中心点上"""
		left *= self.__scale
		parentHalfWidth = self.gui.parent.width * 0.5
		GUIBaseObject._setLeft( self, parentHalfWidth - left )
		self.update( self._getPos() )

	def _getLeft( self ) :
		"""pos是指贴图的那个点位于父窗口的中心"""
		left = GUIBaseObject._getLeft( self )
		return ( self.gui.parent.width * 0.5 - left ) / self.__scale

	def _setTop( self, top ) :
		"""保持pos位于父窗口的中心点上"""
		top *= self.__scale
		parentHalfHeihgt = self.gui.parent.height * 0.5
		GUIBaseObject._setTop( self, parentHalfHeihgt - top )
		self.update( self._getPos() )

	def _getTop( self ) :
		"""pos是指贴图的那个点位于父窗口的中心"""
		top = GUIBaseObject._getTop( self )
		return ( self.gui.parent.height * 0.5 - top ) / self.__scale

	def _setPos( self, ( left, top ) ) :
		"""pos是指贴图的那个点位于父窗口的中心"""
		self._setLeft( left )
		self._setTop( top )
		self.update( self._getPos() )

	def _getPos( self ) :
		"""pos是指贴图的那个点位于父窗口的中心"""
		return ( self._getLeft(), self._getTop() )

	left = property( _getLeft, _setLeft )
	top = property( _getTop, _setTop )
	pos = property( _getPos, _setPos )


class Motor( object ) :
	"""移动引擎"""

	__cc_interval = 0.02												# 滚动回调间隔，单位：秒

	def __init__( self, obj ) :
		object.__init__( self )
		self.__driveObj = obj
		self.__cbid = 0													# callback ID
		self.__speed = ( 0, 0 )											# 移动速度( 水平, 垂直 )
		self.__duration = 0												# 设定的移动时间
		self.__src_pos = ( 0, 0 )										# 移动的起始位置
		self.__dst_pos = ( 0, 0 )										# 移动的目标位置
		self.__startTime = 0											# 上一次回调的时间（用于计算两次回调的间隔）

		self.__onArrive = ControlEvent( "onArrive", self )				# 到达目的地事件

	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	@property
	def onArrive( self ) :
		return self.__onArrive

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def start( self ) :
		"""启动"""
		self.__moving()

	def shut( self ) :
		"""停机"""
		if self.__cbid :
			BigWorld.cancelCallback( self.__cbid )
			self.__cbid = 0

	def refresh( self, src, dst, duration ) :
		"""更新移动参数"""
		xs = ( dst[0] - src[0] ) / duration
		ys = ( dst[1] - src[1] ) / duration
		self.__speed = ( xs, ys )
		self.__driveObj.updateSpeed( self.__speed )
		self.__src_pos = src
		self.__dst_pos = dst
		self.__duration = duration

	def move( self, src, dst, duration ) :
		"""启程向目标点移动"""
		self.shut()
		if self.__driveObj is None : return
		self.refresh( src, dst, duration )
		self.__startTime = time.time()
		self.__moving()

	def destroy( self ) :
		"""销毁，清理掉数据"""
		self.shut()
		self.__driveObj = None

	@staticmethod
	def calcDistance( src, dst ) :
		"""计算两点之间的距离"""
		return math.sqrt( ( dst[0] - src[0] )**2 + ( dst[1] - src[1] )**2 )

	def isArrive( self ) :
		"""是否到达了目的地，根据两点之间的距离来大致判断"""
		return self.calcDistance( self.__driveObj.pos, self.__dst_pos ) < 0.5


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __moving( self ) :
		"""不停地移动，直到到达目的地"""
		moveTime = time.time() - self.__startTime
		if moveTime > self.__duration :
			self.__driveObj.pos = self.__dst_pos
			self.shut()
			self.onArrive( self.__dst_pos )
			return
		xd = self.__speed[0] * moveTime
		yd = self.__speed[1] * moveTime
		self.__driveObj.pos = ( self.__src_pos[0] + xd, self.__src_pos[1] + yd )
		self.__cbid = BigWorld.callback( self.__cc_interval, self.__moving )


class FadingText( FadingObject, CSRichText ) :
	"""剧情文字"""

	def __init__( self, gui ) :
		FadingObject.__init__( self, gui )
		CSRichText.__init__( self, gui )
		self.visible = 1
		self.fadeout()


class SceneLoader( object ) :

	__cc_inst = None
	__cc_config_path = "config/client/SceneDatas.xml"

	def __init__( self ) :
		assert SceneLoader.__cc_inst is None, "Invoke the getInst method, please!"
		object.__init__( self )
		self.__currSceneID = None
		self.__nodes = {}
		self.__bgMusic = ""
		self.__texture_info = TextureInfo()

	def load( self, sceneID ) :
		"""
		初始化剧情
		"""
		if sceneID == self.__currSceneID : return True				# 该剧情已导入
		sect = Language.openConfigSection( self.__cc_config_path )
		if sect is None :
			ERROR_MSG( "Open config %s fail. Please make sure this config exist!" % \
				self.__cc_config_path )
			return False
		Language.purgeConfig( self.__cc_config_path )
		self.__nodes = {}
		for scene in sect.values() :
			if scene.readInt( "id" ) == sceneID :
				self.__bgMusic = scene.readString( "bgMusic" )
				self.__texture_info.init( scene["texture"] )
				for segment in scene["segments"].values() :
					node = SceneNode( segment )
					self.__nodes[ node.src_pos ] = node
				if None not in self.getVertexs() :					# 这里检查节点的配置是否正确
					self.__currSceneID = sceneID
					return True
				break
		ERROR_MSG( "Can't find scene config by id %i." % sceneID )
		return False

	def getNode( self, src_pos ) :
		"""根据源位置获取对应的节点信息"""
		return self.__nodes.get( src_pos )

	def getVertexs( self ) :
		"""获取顶点坐标"""
		src_poss = set( self.__nodes.keys() )
		dst_poss = set( [n.dst_pos for n in self.__nodes.values()] )
		start_pos = src_poss - dst_poss
		tail_pos = dst_poss - src_poss
		result = [ None, None ]
		if len( start_pos ) == 1 :
			result[0] = list( start_pos )[0]
		elif len( start_pos ) > 1 :
			ERROR_MSG( ">>>>> More than 1 start nodes found! Please check the config." )
		elif len( start_pos ) == 0 :
			ERROR_MSG( ">>>>> Can't find start node! Please check the config." )
		if len( tail_pos ) == 1 :
			result[1] = list( tail_pos )[0]
		elif len( tail_pos ) > 1 :
			ERROR_MSG( ">>>>> More than 1 tail nodes found! Please check the config." )
		elif len( tail_pos ) == 0 :
			ERROR_MSG( ">>>>> Can't find tail node! Please check the config." )
		return result

	def getTextureInfo( self ) :
		return self.__texture_info

	def getBgMusic( self ) :
		return self.__bgMusic

	def clear( self ) :
		"""
		清理掉不再需要的数据
		"""
		self.__currSceneID = None
		self.__nodes = {}

	@classmethod
	def getInst( CLS ) :
		if CLS.__cc_inst is None :
			CLS.__cc_inst = CLS()
		return CLS.__cc_inst


class TextureInfo( object ) :

	def __init__( self ) :
		self.__texture_folder = None
		self.__size = ( 0, 0 )

	def init( self, sect ) :
		self.__texture_folder = sect.readString( "path" )
		self.__size = ( sect.readInt( "width" ), sect.readInt( "height" ) )

	@property
	def textureFolder( self ) :
		return self.__texture_folder

	@property
	def size( self ) :
		return self.__size


class SceneNode( object ) :
	"""剧情节点"""
	def __init__( self, sect ) :
		object.__init__( self )
		self.__src_pos = tuple( sect.readVector2( "src_pos" ) )
		self.__dst_pos = tuple( sect.readVector2( "dst_pos" ) )
		self.__duration = sect.readFloat( "duration" )
		self.__dwell_time = sect.readFloat( "dwell_time" )
		self.__content = sect.readString( "content" )
		self.__speech = sect.readString( "speech" )

	@property
	def src_pos( self ) :
		return self.__src_pos

	@property
	def dst_pos( self ) :
		return self.__dst_pos

	@property
	def duration( self ) :
		return self.__duration

	@property
	def dwell_time( self ) :
		return self.__dwell_time

	@property
	def content( self ) :
		return self.__content

	@property
	def speech( self ) :
		return self.__speech


sceneLoader = SceneLoader.getInst()
ScenePlayer.registerEvents()
