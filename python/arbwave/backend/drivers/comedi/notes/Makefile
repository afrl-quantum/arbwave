noinst_PROGRAMS = ao_mmap

LIBS = -lcomedi -lm
EXTRA = common.c
CC = gcc

all: $(noinst_PROGRAMS)

%: %.c
	$(CC) $(EXTRA) $@.c $(LIBS) -o $@
board_info:
	$(CC) $(EXTRA) info.c $(LIBS) -o $@

clean:
	rm -f *.o
	rm -rf .libs
	@list='$(noinst_PROGRAMS)'; for p in $$list; do \
	  rm -f $$p ; \
	done


