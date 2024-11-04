import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/treelike')))

from treelike import TreeLike

import uuid

class Tree(TreeLike):
	@property
	def children(self):
		return self._children

	@children.setter
	def children(self, value: list['TreeLike']):
		self._children = value

	def __init__(self):
		super().__init__()
		self.uuid = str(uuid.uuid4())
		self._children = []
		self.test = []
		self.repr_include_falsy = False
		self.repr_keys = False
		# self.repr_spacing = 1
		# self.repr_symbols = {
		# 	"vertical": "│",
		# 	"horizontal": "─",
		# 	"corner": "└",
		# 	"intersection": "├",
		# 	"arrow": "►",
		# 	"space": " "
		# }
		# self.repr_vertical = " "
		# self.repr_horizontal = "⎯"
		# self.repr_corner = "✦"
		# self.repr_intersection = "✦"
		# self.repr_arrow = ">"
		# self.repr_space = " "

	def repr_uuid(self):
		return 'uuid', self.uuid[-3:]

	def repr_self(self):
		return "1"

	# def repr_self(self):
	# 	return 'a'

	def __eq__(self, other):
		return self.uuid == other.uuid

root = Tree()
child1 = Tree()
child2 = Tree()
child3 = Tree()
grandchild1 = Tree()
grandchild2 = Tree()
grandchild3 = Tree()
great_grandchild1 = Tree()

root.children = [child1, child2]
child1.children = [grandchild1, grandchild2]
child2.children = [grandchild3]
grandchild1.children = [great_grandchild1]

print(root.pretty())
print(root)