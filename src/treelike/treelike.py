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
		for i in range(depth - 1):
			if stack[i + 1] != self or stack[i + 1] in seen:
				r += (self._repr_space if stack[i].children and stack[i].children[-1] == stack[i + 1] else self._repr_vertical) + self._repr_space + self._repr_space * (self._repr_spacing + self._extra_spacing)
		r += (self._repr_corner if stack[depth - 1].children[-1] == self else self._repr_intersection) + self._repr_horizontal * self._repr_spacing + self._repr_arrow + str(self) + "\n"
		if self not in seen:
			seen.add(self)
			for child in self.children:
				r += child._pretty(stack, seen)
		stack.pop()
		return r

	def pretty(self):
		r = str(self) + "\n"
		for child in self.children:
			r += child._pretty([self], set())
		return r[:-1]  # ignore last \n