@echo off
echo Today is %date:~,4%-%date:~5,2%-%date:~8,2%, and a good day!
echo I am a small rat,and i like digging holes. I will put one blank line in a hole aftr i diggle it. So, people always call me BlankRat. Now, i am going to search every file of this directory to append one blank line.
echo.

for /r %%i in (*.*) do (
    if not "%%~xi"==".bat" if not "%%~xi"==".log" (
        echo=>>%%i
        echo %%i
    )
)
    
pause
