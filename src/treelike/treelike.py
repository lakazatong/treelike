from abc import abstractmethod

def create_symbol_property(symbol_name):
	def getter(self):
		return getattr(self, f"_repr_{symbol_name}")

	def setter(self, value):
		if not isinstance(value, str) or len(value) != 1:
			raise ValueError(f"{symbol_name} must be a single-character string.")
		setattr(self, f"_repr_{symbol_name}", value)

	return property(getter, setter)

class TreeLike:
	own_attrs = None
	
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

	def __init__(self):
		self.repr_whitelist = set() # only if within the set
		self.repr_blacklist = set() # only if not within the set
		self.repr_keys = True # key=value instead of just value
		self.repr_hidden = False # attributes starting with _
		self.repr_by_default = False # attributes that are neither in white or black list
		self.repr_falsy = False # include values like empty lists, False booleans and None
		self.repr_tree_like = False # these attributes
		self.repr_escape_newlines = True
		self._repr_spacing = 2
		self._repr_symbols = {
			"vertical": "│",
			"horizontal": "─",
			"corner": "└",
			"intersection": "├",
			"arrow": "►",
			"space": " "
		}
		for k, v in self._repr_symbols.items():
			setattr(self.__class__, f'repr_{k}', create_symbol_property(k))
			setattr(self, f"_repr_{k}", v)

	def _pretty(self, stack: list['TreeLike']) -> str:
		depth = len(stack)
		stack.append(self)
		r = ""
		for i in range(depth):
			if stack[i + 1] != self:
				r += (self._repr_space if stack[i].children and stack[i].children[-1] == stack[i + 1] else self._repr_vertical) + self._repr_space + self._repr_space * self._repr_spacing
			else:
				r += (self._repr_corner if stack[i].children[-1] == self else self._repr_intersection) + self._repr_horizontal * self._repr_spacing + self._repr_arrow
		r += str(self) + "\n"
		for child in self.children: r += child._pretty(stack)
		stack.pop()
		return r

	def pretty(self) -> str:
		stack = [self]
		r = str(self) + "\n"
		for child in self.children: r += child._pretty(stack)
		return r[:-1] # ignore last \n

	def __repr__(self):
		filtered_attrs = {}
		for k, v in vars(self).items():
			if (not self.repr_tree_like and k in TreeLike.own_attrs) \
				or (not self.repr_hidden and k.startswith('_')) \
				or k in self.repr_blacklist \
				or (k not in self.repr_whitelist and not self.repr_by_default) \
				or (not v and not self.repr_falsy):
				continue
			filtered_attrs[k] = str(v)
		repr_items = []
		for k, v in filtered_attrs.items():
			repr_method_name = f'repr_{k}'
			to_append = None
			if hasattr(self, repr_method_name):
				repr_key, repr_value = getattr(self, repr_method_name)()
				to_append = f"{repr_key}={repr_value}" if self.repr_keys else str(repr_value)
			else:
				to_append = f"{k}={v}" if self.repr_keys else v
			repr_items.append(to_append.replace('\n', '\\n') if self.repr_escape_newlines else to_append)

		classname = self.__class__.__name__
		repr_class_name = f'repr_self'
		if hasattr(self, repr_class_name):
			classname = getattr(self, repr_class_name)()
		attrs = ', '.join(repr_items)
		return f'{classname}({attrs})'

if not TreeLike.own_attrs:
	class _DummyTree(TreeLike):
		@property
		def children(self): return None
		def __eq__(self, other): return True
		def __init__(self): super().__init__()
	TreeLike.own_attrs = set(vars(_DummyTree()).keys())
	del _DummyTree