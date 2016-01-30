@echo off
set ym=%date:~,4%%date:~5,2%
set today=%date:~8,2%
set /a yesterday=%date:~8,2% - 1
set old=高阶表依赖关系(%ym%%yesterday%).txt
set new=高阶表依赖关系(%ym%%today%).txt

set start_time=%time%
java -jar ProcedureSpider.jar>%new%
set end_time=%time%

set log=ProcedureScanner.log
echo 日期：%ym%%today%，起始时间：%start_time%，结束时间：%start_time%>>%log%
fc /N %new% %old%>>%log%
del %old%
