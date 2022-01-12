# -*- coding: gb18030 -*-

# Implement the pixie main window
# By ganjinxing 2011-2-11

from guis import *
from guis.common.GUIBaseObject import GUIBaseObject
from guis.common.TrapWindow import UnfixedTrapWindow
from guis.controls.Control import Control
from guis.controls.ItemsPanel import ItemsPanel
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Link import PL_Link
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine

import GUIFacade
import StringFormat
import event.EventCenter as ECenter
from Helper import pixieHelper
from cscustom import Polygon
from config.client.GossipType import Datas as MarkMap

MAX_INST_AMOUNT = 4										# ÿ���ౣ�������ʵ������


class OptionGUI( Control ) :
	"""�Ի�ѡ��"""
	__cc_min_height = 22								# ��С�߶�ֵ
	__cc_color_highlight = ( 0,255,0,255 )
	__cc_color_common = ( 255,255,255,255 )

	def __init__( self ) :
		gui = GUI.load( "guis/general/pixiewindow/option.gui" )
		uiFixer.firstLoadFix( gui )
		Control.__init__( self, gui )
		self.width = 180
		self.alpha = 0
		self.focus = True
		self.crossFocus = True
		self.__pyMark = GUIBaseObject( gui.mark )
		self.__pyLabel = CSRichText( gui.rt_label )
		self.__pyLabel.opGBLink = True
		self.__index = -1
		self.setStateView_( UIState.COMMON )

	def init( self, index, mark, text ) :
		"""������Ϣ"""
		self.__index = index
		self.__pyLabel.text = StringFormat.format( text )
		util.setGuiState( self.__pyMark.getGui(), (1,32), MarkMap[ mark ] )
		self.height = max( self.__cc_min_height, self.__pyLabel.bottom )
		self.setStateView_( UIState.COMMON )

	def onMouseEnter_( self ) :
		self.setStateView_( UIState.HIGHLIGHT )
		return Control.onMouseEnter_( self )

	def onMouseLeave_( self ) :
		self.setStateView_( UIState.COMMON )
		return Control.onMouseLeave_( self )

	def setStateView_( self, state ) :
		"""������۱���"""
		if state == UIState.HIGHLIGHT :
			self.__pyLabel.foreColor = self.__cc_color_highlight
		else :
			self.__pyLabel.foreColor = self.__cc_color_common

	@property
	def index( self ) :
		return self.__index


