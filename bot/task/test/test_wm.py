# -*- coding: gb18030 -*-

import Target
import unittest
from ..taskapps import apps


class WMTest(unittest.TestCase):

	def __init__(self, name=""):
		unittest.TestCase.__init__(self, name)
		self.target = None

	def setUp(self):
		self.target = Target.Target()

	def test_enter_wm1(self):
		taskapp = apps.create_taskapp("wm1_xin_ban_xin_shou_cun")
		appdata = apps.get_app_data("wm1_xin_ban_xin_shou_cun")

		self.assertEqual(len(taskapp.tasks), len(appdata[1]))

		self.assertEqual(taskapp.tasks[0].spaceLabel, appdata[1]["Teleport"][0])
		self.assertEqual(taskapp.tasks[0].position, appdata[1]["Teleport"][1])

		self.assertEqual(taskapp.tasks[1].wait_time, appdata[1]["Wait"][0])
		self.assertEqual(taskapp.tasks[1].timer_id, 0)

		self.assertEqual(taskapp.tasks[2].position, appdata[1]["Move"][0])

		self.assertEqual(taskapp.currentIndex, -1)

		taskapp.do(self.target)

		self.assertEqual(taskapp.target(), self.target)
		self.assertEqual(taskapp.currentIndex, 0)

		self.assertEqual(taskapp.tasks[1].timer_id, 0)

	def test_enter_all_wm(self):
		taskapp = apps.create_taskapp("all_wm_xin_ban_xin_shou_cun")
		appdata = apps.get_app_data("all_wm_xin_ban_xin_shou_cun")

		self.assertEqual(len(taskapp.tasks), len(appdata[1]))

		taskapp.do(self.target)

		self.assertEqual(taskapp.target(), self.target)
		self.assertEqual(taskapp.currentIndex, 0)

	def test_custom_combine_template(self):
		taskapp = apps.create_taskapp("test_custom_combine")
		appdata = apps.get_app_data("test_custom_combine")

		self.assertEqual(len(taskapp.tasks), len(appdata[1]))

		self.assertEqual(taskapp.tasks[0].spaceLabel, "xin_ban_xin_shou_cun")
		self.assertEqual(taskapp.tasks[0].position, (-185, 28.6, -128))

		taskapp.do(self.target)

		self.assertEqual(taskapp.target(), self.target)
		self.assertEqual(taskapp.currentIndex, 0)

	def test_custom_parallel_template(self):
		taskapp = apps.create_taskapp("test_custom_parallel")
		appdata = apps.get_app_data("test_custom_parallel")

		self.assertEqual(len(taskapp.tasks), len(appdata[1]))

		self.assertEqual(taskapp.tasks[0].spaceLabel, "xin_ban_xin_shou_cun")
		self.assertEqual(taskapp.tasks[0].position, (-185, 28.6, -128))

		self.assertEqual(taskapp.doneCounter, 0)

		taskapp.do(self.target)

		self.assertEqual(taskapp.doneCounter, len(appdata[1]))


def test():
	suite = unittest.TestSuite()
	suite.addTest( unittest.makeSuite( WMTest, "test" ) )

	textRunner = unittest.TextTestRunner()
	textRunner.run( suite )
