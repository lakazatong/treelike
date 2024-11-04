@echo off
python -m build
for %%f in (dist\*.whl) do (
	pip install "%%f" --force-reinstall
	goto :end
)
:end
