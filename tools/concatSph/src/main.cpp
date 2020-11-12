// concatSph main
#include <cstdio>
#include <algorithm>
#include <regex>
#include "Data_Dfi.h"
#include "Data_DfiSv.h"

using namespace std;
using namespace CES;

void usage(const char* prog) {
  fprintf(stderr, "usage: %s -i infile.dfi -o outfile_%%s_.sph [-s step]\n",
	  prog);
}

char* getArgOption(char** begin, char** end, const string& option) {
  char** itr = std::find(begin, end, option);
  if (itr != end && ++itr != end) {
    return *itr;
  }
  return 0;
}

bool argOptionExists(char** begin, char** end, const string& option) {
  return std::find(begin, end, option) != end;
}


int main(int argc, char** argv) {
  string dfipath, sphpath;
  int tstp = -1;
  if ( argOptionExists(argv, argv+argc, "-h") ) {
    usage(argv[0]);
    exit(0);
  }
  char* dfifn = getArgOption(argv, argv+argc, "-i");
  if ( dfifn ) dfipath = string(dfifn);
  char* sphfn = getArgOption(argv, argv+argc, "-o");
  if ( sphfn ) sphpath = string(sphfn);
  char* sstp =  getArgOption(argv, argv+argc, "-s");
  if ( sstp ) tstp = atoi(sstp);
  if ( dfipath.empty() || sphpath.empty() ) {
    fprintf(stderr, "%s: no input.dfi nor output.sph specified.\n", argv[0]);
    usage(argv[0]);
    exit(1);
  }

  Data_Dfi dfi;
  if ( ! dfi.init(dfipath) ) {
    fprintf(stderr, "%s: read failed: %s\n", argv[0], dfipath.c_str());
    exit(1);
  }

  Data_DfiSv dfiSv;
  if ( ! dfiSv.init(&dfi) ) {
    fprintf(stderr, "%s: parse failed: %s\n", argv[0], dfipath.c_str());
    exit(1);
  }

  if ( tstp < 0 ) {
    for ( size_t stp = 0; stp < dfiSv.m_numStps; stp++ ) {
      if ( ! dfiSv.setCurrentStepIdx(stp) ) {
	fprintf(stderr, "%s: read SPHs failed: step=%lu\n", argv[0], stp);
	exit(1);
      }
      printf("step=%lu read.", stp);

      // write
      char stp_buff[16];
      sprintf(stp_buff, "%06lu", stp);
      string path = regex_replace(sphpath, regex("%s"), stp_buff);
      if ( ! dfiSv.saveSphFile(path) ) {
	fprintf(stderr, "%s: write SPH failed: %s\n", argv[0], path.c_str());
	exit(1);
      }
      printf(" write %s done.\n", path.c_str());
      
    } // end of for(stp)
  } else {
    size_t stp = (size_t)tstp;
    if ( ! dfiSv.setCurrentStepIdx(stp) ) {
      fprintf(stderr, "%s: read SPHs failed: step=%lu\n", argv[0], stp);
      exit(1);
    }
    printf("step=%lu read.", stp);

    // write
    char stp_buff[16];
    sprintf(stp_buff, "%06lu", stp);
    string path = regex_replace(sphpath, regex("%s"), stp_buff);
    if ( ! dfiSv.saveSphFile(path) ) {
      fprintf(stderr, "%s: write SPH failed: %s\n", argv[0], path.c_str());
      exit(1);
    }
    printf(" write %s done.\n", path.c_str());
  }
}
