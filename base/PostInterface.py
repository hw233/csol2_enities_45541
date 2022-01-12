# -*- coding: gb18030 -*-
#
# $Id: PostInterface.py,v 1.1 2007-03-26 07:04:31 panguankong Exp $

"""
postoffice interface
"""

import BigWorld

class PostInterface:
	def __init__( self ):
		self.postofficeBase = BigWorld.globalBases["Postoffice"]
		if self.postofficeBase == None:
			ERROR_MSG( "GlobalBases postofficeBase Not Find!" )
		
		self.cellData["postofficeBase"] = self.postofficeBase
		self.playerName = self.cellData["playerName"]
	
	def postLogon( self ):
		"""
		登录邮件
		"""
		self.postofficeBase.logon( self.playerName, self )
		
	def postLogout( self ):
		"""
		退出邮件系统
		"""
		self.postofficeBase.logout( self.playerName )


# $Log: not supported by cvs2svn $
# 