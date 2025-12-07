CC = gcc
CFLAGS = -Wall -Wextra -O2
LIBS = -lmpfr -lgmp

TARGET = mandelbrot
SRC = mandelbrot.c mpfr_base32.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LIBS)

clean:
	rm -f $(TARGET)

.PHONY: all clean
