# Makefile for Arbwave manual

STY=../common-tex-sty

TEXINPUTS=$(STY):$(STY)/gloss:

PAPER=manual

LATEX=latex
PDFLATEX=pdflatex

MKINDEX=makeindex

BSTINPUTS="../common-tex-sty/gloss:../common-tex-sty:"

all: $(PAPER).pdf


%.pdf: %.tex repeat ../common-tex-sty/arbwave-version.sty
	(export TEXINPUTS=$(TEXINPUTS) && $(PDFLATEX) $<)

.PHONY: repeat

../common-tex-sty/arbwave-version.sty: repeat
	../common-tex-sty/mk_version.py

distribution: all clean

index:
	$(MKINDEX) $(PAPER)

bib:
	export BSTINPUTS=${BSTINPUTS} ; \
	bibtex $(PAPER)

biball:
	export BSTINPUTS=$(BSTINPUTS) ; \
	for i in *.aux; do bibtex `basename $$i .aux`; done;
	make linkaux


linkaux: cleanaux
	@echo "creating links to all .aux files in chapter directories"
	@for i in $(CHAPTER_DIRS); do \
            if [ "$$i" = "." ]; then \
                continue; \
            fi; \
            echo "$(NOT_CHAPTER)" |grep "$$i" > /dev/null; \
            if [ "$$?" = "1" ]; then \
                for j in *.aux; do \
                    ln -s ../$$j $$i/$$j; \
                done; \
            else \
                echo "skip directory $$i"; \
            fi \
        done;

cleanaux:
	@echo "removing links to all .aux files from chapter directories"
	@for i in $(CHAPTER_DIRS); do \
            if [ "$$i" = "." ]; then \
                continue; \
            fi; \
            echo "$(NOT_CHAPTER)" |grep "$$i" > /dev/null; \
            if [ "$$?" = "1" ]; then \
                for j in *.aux; do \
                    rm -f $$i/$$j; \
                done; \
            else \
                echo "skip directory $$i"; \
            fi \
        done;


spell:
	aspell -t -c $(PAPER).tex;

LATEX_GARBAGE=*.blg *.end *.bbl *.lof \
              *.aux  *.log  *.toc \
              *.idx *.ilg *.ind *.loa \
              *.lot *.out *.brf \
              *Notes.bib

clean:
	$(RM) $(LATEX_GARBAGE)
