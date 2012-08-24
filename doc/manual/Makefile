# Makefile for Arbwave manual

STY=../common-tex-sty

TEXINPUTS=$(STY):$(STY)/gloss:

PAPER=manual

LATEX=latex

DVIPDF=dvipdfm -p letter

#DVIPDF=dvipdf -dSAFER -sPAPERSIZE=letter
#   -dPDFSETTINGS=/printer -dCompatibilityLevel=1.3 \
#   -dMaxSubsetPct=100 -dSubsetFonts=true -dEmbedAllFonts=true

MKINDEX=makeindex

BSTINPUTS=":../common-tex-sty/gloss:./common-tex-sty"

all: pdfall

pdfall:
	make DVIOUT=false dviall
	make pdf

ifeq ($(DVIOUT),)
    DVIOUT=true
endif

.PHONY: DVIoutput.tex
DVIoutput.tex:
	@echo "\setboolean{DVIoutput}{$(DVIOUT)}" > $@

dviall: DVIoutput.tex
	make dvi
	make biball
	make dvi
	make dvi
	make index
	make dvi

dvi $(PAPER)-dvi:
	(export TEXINPUTS=$(TEXINPUTS) && $(LATEX) $(PAPER))

pdf:$(PAPER).dvi
	$(DVIPDF) $(PAPER)

$(PAPER).ps:  $(PAPER).dvi
	dvips -Ppdf -G0 $(PAPER)

distribution: all clean

#manual.htm.tar.gz:  manual.dvi
#	latex2html manual
#	tar cf - manual | gzip -c >manual.htm.tar.gz

index:
	$(MKINDEX) $(PAPER)

bib:
	export BSTINPUTS=${BSTINPUTS} ; \
	bibtex $(PAPER)

biball:
	@export BSTINPUTS=$(BSTINPUTS) ; \
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

LATEX_GARBAGE=$(PAPER).blg $(PAPER).end $(PAPER).bbl $(PAPER).lof \
              $(PAPER).aux  $(PAPER).dvi  $(PAPER).log  $(PAPER).toc \
              $(PAPER).sym.aux $(PAPER).sym.blg $(PAPER).sym.bbl \
              $(PAPER).idx $(PAPER).ilg $(PAPER).ind $(PAPER).loa \
              $(PAPER).lot $(PAPER).out $(PAPER).brf \
              DVIoutput.tex

clean:
	$(RM) $(LATEX_GARBAGE)
