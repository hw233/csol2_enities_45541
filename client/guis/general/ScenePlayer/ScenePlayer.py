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

VIEW_SIZE = ( 1024.0, 768.0 )						# Ĭ���ڴ˷ֱ��������þ���
PIECE_SIZE = 512.0									# ��Ƭ�ĳߴ磨������ȣ�
PRV_TIME = 0.5										# Ԥ�ȼ���0.5��󽫻���ֵ���ͼ


class FadingObject( object ) :
	"""alpha˥����"""

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
	"""���鲥����"""
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
		self.__motor = Motor( self.__pyFresco )					# ������ڽ������ã�ͨ������destroy�����
		self.__motor.onArrive.bind( self.__onNodeArrive )

		self.__pyContent = FadingText( gui.rtx_content )		# �����ı�
		self.__pyContent.align = "C"
		self.__pyContent.h_dockStyle = "CENTER"
		self.__pyContent.v_dockStyle = "BOTTOM"
		self.__initContent( "STXINWEI.TTF", 28 )

		self.__pyBtnHide = HButtonEx( gui.btn_hide )				# �رհ�ť
		self.__pyBtnHide.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnHide.onLClick.bind( self.__onHide )
		self.__pyBtnHide.h_dockStyle = "RIGHT"
		self.__pyBtnHide.v_dockStyle = "BOTTOM"
		self.__pyBtnHide.visible = False
		labelGather.setPyBgLabel( self.__pyBtnHide, "ScenePlayer:main", "btnHide" )

		self.__layout()

		# ����������ⴰ��
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
		"""����ڻ�"""
		self.__onNodeArrive( sceneLoader.getVertexs()[0] )

	def __onNodeArrive( self, dst_pos ) :
		"""�Ѿ����ﵽĿ��ڵ�
		@param	dst_pos : Ŀ�������"""
		node = sceneLoader.getNode( dst_pos )
		if node is None :
			self.fadeaway()										# �Ҳ��������ڵ㣬����
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
				rds.soundMgr.switchVoice( node.speech )			# �л�����
			if node.content == "EOF" :							# ��������Ϊ�����ı�
				self.__pyContent.fadeout()
			elif node.content :									# �������ʾ�ı�
				self.__pyContent.text = node.content
				self.__pyContent.fadein()

	def __layout( self ) :
		"""��Ϸ�ֱ��ʸı�"""
		global VIEW_SIZE
		self.size = BigWorld.screenSize()
		self.pos = 0, 0
		scale = max( self.width / VIEW_SIZE[0], self.height / VIEW_SIZE[1] )
		self.__pyFresco.zoom( scale )							# ���մ�ı�����������
		spacing = self.__pyBtnHide.left
		self.__pyContent.maxWidth = spacing - 40				# �Զ������ı���ʾ�������
		self.__pyContent.left = ( spacing - self.__pyContent.maxWidth ) * 0.5

	def __onHide( self ) :
		"""�����ť�˳�"""
		self.__pyBtnHide.visible = False
		self.fadeaway()

	def __cancelCallback( self, cbids ) :
		"""ȡ���ص�"""
		for cbid in cbids :
			BigWorld.cancelCallback( cbid )

	# -------------------------------------------------
	# public
	# -------------------------------------------------
	def play( self ) :
		"""���ž���"""
		self.__cancelCallback( self.__fadeoutCbids )
		self.__fadeoutCbids = []
		self.__pyFresco.draw( sceneLoader.getTextureInfo() )
		self.__pyFresco.pos = sceneLoader.getVertexs()[0]
		ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", False )
		self.show()
		self.fadein()
		rds.soundMgr.lockBgPlay( False )						# �����������ֲ���
		rds.soundMgr.stopMusic()								# ֹͣ��Ϸ����
		def callback() :
			if self.disposed : return							# �Ѿ�����
			self.__browseFresco()								# ����ڻ�
			rds.soundMgr.lockBgPlay( False )					# �����������ֲ��ţ���Ϊ�����callback��Ϊ��ֹ���⣬�����ٽ���һ�Σ�
			bgMusic = sceneLoader.getBgMusic()
			rds.soundMgr.switchMusic( bgMusic )					# ���ű�������
			rds.soundMgr.lockBgPlay( True )						# �����������ֲ���
			self.__pyBtnHide.visible = True
			self.__pyFresco.fadein()
		self.__fadeinCbids.append( \
			BigWorld.callback( self.fadeSpeed + 2, callback ) )

	def fadeaway( self ) :
		"""���ţ��˳�"""
		self.__cancelCallback( self.__fadeinCbids )
		self.__fadeinCbids = []
		rds.soundMgr.stopVoice()								# ֹͣ�԰�����
		rds.soundMgr.lockBgPlay( False )						# �����������ֲ���
		player = BigWorld.player()
		if player and player.isPlayer() :
			currArea = player.getCurrArea()
			music = ""
			if currArea :
				music = currArea.getMusic()
			rds.soundMgr.switchMusic( music )					# ��������Ϊ��ҵ�ǰ�������������
		self.__pyFresco.fadeout()
		ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", True )		# ������ʾ���д���
		def callback() :
			self.destroy()										# ���������ʵ��
		self.__fadeoutCbids.append( \
			BigWorld.callback( self.__pyFresco.fadeSpeed * 0.5, self.fadeout ) )
		self.__fadeoutCbids.append( \
			BigWorld.callback( self.fadeSpeed + self.__pyFresco.fadeSpeed * 0.5, callback ) )

	def destroy( self ) :
		"""���ٲ�����"""
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
		"""����/��ȡʵ��"""
		return CLS.__cc_inst

	@classmethod
	def instance( CLS ) :
		"""����/��ȡʵ��"""
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
		"""ע�ᴥ���¼�"""
		ECenter.registerEvent( "EVT_ON_DISPLAY_SCENE", CLS )

	@classmethod
	def onEvent( CLS, evtMacro, *args ) :
		if evtMacro == "EVT_ON_RESOLUTION_CHANGED" :			# �ֱ��ʸı���¼�
			if CLS.__cc_inst :
				CLS.getInst().__layout()
		elif evtMacro == "EVT_ON_DISPLAY_SCENE" :
			CLS.onDisplay( *args )


