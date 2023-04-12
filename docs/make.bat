@REM @ECHO OFF

@REM pushd %~dp0

@REM REM Command file for Sphinx documentation

@REM if "%SPHINXBUILD%" == "" (
@REM 	set SPHINXBUILD=python -msphinx
@REM )
@REM set SOURCEDIR=.
@REM set BUILDDIR=_build
@REM set SPHINXPROJ=aa_pbs_exporter

@REM if "%1" == "" goto help

@REM %SPHINXBUILD% >NUL 2>NUL
@REM if errorlevel 9009 (
@REM 	echo.
@REM 	echo.The Sphinx module was not found. Make sure you have Sphinx installed,
@REM 	echo.then set the SPHINXBUILD environment variable to point to the full
@REM 	echo.path of the 'sphinx-build' executable. Alternatively you may add the
@REM 	echo.Sphinx directory to PATH.
@REM 	echo.
@REM 	echo.If you don't have Sphinx installed, grab it from
@REM 	echo.http://sphinx-doc.org/
@REM 	exit /b 1
@REM )

@REM %SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%
@REM goto end

@REM :help
@REM %SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%

@REM :end
@REM popd
