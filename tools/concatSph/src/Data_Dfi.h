//
// Data_Dfi
//
#ifndef _DATA_DFI_H_
#define _DATA_DFI_H_

#include <string>
#include <deque>
#include <vector>

#include "utilMath.h"
typedef float vector2[2];

//----------------------------------------------------------------
// class Data_Dfi
//----------------------------------------------------------------
class Data_Dfi
{
public:
  enum BrickType {Brick_NONE=0, Brick_Sph, Brick_P3dF};

  struct TimeSlice {
    int   step;
    float time;
    vector2 vecMinMax;
    std::deque<float> datMin, datMax;
    TimeSlice(const int stp=0, const float tm=0.f, const size_t vlen=0)
      : step(stp), time(tm) {
      vecMinMax[0] = vecMinMax[1] = 0.f;
      if ( vlen > 0 ) {datMin.resize(vlen, 0); datMax.resize(vlen, 0);}
    }
  };

  struct BrickInfo {
    CES::Vec3<size_t> voxelSize;
    CES::Vec3<size_t> headIdx; // starts from [0,0,0]
    int ID;
    BrickInfo(const int id=-1) : ID(id) {}
  };

  Data_Dfi();
  virtual ~Data_Dfi();

  BrickType getBrickType() const {return m_brickType;}
  std::string getIndexPath() const {return m_path;}
  std::string getBaseDir() const {return m_baseDir;}
  std::string getProcPath() const {return m_procPath;}
  CES::Vec3<float> getPitch() const;

  //private:
  std::string           m_path;
  std::string           m_baseDir;
  BrickType             m_brickType;
  bool                  m_useTsDir;
  std::string           m_dirPath;
  std::string           m_filePrefix;
  bool                  m_filenameStepRank;
  size_t                m_numGc;
  size_t                m_dataLen;

  std::string           m_procPath;
  std::deque<TimeSlice> m_timeSliceList;

  CES::Vec3<size_t>     m_globalDims;
  CES::Vec3<size_t>     m_globalDiv;
  CES::Vec3<float>      m_globalOrig;
  CES::Vec3<float>      m_globalRegn;

  std::string           m_activeDomainPath;
  unsigned char*        m_activeDomainFlag;

  std::deque<BrickInfo> m_brickList;

  void reset();
  virtual bool init(const std::string& path);
  bool readActiveSubdomainFile();
  static int searchStrVector(const std::vector<std::string>& list,
			     const std::string& x);
};


static bool operator<(const Data_Dfi::BrickInfo& l,
		      const Data_Dfi::BrickInfo& r) {
  if ( l.headIdx[2] != r.headIdx[2] ) return l.headIdx[2] < r.headIdx[2];
  if ( l.headIdx[1] != r.headIdx[1] ) return l.headIdx[1] < r.headIdx[1];
  return l.headIdx[0] < r.headIdx[0];
}

#endif // _DATA_DFI_H_
