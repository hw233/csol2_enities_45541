# -*- coding: gb18030 -*-
#
# $Id: MessagePanel.py,v 1.10 2008-08-30 09:05:30 huangyongwei Exp $

"""
implement panel for showing chating message

2007/04/18: writen by huangyongwei
2008/04/02: rewriten by huangyongwei ( new version )
2009/04/06: rewriten by huangyongwei:
			��ϵͳ��Ϣ������һ��������з�ҳ��ʾ
"""


import time
from guis import *
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ScrollPanel import VScrollPanel
from guis.general.chatwindow.channelcolorsetter.ColorSetter import ColorSetter
import csdefine

FOMAT_CHANNELS = [ csdefine.CHAT_CHANNEL_SYSTEM,
		csdefine.CHAT_CHANNEL_COMBAT,
		csdefine.CHAT_CHANNEL_PERSONAL,
		csdefine.CHAT_CHANNEL_MESSAGE,
		csdefine.CHAT_CHANNEL_SC_HINT,
		csdefine.CHAT_CHANNEL_MSGBOX,
		csdefine.CHAT_CHANNEL_SYSBROADCAST,
		csdefine.CHAT_CHANNEL_NPC_SPEAK,
		csdefine.CHAT_CHANNEL_NPC_TALK,
		]

