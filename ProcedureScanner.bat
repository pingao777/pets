@echo off
set ym=%date:~,4%%date:~5,2%
set today=%date:~8,2%
set /a yesterday=%date:~8,2% - 1
set old=高阶表依赖关系(%ym%%yesterday%).txt
set new=高阶表依赖关系(%ym%%today%).txt

java -jar ProcedureSpider.jar>%new%&&echo 创建%new%成功。

fc %new% %old%
if %errorlevel%==0 echo 删除%old%&&del %old%

pause 
