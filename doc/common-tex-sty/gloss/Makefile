ALL :
	pdflatex sample
	for i in *.aux; do bibtex $$i; done
	pdflatex sample
	pdflatex sample
	pdflatex sample

clean :
	$(RM) *.aux *.bbl *.blg *.gls.aux *.gls.bbl *.gls.blg *.log *.pdf \
	      *.sym.aux *.sym.bbl *.sym.blg *.out
