@ECHO OFF
REM Demarre le serveur Web Tours avec Strawberry Perl dans le PATH.
REM Les scripts CGI commencent par "#!perl" : sans perl dans le PATH du
REM processus Apache, toutes les pages cgi-bin repondent "500 Internal Server Error".
SETLOCAL
IF "%PERL_HOME%"=="" SET "PERL_HOME=C:\strawberry\perl\bin"
IF NOT EXIST "%PERL_HOME%\perl.exe" (
    ECHO perl.exe introuvable dans %PERL_HOME% - installez strawberry-perl ou definissez PERL_HOME.
    EXIT /B 1
)
SET "PATH=%PERL_HOME%;C:\strawberry\c\bin;%PATH%"
CD /D "%~dp0..\WebTours"
ECHO Web Tours : http://127.0.0.1:1080/WebTours/index.htm  (CTRL-C pour arreter)
bin\httpd.exe -d "%CD%"
