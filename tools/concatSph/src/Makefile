TARGET=concatSph
OBJS=	main.o \
	Data_Dfi.o \
	Data_DfiSv.o

G=-g -O0
LIBS=-L../TextParser/lib -lTP
CXXFLAGS=-I../TextParser/include $(G)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) -o $@ $(OBJS) $(LIBS)

clean:
	rm -f $(OBJS) $(TARGET)
