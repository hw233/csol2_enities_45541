# -*- coding: gb18030 -*-

import Target
import unittest
from ..taskapps import apps
from .. import Task
from .. import TaskGroup


class PGroupTest(unittest.TestCase):

	def __init__(self, name=""):
		unittest.TestCase.__init__(self, name)
		self.target = None

	def setUp(self):
		self.target = Target.Target()

	def test_parallel_group(self):
		task = TaskGroup.ParallelTaskGroup()
		task.addTask(Task.Move((0,0,0)))
		task.addTask(Task.Wait(5))

		self.assertEqual(len(task.tasks), 2)
		self.assertEqual(task.doneCounter, 0)

		task.do(self.target)

		self.assertEqual(task.doneCounter, 2)


def test():
	suite = unittest.TestSuite()
	suite.addTest( unittest.makeSuite( PGroupTest, "test" ) )

	textRunner = unittest.TextTestRunner()
	textRunner.run( suite )
