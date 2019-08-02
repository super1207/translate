python -m pip install --upgrade pip
pip install -r request.txt
pyinstaller -w -F GUI.spec
echo 如果你没有看到报错或警告，那么，说明编译成功了
pause