class MSGPanel( VScrollPanel ) :
	__cc_max_count		= 50						# ��ౣ������Ϣ����
	__cc_vs_duration	= 120						# ������ʾʱ��
	__cc_paste_interval = 0.1						# ��Ϣˢ�¼��

	def __init__( self, panel, sbar ) :
		VScrollPanel.__init__( self, panel, sbar )
		self.mouseScrollFocus = True
		self.pySBar.v_dockStyle = "VFILL"
		self.pySBar.h_dockStyle = "RIGHT"
		self.pySBar.onLMouseDown.bind( self.__onSBarLMouseDown )
		self.skipScroll = False
		self.perScroll = 32							# ��λ����ֵ
		self.pyRichs_ = []							# ���������Ϣ CSRichText
		self.__persistCBIDs = {}					# ������ʾ callback ID
		self.__allPersistsCBID = 0					# ȫ�����³�����ʾ��ʱ callback ID
		self.__widthChangedDelayCBID = 0			# ��ȸı�ʱ����ʱ������Ϣ���� callback ID
		self.__msgsBuffer = []						# ��Ϣ����
		self.__pasteCBID = 0						# ����ʱ�䵽��ʱ�������Ϣ�� callback ID


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����ؼ��¼�
		"""
		VScrollPanel.generateEvents_( self )
		self.__onLinkMessageLClick = self.createEvent_( "onLinkMessageLClick" )
		self.__onLinkMessageRClick = self.createEvent_( "onLinkMessageRClick" )

	@property
	def onLinkMessageLClick( self ) :
		"""
		������ĳ����������Ϣʱ������
		"""
		return self.__onLinkMessageLClick

	@property
	def onLinkMessageRClick( self ) :
		"""
		�Ҽ����ĳ����������Ϣʱ������
		"""
		return self.__onLinkMessageRClick


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __flushWidth( self ) :
		"""
		��Ϣ�����ȸı�ʱ������
		"""
		self.__cancelAllPersists()
		width = self.width
		key = self.__generatePersistKey()
		def fn( pyRich ) :
			pyRich.maxWidth = width
			pyRich.detectKey = key
			pyRich.visible = True
		self.__layoutItems( fn )
		self.scroll = self.maxScroll
		cbid = BigWorld.callback( self.__cc_vs_duration, \
			Functor( self.__vsPersistArrived, key, self.pyRichs_ ) )	# ����ֱ���� __repersistAll ��ԭ���Ǳ�����ѭ��һ��
		self.__persistCBIDs[key] = cbid

	def __flushHeight( self ) :
		"""
		��Ϣ����߶ȸı�ʱ������
		"""
		self.__cancelAllPersists()
		key = self.__generatePersistKey()
		def fn( pyRich ) :
			pyRich.detectKey = key
			pyRich.visible = True
		self.__layoutItems( fn )
		self.scroll = self.maxScroll
		cbid = BigWorld.callback( self.__cc_vs_duration, \
			Functor( self.__vsPersistArrived, key, self.pyRichs_ ) )	# ����ֱ���� __repersistAll ��ԭ���Ǳ�����ѭ��һ��
		self.__persistCBIDs[key] = cbid

	# -------------------------------------------------
	def __getMSGRich( self ) :
		"""
		��ȡһ����Ϣ CSRichText
		"""
		if len( self.pyRichs_ ) >= self.__cc_max_count :
			pyRich = self.pyRichs_.pop( 0 )
			pyRich.visible = True
			return pyRich
		pyRich = CSRichText()
		pyRich.opGBLink = True
		self.addPyChild( pyRich )
		pyRich.onComponentLClick.bind( self.onLinkMessageLClick_ )
		pyRich.onComponentRClick.bind( self.onLinkMessageRClick_ )
		pyRich.maxWidth = self.width
		return pyRich

	def __layoutItems( self, fn = None ) :
		"""
		��������������Ϣ��λ��
		"""
		top = 0
		for pyRich in self.pyRichs_ :
			if fn : fn( pyRich )
			pyRich.top = top
			top = pyRich.bottom
		if top < self.height :							# ˵����Ϣ���ڿ�����ʾ��������Ϣ
			bottom = self.height
			for pyRich in reversed( self.pyRichs_ ) :
				pyRich.bottom = bottom
				bottom = pyRich.top
			self.maxScroll = 0
		else :
			self.maxScroll = top - self.height

	# -------------------------------------------------
	def __generatePersistKey( self ) :
		"""
		����һ��������ʾ��
		"""
		key = 0
		while True :
			if key not in self.__persistCBIDs :
				return key
			key += 1

	def __vsPersistArrived( self, key, pyRichs ) :
		"""
		����ʱ�䵽��
		"""
		self.__persistCBIDs.pop( key )
		for pyRich in pyRichs :
			if pyRich.detectKey == key :
				pyRich.visible = False

	def __vsPersist( self, pyRichs ) :
		"""
		�ӳ���ʾָ����Ϣ
		"""
		key = self.__generatePersistKey()
		for pyRich in pyRichs :
			pyRich.visible = True
			pyRich.detectKey = key								# ��¼�����г�������( ��Ϊ CSRichText ���ظ����õ� )
		cbid = BigWorld.callback( self.__cc_vs_duration, \
			Functor( self.__vsPersistArrived, key, pyRichs ) )
		self.__persistCBIDs[key] = cbid

	def __cancelAllPersists( self ) :
		"""
		ȡ�����г�����ʾ
		"""
		for cbid in self.__persistCBIDs.itervalues() :
			BigWorld.cancelCallback( cbid )
		self.__persistCBIDs = {}

	def __repersistAll( self ) :
		"""
		ȫ����Ϣ���ӳ����أ����³�����ʾ
		"""
		def vsPersist() :
			self.__cancelAllPersists()
			self.__vsPersist( self.pyRichs_ )
		BigWorld.cancelCallback( self.__allPersistsCBID )
		self.__allPersistsCBID = BigWorld.callback( 0.3, vsPersist )	# ʹ�� callback ��ʱһ������ʾ��ԭ���ǣ���ֹ��Ƶ�� reset

	# -------------------------------------------------
	def __onSBarLMouseDown( self, mods ) :
		"""
		�����������ʱ����
		"""
		self.__repersistAll()

	# -------------------------------------------------
	def __addMessage( self, msg, color ,chid) :
		"""
		���һ����Ϣ
		"""
		scroll = self.maxScroll - self.scroll			# ����ԭ���Ĺ���λ��
		count = len( self.pyRichs_ )					# ԭ������Ϣ����
		pyRich = self.__getMSGRich()
		decHeight = pyRich.height						# ���ӵĸ߶�
		if chid not in FOMAT_CHANNELS:
			pyRich.text_axi = ""
		else:
			pyRich.text = ""
		if len( color ) == 3 : color += ( 255,)			# foreColor������4��Ԫ�أ�����CSRichText�������ʱ�����
		pyRich.foreColor = color
		if chid not in FOMAT_CHANNELS:
			pyRich.text_axi = msg
		else:
			pyRich.text = msg
		self.pyRichs_.append( pyRich )

		# ���µ���������Ϣ��λ��
		self.__layoutItems()

		# �����Ϣ��ԭ���Ĺ���λ�øı䣬�ָ�ԭ���Ĺ���λ��
		gap = 2 * pyRich.lineHeight
		if scroll < max( gap, pyRich.height ) :			# ֮ǰ���������ǹ�������
			self.scroll = self.maxScroll				# ���������λ��
		elif count >= self.__cc_max_count :				# ֮ǰ���������ǹ����м��,������Ϣ CSRichText �Ѿ�ѭ��ʹ��
			self.scroll -= decHeight					# �򣬱���ԭ���Ĺ���λ��
		self.__vsPersist( [pyRich] )					# ������ʾһ��ʱ��
		return pyRich

	# -------------------------------------------------
	def __cacheMessage( self, msg, color, chid ) :
		"""������Ϣ"""
		if len( self.__msgsBuffer ) > self.__cc_max_count :
			self.__msgsBuffer.pop( 0 )
		self.__msgsBuffer.append( ( msg, color, chid ) )
		if self.gui.parent.visible :
			self.startPasting()

	def __pasteMessages( self ) :
		"""ճ�����л������Ϣ"""
		if len( self.__msgsBuffer ) == 0 :
			self.__pasteCBID = 0
			return
		msg, color, chid = self.__msgsBuffer.pop( 0 )
		pyRich = self.__addMessage( msg, color ,chid)
		pyRich.chid = chid
		self.__pasteCBID = BigWorld.callback( self.__cc_paste_interval, \
												self.__pasteMessages )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseScroll_( self, dz ) :
		"""
		�����ֹ���ʱ������
		"""
		VScrollPanel.onMouseScroll_( self, dz )
		self.__repersistAll()
		return True

	# -------------------------------------------------
	def onLinkMessageLClick_( self, pyCom ) :
		"""
		������ĳ����������Ϣʱ������
		"""
		self.onLinkMessageLClick( pyCom )

	def onLinkMessageRClick_( self, pyCom ) :
		"""
		�Ҽ����ĳ����������Ϣʱ������
		"""
		self.onLinkMessageRClick( pyCom )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addChanelMessage( self, channel, msg ) :
		"""
		���һ��Ƶ����Ϣ
		"""
		chid = channel.id
		color = ColorSetter().getChannelColor( chid )
		self.__cacheMessage( msg, color, chid )
		#pyRich = self.__addMessage( msg, color )
		#pyRich.chid = chid

	def addCommonMessage( self, msg, color ) :
		"""
		��ʾһ����ͨ��Ϣ
		"""
		self.__cacheMessage( msg, color, None )
		#pyRich = self.__addMessage( msg, color )
		#pyRich.chid = None

	def clearMessages( self ) :
		"""
		���������Ϣ
		"""
		self.__cancelAllPersists()
		for pyRich in self.pyRichs_ :
			self.delPyChild( pyRich )
		self.pyRichs_ = []
		self.__msgsBuffer = []	# ��ջ�����Ϣ

	def resetMSGColor( self, chcolors ) :
		"""
		��������Ƶ����ɫ
		"""
		for pyRich in self.pyRichs_ :
			color = chcolors.get( pyRich.chid, None )
			if color : pyRich.foreColor = color

	# -------------------------------------------------
	def startPasting( self ) :
		"""������Ϣճ������"""
		if self.__pasteCBID == 0 :						# ճ��û����
			self.__pasteMessages()						# ճ��һ����Ϣ

	def stopPasting( self ) :
		"""ֹͣճ������"""
		#if self.__pasteCBID != 0 :
		BigWorld.cancelCallback( self.__pasteCBID )
		self.__pasteCBID = 0

	# -------------------------------------------------
	def upScrollHistory( self ) :
		"""
		�Ϸ���ʷ��Ϣ���Ϸ�һҳ��
		"""
		self.scroll -= self.height

	def downScrollHistory( self ) :
		"""
		�·���ʷ��Ϣ���·�һҳ��
		"""
		self.scroll += self.height

	def scrollToEnd( self ) :
		"""
		�����������յ�����Ϣ��
		"""
		self.scroll = self.maxScroll


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		VScrollPanel._setWidth( self, width )
		BigWorld.cancelCallback( self.__widthChangedDelayCBID )
		self.__widthChangedDelayCBID = BigWorld.callback( 0.5, self.__flushWidth )	# ����������ıȽϴ���˿�ȸı�Ƶ�ȹ���ʱ����ʱ����

	def _setHeight( self, height ) :
		VScrollPanel._setHeight( self, height )
		self.__flushHeight()


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	width = property( VScrollPanel._getWidth, _setWidth )
	height = property( VScrollPanel._getHeight, _setHeight )
