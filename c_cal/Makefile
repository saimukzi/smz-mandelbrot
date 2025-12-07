CC = gcc
CFLAGS = -Wall -Wextra -O2
LIBS = -lmpfr -lgmp

TARGET1 = mandelbrot
TARGET2 = base_convert
SRC1 = mandelbrot.c mpfr_base32.c
SRC2 = base_convert.c mpfr_base32.c

all: $(TARGET1) $(TARGET2)

$(TARGET1): $(SRC1)
	$(CC) $(CFLAGS) -o $(TARGET1) $(SRC1) $(LIBS)

$(TARGET2): $(SRC2)
	$(CC) $(CFLAGS) -o $(TARGET2) $(SRC2) $(LIBS)

clean:
	rm -f $(TARGET1) $(TARGET2)

.PHONY: all clean