class OptionPanel( GUIBaseObject ) :
	"""ѡ�����"""
	__cc_col_width = 180
	__cc_col_height = 24

	def __init__( self ) :
		gui = GUI.Window("")
		GUIBaseObject.__init__( self, gui )
		self.setToDefault()
		self.height = 0
		self.__pyOptions = []
		self.__pyIdleOpts = {}											# �����

	# -------------------------------------------------
	def __getPyOpt( self, name ) :
		"""�Ӷ�����л�ȡһ������"""
		pyOpts = self.__pyIdleOpts.get( name )
		if pyOpts and len( pyOpts ) :
			return pyOpts.pop( 0 )
		if name == "CSRichText" :
			pyOpt = CSRichText()
			pyOpt.opGBLink = True
			pyOpt.maxWidth = self.__cc_col_width
			pyOpt.autoNewline = False
			return pyOpt
		if name == "OptionGUI" :
			return OptionGUI()

	def __savePyOpt( self, pyOpt ) :
		"""�������"""
		elemClass = pyOpt.__class__.__name__
		pyOpts = self.__pyIdleOpts.get( elemClass )
		if pyOpts is None :
			self.__pyIdleOpts[ elemClass ] = [ pyOpt ]
		elif len( pyOpts ) < MAX_INST_AMOUNT :
			pyOpts.append( pyOpt )
		else :
			print ">>>>--------> %s is full." % elemClass

	def __onGossipOptionClicked( self, pyOpt ) :
		"""�������ͨ�Ի�ѡ��"""
		GUIFacade.selectGossipOption( pyOpt.index )

	def __onQuestOptionClicked( self, pyOpt ) :
		"""���������Ի�ѡ��"""
		GUIFacade.selectGossipQuest( pyOpt.index )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def __layout( self ) :
		"""���ѡ��"""
		top = 0
		lineHeight = 0
		for idx, pyOpt in enumerate( self.__pyOptions ) :
			col = idx % 2
			lineHeight = max( lineHeight, pyOpt.height )
			pyOpt.left = self.__cc_col_width * col
			pyOpt.top = top
			if col == 1 :
				top += max( lineHeight, self.__cc_col_height )
				lineHeight = 0
		if len( self.__pyOptions ) :
			self.height = self.__pyOptions[-1].bottom
		else :
			self.height = 0

	def addHelpOptions( self, options ) :
		"""��Ӱ���ѡ��"""
		for label, linkID in options :
			pyOpt = self.__getPyOpt( "CSRichText" )
			label = StringFormat.format( label )
			linkMark = "pixieHelp:%i" % linkID
			pyOpt.text = PL_Link.getSource( label, linkMark, \
				cfc = ( 0,255,0 ), hfc = ( 0,255,255 ) )
			self.addPyChild( pyOpt )
			self.__pyOptions.append( pyOpt )
		self.__layout()

	def addGossipOptions( self, options ) :
		"""�����ͨ�Ի�ѡ��"""
		for idx, option in enumerate( options ) :
			pyOpt = self.__getPyOpt( "OptionGUI" )
			pyOpt.init( idx, option[2], option[1] )
			pyOpt.onLClick.bind( self.__onGossipOptionClicked )
			self.addPyChild( pyOpt )
			self.__pyOptions.append( pyOpt )
		self.__layout()

	def addQuestOptions( self, options ) :
		"""�������Ի�ѡ��"""
		for idx, option in options :
			pyOpt = self.__getPyOpt( "OptionGUI" )
			pyOpt.init( idx, option[2], option[1] )
			pyOpt.onLClick.bind( self.__onQuestOptionClicked )
			self.addPyChild( pyOpt )
			self.__pyOptions.append( pyOpt )
		self.__layout()

	def clearOptions( self ) :
		"""���ѡ��"""
		for pyOpt in self.__pyOptions :
			self.delPyChild( pyOpt )
			self.__savePyOpt( pyOpt )
		self.__pyOptions = []
		self.__layout()


