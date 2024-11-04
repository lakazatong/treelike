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
	def children(self) -> list['TreeLike']:
		pass

	@children.setter
	@abstractmethod
	def children(self, value: list['TreeLike']):
		pass

	@abstractmethod
	def __eq__(self, other: object) -> bool:
		pass

	def __ne__(self, other: object) -> bool:
		return not (self == other)

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

	def _pretty(self, stack: list['TreeLike']) -> str:
		depth = len(stack)
		stack.append(self)
		r = ""
		for i in range(depth):
			if stack[i + 1] != self:
				r += (self._repr_space if stack[i].children and stack[i].children[-1] == stack[i + 1] else self._repr_vertical) + self._repr_space + self._repr_space * (self._repr_spacing + self._extra_spacing)
			else:
				r += (self._repr_corner if stack[i].children[-1] == self else self._repr_intersection) + self._repr_horizontal * self._repr_spacing + self._repr_arrow
		r += str(self) + "\n"
		for child in self.children:
			r += child._pretty(stack)
		stack.pop()
		return r

	def pretty(self) -> str:
		stack = [self]
		r = str(self) + "\n"
		for child in self.children:
			r += child._pretty(stack)
		return r[:-1]  # ignore last \n