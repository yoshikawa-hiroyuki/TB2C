// concatSph main
#include <cstdio>
#include "Data_Dfi.h"
#include "Data_DfiSv.h"

using namespace std;
using namespace CES;

int main(int argc, char** argv) {
  string dfipath;
  if ( argc > 1 )
    dfipath = string(argv[1]);
  else {
    fprintf(stderr, "usage: %s infile.dfi\n", argv[0]);
    exit(1);
  }

  Data_Dfi dfi;
  dfi.init(dfipath);

  Data_DfiSv dfiSv;
  dfiSv.init(&dfi);

}
