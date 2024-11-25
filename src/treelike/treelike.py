from abc import abstractmethod
from repr import Repr

warn = True

def create_symbol_property(symbol_name):
	def getter(self):
		return getattr(self, f'_repr_{symbol_name}')

	if symbol_name == 'arrow':
		def setter(self, value):
			global warn
			if not isinstance(value, str):
				raise ValueError(f'{symbol_name} must be a string.')
			setattr(self, f'_repr_{symbol_name}', value)
			self._extra_spacing = sum(1 for c in value if c.isspace())
			if warn and '\t' in value:
				print('treelike: Warning: tabs in symbols are not supported, it may not look right')
				warn = False
	else:		
		def setter(self, value):
			global warn
			if not isinstance(value, str) or len(value) != 1:
				raise ValueError(f'{symbol_name} must be a single-character string.')
			setattr(self, f'_repr_{symbol_name}', value)
			if warn and '\t' in value:
				print('treelike: Warning: tabs in symbols are not supported, it may not look right')
				warn = False

	return property(getter, setter)

class TreeLike(Repr):
	@property
	@abstractmethod
	def children(self):
		pass

	@children.setter
	@abstractmethod
	def children(self, value):
		pass

	@abstractmethod
	def __hash__(self):
		pass
	
	def __eq__(self, other):
		return hash(self) == hash(other)

	def __ne__(self, other):
		return hash(self) != hash(other)

	def __init__(self):
		super().__init__()
		self._repr_spacing = 1
		self._repr_symbols = {
			"vertical": "│",
			"horizontal": "─",
			"corner": "└",
			"intersection": "├",
			"arrow": "► ",
			"space": " "
		}
		for k, v in self._repr_symbols.items():
			setattr(self.__class__, f'repr_{k}', create_symbol_property(k))
			setattr(self, f"_repr_{k}", v)
		self._extra_spacing = 1

	@property
	def repr_symbols(self):
		return self._repr_symbols

	@repr_symbols.setter
	def repr_symbols(self, symbols):
		if any(not isinstance(value, str) or len(value) != 1 for value in symbols.values()):
			raise ValueError("All values must be single-character strings.")
		self._repr_symbols = symbols
		for key, value in symbols.items():
			setattr(self, f"_repr_{key}", value)

	@property
	def repr_spacing(self):
		return self._repr_spacing

	@repr_spacing.setter
	def repr_spacing(self, spacing):
		if not isinstance(spacing, int) or spacing < 0:
			raise ValueError("Spacing must be a positive integer.")
		self._repr_spacing = spacing

	def _pretty(self, stack, seen):
		depth = len(stack)
		stack.append(self)
		r = ""
		def add_to_r(node, depth, stack, last):
			nonlocal r
			for i in range(depth - 1):
				if stack[i + 1] != node or stack[i + 1] in seen:
					r += (node._repr_space if stack[i].children and stack[i].children[-1] == stack[i + 1] else node._repr_vertical) + node._repr_space + node._repr_space * (node._repr_spacing + node._extra_spacing)
			r += (node._repr_corner if stack[depth - 1].children[-1] == node and last else node._repr_intersection) + node._repr_horizontal * node._repr_spacing + node._repr_arrow + str(node) + "\n"
		add_to_r(self, depth, stack, True)
		if self not in seen:
			seen.add(self)
			for child in self.children:
				n = self.children.count(child)
				if child in seen:
					if n == 1:
						add_to_r(child, depth + 1, stack + [child], True)
					continue
				if n > 1:
					for _ in range(n-1):
						add_to_r(child, depth + 1, stack + [child], False)
				r += child._pretty(stack, seen)
		stack.pop()
		return r

	def pretty(self):
		r = str(self) + "\n"
		for child in self.children:
			r += child._pretty([self], set([self]))
		return r[:-1]  # ignore last \n