class PixieWindow( UnfixedTrapWindow ) :
	"""
	������������
	"""
	def __init__( self ) :
		wnd = GUI.load( "guis/general/pixiewindow/pixiewnd.gui" )
		uiFixer.firstLoadFix( wnd )
		UnfixedTrapWindow.__init__( self, wnd )

		self.__triggers = {}
		self.__registerEvents()
		self.__initialize( wnd )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		self.__pyPnlContent = ItemsPanel( wnd.pnl_content, wnd.sbar_content )
		self.__pyPnlContent.sbarState = ScrollBarST.AUTO

		self.__pyPnlOptions = OptionPanel()
		self.__pyPnlOptions.width = wnd.pnl_content.width

		self.__pyGossipText = CSRichText()
		self.__pyGossipText.opGBLink = True
		self.__pyGossipText.maxWidth = wnd.pnl_content.width

		self.__pyPnlContent.addItems( ( self.__pyGossipText, self.__pyPnlOptions, ) )

		self.__wnd_zone = Polygon([(50,185),(49,178),(43,169),(46,162),(90,140),(91,131),
									(76,125),(74,115),(67,113),(61,103),(65,95),(74,88),
									(76,69),(82,57),(113,39),(115,26),(111,22),(106,17),(124,0),
									(148,13),(149,19),(141,31),(154,40),(134,36),(132,29),
									(137,20),(131,21),(124,30),(125,42),(153,68),(155,81),
									(150,101),(155,110),(145,126),(146,137),(138,145),(157,173),
									(155,185),(433,185),(433,371),(0,371),(0,185)])

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------

	def __registerEvents( self ) :
		self.__triggers["EVT_END_GOSSIP"] = self.__onEndGossip
		self.__triggers["EVT_ON_HIDE_PIXIE_WINDOW"] = self.hide
		self.__triggers["EVT_ON_TRIGGER_PIXIE_HELP"] = self.__triggerHelp
		self.__triggers["EVT_ON_TRIGGER_PIXIE_GOSSIP"] = self.__triggerGossip
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __clearContent( self ) :
		"""��նԻ�����"""
		self.__pyGossipText.text = ""
		self.__pyPnlOptions.clearOptions()

	# -------------------------------------------------
	def __onEndGossip( self ) :
		"""����NPC�Ի�"""
		if self.trapID_ > 0 :												# ����С����Ի�״̬
			self.hide()

	def __triggerHelp( self, content, options ) :
		"""����С�������"""
		self.__clearContent()
		self.__addGossipText( content )
		self.__addHelpOptions( options )
		self.__pyPnlContent.layoutItems_()
		self.setTrappedEntID( -1 )											# ����ӶԻ�����
		self.show()

	def __triggerGossip( self ) :
		"""����С����NPC�Ի�"""
		self.__clearContent()
		self.__addGossipText( GUIFacade.getGossipText() )
		self.__addQuestOptions( self.__getQuestOptions() )
		self.__addGossipOptions( self.__getGossipOptions() )
		self.__pyPnlContent.layoutItems_()
		self.setTrappedEntID( GUIFacade.getGossipTargetID() )				# ���С����Ի�����
		self.show()

	def __getGossipOptions( self ) :
		"""��õ�ǰ�Ի�����ͨ�Ի�ѡ��"""
		return GUIFacade.getGossipOptions()									# ��ͨ�Ի�ѡ��

	def __getQuestOptions( self ) :
		"""��õ�ǰ�Ի�������Ի�ѡ��"""
		quests = GUIFacade.getGossipQuests()
		questLogs = GUIFacade.getQuestLogs()
		result = []
		for idx, qInfo in enumerate( quests ) :
			if questLogs.has_key( qInfo[0] ) :
				if GUIFacade.questIsCompleted( qInfo[0] ) :
					result.insert( 0, ( idx, qInfo ) )						# ��ɵ����������
				else :
					result.insert( len(result)/2, ( idx, qInfo ) )			# δ���������м�
			else :
				result.append( ( idx, qInfo ) )								# �ɽӵ����������
		return result

	# -------------------------------------------------
	def __addHelpOptions( self, options ) :
		"""��Ӱ����Ի�ѡ��"""
		self.__pyPnlOptions.addHelpOptions( options )

	def __addGossipOptions( self, options ) :
		"""�����ͨ�Ի�ѡ��"""
		self.__pyPnlOptions.addGossipOptions( options )

	def __addQuestOptions( self, options ) :
		"""�������Ի�ѡ��"""
		self.__pyPnlOptions.addQuestOptions( options )

	def __addGossipText( self, text ) :
		"""�����ͨ�Ի��ı�"""
		self.__pyGossipText.text = StringFormat.format( text )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def addTrap_( self ) :
		"""
		�������
		"""
		if self.trappedEntity :
			UnfixedTrapWindow.addTrap_( self )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onLeaveWorld( self ) :
		"""�������"""
		self.hide()

	def onEvent( self, evtMacro, *args ) :
		self.__triggers[evtMacro]( *args )

	def isMouseHit( self ) :
		"""
		�ж�����Ƿ���ڶ����������
		"""
		return self.__wnd_zone.isPointIn( self.mousePos )

	def onLClick_( self, mods ) :
		"""
		�����������ʱ������
		"""
		if self.isMouseHit() :
			return UnfixedTrapWindow.onLClick_( self, mods )
		return False

	def onClose_( self ) :
		"""
		�ر�ʱ����
		"""
		pixieHelper.sinkTopicsLink()
		return UnfixedTrapWindow.onClose_( self )