class Fresco( FadingObject, GUIBaseObject ) :
	"""����ͼ��"""

	def __init__( self, gui ) :
		FadingObject.__init__( self, gui )
		GUIBaseObject.__init__( self, gui )
		self.fadeout()
		self.__moveSpeed = ( 0, 0 )					# �ƶ��ٶȣ���ȡ��Ƭʱ��Ҫ��
		self.__orgn_size = gui.size					# ԭʼ�ߴ�
		self.__scale = 1.0							# ���ű�����������Ȳ���������ţ�
		self.__txFolder = ""						# ��ͼ��Ƭ�Ĵ��Ŀ¼
		self.__pyIdleElem = []
		self.__pyElemMap = {}

	def dispose( self ) :
		GUIBaseObject.dispose( self )
		self.__pyIdleElem = []
		self.__pyElemMap = {}

	def draw( self, textureInfo ) :
		"""����ͼ��"""
		self.__releasePieces( self.__pyElemMap.keys() )
		self.__orgn_size = textureInfo.size
		self.__txFolder = textureInfo.textureFolder
		self.size = textureInfo.size
		self.zoom( self.__scale )
		self.update( self.pos )

	def zoom( self, scale ) :
		"""����ͼ��"""
		pos = self.pos								# ��������ǰ��λ��
		self.width = self.__orgn_size[0] * scale
		self.height = self.__orgn_size[1] * scale
		self.__scale = scale
		self.pos = pos								# ����λ��
		self.__layout()

	def update( self, pos ) :
		"""���±ڻ�"""
		new_pieces = self.measurePieces( pos )
		old_pieces = self.__pyElemMap.keys()
		if new_pieces == old_pieces : return				# ��Ҫ��ʾ����Ƭû��
		pieces_out = set( old_pieces ) - set( new_pieces )
		self.__releasePieces( pieces_out )
		pieces_add = set( new_pieces ) - set( old_pieces )
		self.__combine( pieces_add )

	def measurePieces( self, pos ) :
		"""������������ص���ͼ��Ƭ"""
		global VIEW_SIZE, PIECE_SIZE, PRV_TIME
		h_speed, v_speed = self.__moveSpeed
		view_top = pos[1] - VIEW_SIZE[1] * 0.5
		view_left = pos[0] - VIEW_SIZE[0] * 0.5
		view_right = view_left + VIEW_SIZE[0]
		view_bottom = view_top + VIEW_SIZE[1]
		t_pcount = int( ( view_top ) / PIECE_SIZE )						# ���˵���Ƭ����
		l_pcount = int( ( view_left ) / PIECE_SIZE )					# ��ߵ���Ƭ����
		v_pright = l_pcount * PIECE_SIZE
		h_count = int( math.ceil( ( view_right - v_pright ) / PIECE_SIZE ) )
		h_pbottom = t_pcount * PIECE_SIZE
		v_count = int( math.ceil( ( view_bottom - h_pbottom ) / PIECE_SIZE ) )
		# ���²��ִ����Ǹ����ƶ��ٶȵĴ�С�ͷ������������Ԥ���ص���Ƭ
		if h_speed > 0 :												# ˮƽ�ٶ�����
			prv_dist = view_right + PRV_TIME * h_speed - PIECE_SIZE * ( l_pcount + h_count )
			if prv_dist > 0 :
				h_count += int( math.ceil( prv_dist / PIECE_SIZE ) )
		elif h_speed < 0 :												# ˮƽ�ٶ�����
			prv_dist = v_pright - view_left - PRV_TIME * h_speed
			if prv_dist > 0 :
				inc_count = int( math.ceil( prv_dist / PIECE_SIZE ) )
				h_count += inc_count
				l_pcount -= inc_count
		if v_speed > 0 :												# ��ֱ�ٶ�����
			prv_dist = view_bottom + PRV_TIME * v_speed - PIECE_SIZE * ( t_pcount + v_count )
			if prv_dist > 0 :
				v_count += int( math.ceil( prv_dist / PIECE_SIZE ) )
		elif v_speed < 0 :												# ��ֱ�ٶ�����
			prv_dist = h_pbottom - view_top - PRV_TIME * v_speed
			if prv_dist > 0 :
				inc_count = int( math.ceil( prv_dist / PIECE_SIZE ) )
				v_count += inc_count
				t_pcount -= inc_count
		# ���ϲ��ִ����Ǹ����ƶ��ٶȵĴ�С�ͷ������������Ԥ���ص���Ƭ
		result = []
		for i in xrange( v_count ) :
			for j in xrange( h_count ) :
				result.append( ( t_pcount + i, l_pcount + j ) )
		return result

	def updateSpeed( self, speed ) :
		"""�����֪ͨ�ٶȸ���"""
		self.__moveSpeed = speed

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __combine( self, pieces ) :
		"""����Ƭƴ�ϳ���������ͼ"""
		path_fmt = self.__txFolder + "/p_%.2i.dds"
		colAmount = int( math.ceil( self.__orgn_size[0] / PIECE_SIZE ) )
		for piece in pieces :
			cb = Functor( self.__loadPieceCb, piece )
			BigWorld.fetchTexture( path_fmt % ( piece[0] * colAmount + piece[1] + 1 ), cb )

	def __loadPieceCb( self, piece, elem ) :
		"""��Ƭ���ػص�"""
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
		"""����������ͼ��λ��"""
		for ( i, j ), elem in self.__pyElemMap.iteritems() :
			elem.size.x = PIECE_SIZE * self.__scale
			elem.size.y = PIECE_SIZE * self.__scale
			elem.position.x = j * PIECE_SIZE * self.__scale
			elem.position.y = i * PIECE_SIZE * self.__scale

	# -------------------------------------------------
	# property
	# -------------------------------------------------
	def _setLeft( self, left ) :
		"""����posλ�ڸ����ڵ����ĵ���"""
		left *= self.__scale
		parentHalfWidth = self.gui.parent.width * 0.5
		GUIBaseObject._setLeft( self, parentHalfWidth - left )
		self.update( self._getPos() )

	def _getLeft( self ) :
		"""pos��ָ��ͼ���Ǹ���λ�ڸ����ڵ�����"""
		left = GUIBaseObject._getLeft( self )
		return ( self.gui.parent.width * 0.5 - left ) / self.__scale

	def _setTop( self, top ) :
		"""����posλ�ڸ����ڵ����ĵ���"""
		top *= self.__scale
		parentHalfHeihgt = self.gui.parent.height * 0.5
		GUIBaseObject._setTop( self, parentHalfHeihgt - top )
		self.update( self._getPos() )

	def _getTop( self ) :
		"""pos��ָ��ͼ���Ǹ���λ�ڸ����ڵ�����"""
		top = GUIBaseObject._getTop( self )
		return ( self.gui.parent.height * 0.5 - top ) / self.__scale

	def _setPos( self, ( left, top ) ) :
		"""pos��ָ��ͼ���Ǹ���λ�ڸ����ڵ�����"""
		self._setLeft( left )
		self._setTop( top )
		self.update( self._getPos() )

	def _getPos( self ) :
		"""pos��ָ��ͼ���Ǹ���λ�ڸ����ڵ�����"""
		return ( self._getLeft(), self._getTop() )

	left = property( _getLeft, _setLeft )
	top = property( _getTop, _setTop )
	pos = property( _getPos, _setPos )


