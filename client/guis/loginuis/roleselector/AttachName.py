# -*- coding: gb18030 -*-
#
# $Id: AttachName.py,v 1.9 2008-07-24 03:36:12 huangyongwei Exp $

"""
implement role selection dialog
2007/10/16 : writen by huangyongwei
"""

import time
import csconst
from guis import *
import event.EventCenter as ECenter
from EntityAttachment import EntityAttachment
from guis.common.PyGUI import PyGUI
from guis.controls.StaticText import StaticText
from LabelGather import labelGather
import csdefine
import GUI

class AttachName( EntityAttachment, PyGUI ) :
	def __init__( self ) :
		EntityAttachment.__init__( self )
		bg = GUI.load( "guis/loginuis/roleselector/attachname.gui" )
		uiFixer.firstLoadFix( bg )
		PyGUI.__init__( self, bg )
		
		self.__pyStName = StaticText( bg.stName )
		self.__pyStName.setFloatNameFont()
		self.__pyStName.text = ""
		self.__pyRoleInfo = RoleInfo( bg.roleInfo )
		self.__guiAttach = None
		self.__role = None
		self.pyElements_ = [self.__pyRoleInfo, self.__pyStName]

		ECenter.registerEvent( "EVT_ON_RENAME_ROLE_SUCCESS", self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __setRoleInfo( self, roleInfo ) :
		if roleInfo is None : return
		roleName = roleInfo.getName()
		self.__pyStName.text = roleName
		self.__pyRoleInfo.setRoleInfo( roleInfo )
		self.width = max( self.__pyRoleInfo.width, self.__pyStName.width) + 6.0
		self.layout_()
		
	def __onNameChanged( self, roleID, newName ) :
		"""
		角色改名
		"""
		if self.__role is None : return
		roleInfo = self.__role.roleInfo
		if roleInfo is None or \
			roleInfo.getID() != roleID : return
		self.__setRoleInfo( roleInfo )

	def layout_( self ) :
		preTop = 0
		for pyElem in self.pyElements_ :
			if not pyElem.visible : continue
			pyElem.center = 0.0
			pyElem.bottom = preTop
			preTop = pyElem.top - 4.0
		self.height = -preTop
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onAttached( self, role ) :
		self.__role = role
		EntityAttachment.onAttached( self, role )
		roleInfo = role.roleInfo
		self.__setRoleInfo( roleInfo )
		if role.model is None : return

		self.__guiAttach = GUI.BillboardAttachment()
		self.__guiAttach.component = self.getGui()
		self.__guiAttach.position = Math.Vector3( 0, role.model.height / 2.0 , 0 )
		self.__guiAttach.excursion = 0.0
		try :
			bindNode = role.model.node( "HP_body" )
			bindNode.attach( self.__guiAttach )
		except :
			ERROR_MSG( "not node named 'HP_body' in this mode!" )

	def onDetached( self ) :
		if not self.__role : return
		if not self.__role.model: return
		bindNode = self.__role.model.node("HP_body")
		bindNode.detach( self.__guiAttach )
		self.__role = None
		self.__guiAttach = None

	# ---------------------------------------
	def onEnterWorld( self ) :
		pass

	def onLeaveWorld( self ) :
		self.onDetached()

	# ---------------------------------------
	def onTargetFocus( self ) :
		pass

	def onTargetBlur( self ) :
		pass

	# ---------------------------------------
	def onBecomeTarget( self ) :
		pass

	def onLoseTarget( self ) :
		pass

	def onEvent( self, evtMacro, *args ) :
		self.__onNameChanged( *args )

# 角色头顶名称
class RoleInfo( PyGUI ):
	def __init__( self, roleInfo ):
		PyGUI.__init__( self, roleInfo )
		self.__pyCmpIcon = PyGUI( roleInfo.campIcon )
		self.__pyStInfo = StaticText( roleInfo.stInfo )
		self.__pyStInfo.setFloatNameFont()
		self.__pyStInfo.text = ""
		self.__camp = 0
	
	def setRoleInfo( self, roleInfo ):
		profession = csconst.g_chs_class[roleInfo.getClass()]
		camp = ( roleInfo.getRaceClass()& csdefine.RCMASK_CAMP ) >> 20
		util.setGuiState( self.__pyCmpIcon.getGui(), ( 1, 2 ), ( 1, camp ) )
		if roleInfo.getLevel() > 0:
			level = labelGather.getText( "RoleSelector:attachName", "level", roleInfo.getLevel() )
			self.__pyStInfo.text = "%s %s" % ( profession, level )
		else:
			self.__pyStInfo.text = "%s   "%profession
		self.width = self.__pyCmpIcon.width + self.__pyStInfo.width