@echo off
REM Compilation script for LaTeX manuscript
REM Run this from the latex_manuscript directory

echo Compiling LaTeX manuscript...
echo.

REM First pass - generate aux files
pdflatex -interaction=nonstopmode manuscript.tex

REM Generate bibliography
bibtex manuscript

REM Second pass - incorporate references
pdflatex -interaction=nonstopmode manuscript.tex

REM Third pass - finalize cross-references
pdflatex -interaction=nonstopmode manuscript.tex

echo.
echo Compilation complete!
echo Output: manuscript.pdf
echo.

REM Clean up auxiliary files (optional)
REM Uncomment the lines below to auto-delete auxiliary files
REM del manuscript.aux manuscript.bbl manuscript.blg manuscript.log manuscript.out manuscript.toc

pause
