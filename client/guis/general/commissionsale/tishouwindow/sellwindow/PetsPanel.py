# -*- coding: gb18030 -*-
# implement the PetsPanel class
# written by ganjinxing 2009-10-30

from guis import *
from guis.general.vendwindow.sellwindow.PetsPanel import BasePetPanel
from guis.tooluis.inputbox.MoneyInputBox import MoneyInputBox
from config.client.msgboxtexts import Datas as mbmsgs
from LabelGather import labelGather
import csdefine
import csconst
import csstatus


class PetsPanel( BasePetPanel ) :

	def __init__( self, panel, pyBinder = None ) :
		BasePetPanel.__init__( self, panel, pyBinder )
		self.__pyMsgBox = None


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMyPetDraw_( self, pyViewItem ) :
		pyMyPet = pyViewItem.pyPetItem
		pyMyPet.update( pyViewItem )
		pyMyPet.selected = pyViewItem.selected

	def onPetDown_( self ) :
		if not self.__checkOperation() : return
		keepMaxAmount = BigWorld.player().pcg_getKeepingCount()
		curKeepAmount = self.pyMyPanel_.itemCount
		if curKeepAmount >= keepMaxAmount :
			# "您的宠物携带数量已满。"
			self.__showMessage( 0x0321 )
			return
		selSellPet = self.pySellPanel_.selItem
		if selSellPet is None : return
		tishouNPC = self.pyBinder.pyBinder.tishouNPC
		if tishouNPC is not None :
			tishouNPC.cell.takeTSPet( selSellPet.databaseID )

	def onPetUp_( self ) :
		if not self.__checkOperation() : return
		selPet = self.pyMyPanel_.selItem
		if selPet is None : return
		if selPet.isBinded :
			BigWorld.player().statusMessage( csstatus.PET_HAD_BEEN_BIND )
			return
		def addSellPet( result, price ):
			if result == DialogResult.OK:
				if price <= 0:
					# "该宠物还没有定价!"
					showAutoHideMessage( 3.0, 0x0325, mbmsgs[0x0c22], pyOwner = self )
					return
				if BigWorld.player().testAddMoney( price ) > csconst.TRADE_PRICE_UPPER_LIMIT :							# 超过系统规定的金钱上限
					# "价格超出了上限！"
					self.__showMessage( 0x0322 )
					return
				if not self.__checkOperation() : return
				tishouNPC = self.pyBinder.pyBinder.tishouNPC
				if tishouNPC is not None :
					tishouNPC.cell.addTSPet( selPet.databaseID, price )
		MoneyInputBox().show( addSellPet, labelGather.getText( "commissionsale:TiShouPetsPanel", "ipBoxPrice" ), self )

	def onMyPetSelected_( self, index ) :
		"""
		玩家身上的宠物选择发生改变
		"""
		selPet = self.pyMyPanel_.selItem
		tishouNPC = self.pyBinder.pyBinder.tishouNPC
		btnEnable = selPet is not None
		btnEnable &= tishouNPC is not None and not tishouNPC.tsState 				# 摆摊状态下不能操作
		self.pyUpBtn_.enable = btnEnable

	def onSellPetSelected_( self, index ) :
		"""
		正在摆摊的宠物选择发生改变
		"""
		tishouNPC = self.pyBinder.pyBinder.tishouNPC
		btnEnable = index > -1 and tishouNPC and not tishouNPC.tsState				# 摆摊状态下不能操作
		self.pyDownBtn_.enable = btnEnable
		self.pyBinder.enableChangePriceBtn()

	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_TISHOU_PET_REMOVE"] = self.__onSellingPetRemove		# 寄售宠物移去
		self.triggers_["ON_REMOVE_COMMISSION_PET"] = self.__onSellingPetRemove		# 寄售宠物移去
		self.triggers_["EVT_ON_PCG_REMOVE_PET"] = self.onRoleLosePet_ 				# 移除身上的宠物
		self.triggers_["EVT_ON_PCG_ADD_PET"] = self.onRoleGainPet_ 					# 添加待售宠物
		self.triggers_["EVT_ON_TISHOU_PET_SELLING"] = self.__onTSPetSelling 		# 开始替售
		self.triggers_["EVT_ON_TISHOU_PET_UPDATE"] = self.__onPetUpdatePrice		# 宠物价格更新
		for key in self.triggers_ :
			ECenter.registerEvent( key, self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onSellingPetRemove( self, petDBID ) :
		for index, epitome in enumerate( self.pySellPanel_.items ) :
			if epitome.databaseID == petDBID :
				self.pySellPanel_.removeItemOfIndex( index )
				break
		self.pyBinder.onCalcuExpense_()

	def __onTSPetSelling( self, petEpitome, price ) :
		"""
		服务器回调宠物开始寄售
		"""
		if not self.pyBinder.pyBinder.visible : return
		for pEpt in self.pySellPanel_.items :										# 宠物已存在
			if pEpt.databaseID == petEpitome.databaseID :
				return
		petEpitome.rolePrice = price
		self.pySellPanel_.addItem( petEpitome )
		self.pyBinder.onCalcuExpense_()

	def __onPetUpdatePrice( self, petDBID, price ) :
		for index, epitome in enumerate( self.pySellPanel_.items ) :
			if epitome.databaseID == petDBID :
				epitome.rolePrice = price
				self.pySellPanel_.updateItem( index, epitome )
				break
		self.pyBinder.onCalcuExpense_()

	def __showMessage( self, msg ) :
		def query( result ) :
			self.__pyMsgBox = None
		if self.__pyMsgBox is not None :
			self.__pyMsgBox.hide()
		self.__pyMsgBox = showMessage( msg, "", MB_OK, query, None, Define.GST_IN_WORLD )

	def __checkOperation( self ) :
		tishouNPC = self.pyBinder.pyBinder.tishouNPC
		if tishouNPC is None :
			# "未找到寄售NPC！"
			self.__showMessage( 0x0323 )
			return False
		isTishouState = tishouNPC.tsState
		if isTishouState :
			# "请先暂停寄售再进行该操作！"
			self.__showMessage( 0x0324 )
			return False
		return True

	def __queryTSPetInfo( self ) :
		"""
		向服务器申请寄售的宠物数据
		"""
		self.pySellPanel_.clearItems()
		def queryInfo() :
			tishouNPC = self.pyBinder.pyBinder.tishouNPC
			if tishouNPC is not None :
				tishouNPC.cell.queryTSPets()
		if self.visible :
			queryInfo()
		else :
			BigWorld.callback( 0.5, queryInfo )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getSellItems( self ) :
		"""
		获取所有出售的宠物
		"""
		return self.pySellPanel_.items

	def changeItemPrice( self ) :
		if not self.__checkOperation() : return
		selPet = self.pySellPanel_.selItem
		if selPet is None : return
		def changePrice( res, price ):
			if res == DialogResult.OK:
				if price <= 0:
					# "宠物未定价！"
					showAutoHideMessage( 3.0, 0x0325, mbmsgs[0x0c22] )
				elif price != selPet.rolePrice :								# 价格有变动
					if not self.__checkOperation() : return
					if BigWorld.player().testAddMoney( price ) > csconst.TRADE_PRICE_UPPER_LIMIT :				# 超过系统规定的金钱上限
						# "价格超出了上限！"
						self.__showMessage( 0x0322 )
						return
					tishouNPC = self.pyBinder.pyBinder.tishouNPC
					if tishouNPC is not None :
						tishouNPC.cell.updateTSPetPrice( selPet.databaseID, price )
		MoneyInputBox().show( changePrice, labelGather.getText( "commissionsale:TiShouPetsPanel", "ipBoxNewPrice" ), self )

	def onParentHide( self ) :
		pass

	def onParentShow( self ) :
		self.__queryTSPetInfo()

	def onTSNPCFlagChaned( self, oldFlag ) :
		mySelIndex = self.pyMyPanel_.selIndex
		self.onMyPetSelected_( mySelIndex )
		sellSelIndex = self.pySellPanel_.selIndex
		self.onSellPetSelected_( sellSelIndex )

	def onShow( self ) :
		"""
		打开时查询
		"""
		pass

	def dispose( self ) :
		self.triggers_ = {}
		BasePetPanel.dispose( self )

	def __del__( self ) :
		if Debug.output_del_TSPetPanel :
			INFO_MSG( str( self ) )