class Motor( object ) :
	"""�ƶ�����"""

	__cc_interval = 0.02												# �����ص��������λ����

	def __init__( self, obj ) :
		object.__init__( self )
		self.__driveObj = obj
		self.__cbid = 0													# callback ID
		self.__speed = ( 0, 0 )											# �ƶ��ٶ�( ˮƽ, ��ֱ )
		self.__duration = 0												# �趨���ƶ�ʱ��
		self.__src_pos = ( 0, 0 )										# �ƶ�����ʼλ��
		self.__dst_pos = ( 0, 0 )										# �ƶ���Ŀ��λ��
		self.__startTime = 0											# ��һ�λص���ʱ�䣨���ڼ������λص��ļ����

		self.__onArrive = ControlEvent( "onArrive", self )				# ����Ŀ�ĵ��¼�

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
		"""����"""
		self.__moving()

	def shut( self ) :
		"""ͣ��"""
		if self.__cbid :
			BigWorld.cancelCallback( self.__cbid )
			self.__cbid = 0

	def refresh( self, src, dst, duration ) :
		"""�����ƶ�����"""
		xs = ( dst[0] - src[0] ) / duration
		ys = ( dst[1] - src[1] ) / duration
		self.__speed = ( xs, ys )
		self.__driveObj.updateSpeed( self.__speed )
		self.__src_pos = src
		self.__dst_pos = dst
		self.__duration = duration

	def move( self, src, dst, duration ) :
		"""������Ŀ����ƶ�"""
		self.shut()
		if self.__driveObj is None : return
		self.refresh( src, dst, duration )
		self.__startTime = time.time()
		self.__moving()

	def destroy( self ) :
		"""���٣����������"""
		self.shut()
		self.__driveObj = None

	@staticmethod
	def calcDistance( src, dst ) :
		"""��������֮��ľ���"""
		return math.sqrt( ( dst[0] - src[0] )**2 + ( dst[1] - src[1] )**2 )

	def isArrive( self ) :
		"""�Ƿ񵽴���Ŀ�ĵأ���������֮��ľ����������ж�"""
		return self.calcDistance( self.__driveObj.pos, self.__dst_pos ) < 0.5


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __moving( self ) :
		"""��ͣ���ƶ���ֱ������Ŀ�ĵ�"""
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
	"""��������"""

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
		��ʼ������
		"""
		if sceneID == self.__currSceneID : return True				# �þ����ѵ���
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
				if None not in self.getVertexs() :					# ������ڵ�������Ƿ���ȷ
					self.__currSceneID = sceneID
					return True
				break
		ERROR_MSG( "Can't find scene config by id %i." % sceneID )
		return False

	def getNode( self, src_pos ) :
		"""����Դλ�û�ȡ��Ӧ�Ľڵ���Ϣ"""
		return self.__nodes.get( src_pos )

	def getVertexs( self ) :
		"""��ȡ��������"""
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
		�����������Ҫ������
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
	"""����ڵ�"""
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
