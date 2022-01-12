# -*- coding: gb18030 -*-

# ���������¼�鿴����
# written by gjx 2010-06-17

from guis import *
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.RichText import RichText

import os
import time
from ChatFacade import chatFacade
from LabelGather import labelGather
from AbstractTemplates import Singleton
from config.client.msgboxtexts import Datas as mbmsgs

from PLMMsgPanel import PLMMsgPanel


class PLMLogWindow( Singleton, Window ) :

	def __init__( self ) :
		wnd = GUI.load( "guis/general/chatwindow/playmatechat/logviewer.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )

		self.__initialize( wnd )
		self.addToMgr()

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_PLMLogWindow :
			INFO_MSG( "[%s] delete!" % str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		self.__pyBtnSave = Button( wnd.btn_save )
		self.__pyBtnSave.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnSave.onLClick.bind( self.__onSaveLog )

		self.__pyBtnHide = Button( wnd.btn_hide )
		self.__pyBtnHide.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnHide.onLClick.bind( self.hide )

		self.__pyRTClew = RichText( wnd.rt_clew )
		self.__pyRTClew.foreColor = ( 255, 255, 0, 255 )
		# "Ϊ��������˽��ȫ�������¼�����Զ��浵������Ҫ��ʹ�ñ��湦�����Ᵽ�档"
		self.__pyRTClew.text = labelGather.getText( "ChatWindow:PLMLogViewer", "stClew" )

		logPnl = wnd.mlRTB_logPanel
		self.__pyLogBox = PLMMsgPanel( logPnl.clipPanel, logPnl.sbar )

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyBtnSave, "ChatWindow:PLMLogViewer", "btnSave" )
		labelGather.setPyBgLabel( self.__pyBtnHide, "ChatWindow:PLMLogViewer", "btnHide" )

	def __onSaveLog( self ) :
		"""
		����������־
		"""
		pyMsgItems = self.__pyLogBox.pyItems
		if len( pyMsgItems ) == 0 : return
		accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]	# ��ǰ�˺���
		fileName = time.strftime( "%y%m%d_%H%M%S", time.localtime() ) + ".txt"
		filePath = "account/%s/chatlogs/%s" % ( accountName, fileName )
		rootPath = "%s\\res\\%s" % ( os.getcwd(), filePath.replace( "/", "\\" ) )

		def saveFile() :
			try :
				file = open( filePath, "w" )
				for pyMsg in pyMsgItems :
					text = pyMsg.viewText
					file.write( text + "\n" )
				file.flush()
				file.close()
				# �����¼�ѳɹ����浽%s�ļ��С�
				msg = mbmsgs[0x0241] % ( rootPath )
				showMessage( msg, "", MB_OK, None, self )
			except IOError, errstr :
				# "�����ļ�ʧ�ܣ�%s"
				showMessage( mbmsgs[0x0242] % errstr, "", MB_OK, None, self )

		def query( result ) :
			if result == RS_YES : saveFile()

		fileExists = csol.resourceExists( filePath )				# ����ļ��Ƿ����
		if fileExists :												# �����������ʾ��ͻ
			# �ļ�%s�Ѵ��ڣ��Ƿ񸲸ǣ�
			msg = mbmsgs[0x0243] % ( rootPath )
			showMessage( msg, "", MB_YES_NO, query, self )
		else :
			s = ResMgr.openSection( filePath, True )				# ����δ�ҵ��������������ļ���
			s.save()												# �������������������ļ�
			ResMgr.purge( filePath )
			saveFile()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def showChatLogs( self, objName, msgs, pyOwner = None ) :
		"""
		��ʾ�����¼
		"""
		self.__pyLogBox.reset()							# �����������
		self.__pyLogBox.addMessages( msgs )
		title = labelGather.getText( "ChatWindow:PLMLogViewer", "lbTitle", objName )
		self.pyLbTitle_.text = title
		self.show( pyOwner )

	def hide( self ) :
		self.__pyLogBox.reset()
		self.removeFromMgr()
		self.dispose()
		PLMLogWindow.releaseInst()

	def onLeaveWorld( self ) :
		"""
		����뿪��Ϸ
		"""
		self.hide()
