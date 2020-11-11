// concatSph main
#include <cstdio>
#include "Data_Dfi.h"
#include "Data_DfiSv.h"

using namespace std;
using namespace CES;

int main(int argc, char** argv) {
  string dfipath;
  if ( argc > 1 ) {
    dfipath = string(argv[1]);
  } else {
    fprintf(stderr, "usage: %s infile.dfi\n", argv[0]);
    exit(1);
  }

  Data_Dfi dfi;
  if ( ! dfi.init(dfipath) ) {
    fprintf(stderr, "%s: read failed: %s\n", argv[0], dfipath.c_str());
    exit(1);
  }

  Data_DfiSv dfiSv;
  if ( ! dfiSv.init(&dfi) ) {
    fprintf(stderr, "%s: parse failed: %s\n",
	    argv[0], dfipath.c_str());
    exit(1);
  }

  for ( size_t stp = 0; stp < dfiSv.m_numStps; stp++ ) {
    if ( ! dfiSv.setCurrentStepIdx(stp) ) {
      fprintf(stderr, "%s: read SPHs failed: step=%lu\n",
	      argv[0], stp);
      exit(1);
    }
    printf("step=%lu read.\n", stp);

    // write
  }
  
}
