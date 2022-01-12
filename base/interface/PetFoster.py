# -*- coding: gb18030 -*-
#
# $Id: PetFoster.py,v 1.19 2008-08-05 03:09:56 yangkai Exp $

"""
this module implements pet cage interface.

2007/11/07: writen by huangyongwei
"""

import time
import BigWorld
import csdefine
import csconst
import csstatus
import Const
from bwdebug import *
from PetFormulas import formulas
from Function import Functor
from ObjectScripts.GameObjectFactory import g_objFactory
from PetEpitome import queryFosterPets

class PetFoster :
	def __init__( self ) :
		pass

	def onGetCell( self ):
		"""
		"""
		BigWorld.globalData["PetProcreationMgr"].onPlayerGetCell( self.databaseID, self )

	def pft_changePet( self, targetBase, petDBID ):
		"""
		Define method.
		改变了用于繁殖的宠物，把宠物数据发给对方客户端
		"""
		targetBase.client.pft_dstPetChanged( self.pcg_getPetEpitome( petDBID ) )

	def pft_procreatePet( self, dstDatabaseID, petDBID, endTime ):
		"""
		Define method.
		条件符合，开始繁殖宠物的处理

		@param petDBID : 参与繁殖的宠物dbid
		@type petDBID : DATABASE_ID
		"""
		# 运营需求，制作宠物繁殖相关日志 by 姜毅
		pe = self.pcg_getPetEpitome( petDBID )
		ppm = BigWorld.globalData["PetProcreationMgr"]
		name = pe.getAttr("name")
		if name == "":
			name = pe.getAttr("uname")
		name = "%s(%s)"%("name", name )
		isBinded = "%s(%s)"%("isBinded", pe.getAttr("isBinded"))
		# 关于宠物的需记录参数的修改就在这里添加
		nimbus = "%s(%s)"%("nimbus", pe.getAttr("nimbus"))
		species = "%s(%s)"%("species", pe.getAttr("species"))
		dbid = "%s(%s)"%("dbid", petDBID)
		className = "%s(%s)"%( "className", pe.getAttr("className") )
		petDataStr = "%s %s %s %s %s %s"%( name, isBinded, nimbus, species, dbid, className )
		ppm.procreatePetRecord( petDBID, petDataStr )
		# 开始繁殖宠物的处理
		self.pcg_removePet_( petDBID, csdefine.DELETEPET_PROCREATEPET )
		ppm.procreatePet( self.databaseID, self.getName(), dstDatabaseID, petDBID, endTime )

	def pft_remind( self, dstPlayerDBID ):
		"""
		Exposed method.
		宠物繁殖的通知计时放在客户端，客户端收到繁殖信息经过处理确定当前是否已经繁殖完毕，然后向服务器请求相应处理。

		@param dstPlayerDBID : 繁殖对象的dbid
		@type dstPlayerDBID : DATABASE_ID
		"""
		BigWorld.globalData["PetProcreationMgr"].updateProcreateState( self.databaseID, dstPlayerDBID, self )

	def pft_takePet( self, myPetDBID, dstPetDBID ):
		"""
		Define method.
		繁殖成功，获得宠物

		@param myPetDBID : 己方用于繁殖的宠物dbid
		@type myPetDBID : DATABASE_ID
		@param dstPlayerDBID : 对方用于繁殖的宠物dbid
		@type dstPlayerDBID : DATABASE_ID
		"""
		def onUpdateParent( epitome, attrs, res ):
			if res < 0:
				ERROR_MSG( "player( %s ) reduce parents( %i )' life fail when procreated!" % ( self.getName(), epitome.databaseID ) )
			else:
				INFO_MSG( "update life of the pet %i success!" % epitome.databaseID )

		def updateParents( epitome ) :
			life = max( 0, epitome.getAttr( "life" ) - formulas.getProcreateLifeDecreasement() )
			attrs = { "life" : life, "procreated" : csdefine.PET_PROCREATE_STATUS_PROCREATED }
			epitome.updateByDict( attrs, self, Functor( onUpdateParent, epitome, attrs ) )

		def onGetChild( myOwnPetDBID, epitomes, childEpitome ):
			if childEpitome is None :
				ERROR_MSG( "save child pet fail!" )
			else :
				myPetEpitome = epitomes[0]
				if myPetEpitome.databaseID != myOwnPetDBID:
					myPetEpitome = epitomes[1]
				self.pcg_addPet_( myPetEpitome, csdefine.ADDPET_FOSTER )
				self.pcg_addPet_( childEpitome, csdefine.ADDPET_FOSTER )
				self.statusMessage( csstatus.PET_PROCREATE_GET_SUCCESS, childEpitome.getDisplayName() )
				updateParents( myPetEpitome )

				# LOG 信息 17:50 2008-7-21 yk
				species = childEpitome.getAttr("species")
				LOG_MSG( "databaseID(%i), playerName(%s), playerClass(%i), playerLevel(%i), mapMonster(%s), petLevel(%i), petName(%s), hierarchy(%i), ptype(%i), ability(%i)"
					%( self.databaseID, self.getName(), self.getClass(), self.level, childEpitome.getAttr("mapMonster"), childEpitome.getAttr("level"), childEpitome.getAttr("uname"),\
						species & csdefine.PET_HIERARCHY_MASK, species & csdefine.PET_TYPE_MASK, childEpitome.getAttr("ability") ) )

		def onTakePet( success, epitomes ):
			if not success:
				ERROR_MSG( "take procreated pet fail!" )
				self.statusMessage( csstatus.PET_PROCREATE_GET_FAIL_UNKNOW )
			else :
				epitomes = epitomes.values()
				className = epitomes[0].getAttr( "className" )
				child = g_objFactory.getObject( className )
				father, mother = epitomes
				if mother.getAttr( "gender" ) == csdefine.GENDER_MALE :
					father, mother = mother, father
				child.procreatePet( self.databaseID, father, mother, Functor( onGetChild, myPetDBID, epitomes ) )
		queryFosterPets( [myPetDBID, dstPetDBID], onTakePet )
