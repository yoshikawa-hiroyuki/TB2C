//
// Data_DfiSv
//
#ifndef _DATA_DFISV_H_
#define _DATA_DFISV_H_

#include "Data_Dfi.h"


//----------------------------------------------------------------
// class Data_DfiSv
//----------------------------------------------------------------
class Data_DfiSv
{
public:
  Data_DfiSv();
  virtual ~Data_DfiSv();

  bool init(Data_Dfi* pddfi, const CES::Vec3<size_t>* regionIdx =NULL);
  class Data_Dfi* getRefDataDfi() {return p_refDataDfi;}
  const CES::Vec3<size_t>* getRegionIdx() const {return m_regionIdx;}
  bool setCurrentStepIdx(const size_t stpIdx);
  bool saveSphFile(const std::string& path) const;

  struct StpUnit {
    int   step;
    float time;
    StpUnit(const int stp =0, const float tm =0.f) : step(stp), time(tm) {}
    StpUnit(const StpUnit& org) {*this = org;}
    void operator=(const StpUnit& org) {step = org.step; time = org.time;}
    bool operator==(const StpUnit& x) {return (step==x.step && time==x.time);}
    bool operator<(const StpUnit& x) {return (step < x.step);}
  };

  //protected:
  class Data_Dfi*     p_refDataDfi;
  CES::Vec3<size_t>   m_regionIdx[2];
  float*              m_pData;
  size_t              m_numStps;
  std::deque<StpUnit> m_stpList; // [m_numSteps]
  CES::Vec3<size_t>   m_dims;
  size_t              m_dataLen;
  size_t              m_currentStepIdx;
  
  static bool ReadinSph(const std::string& path, float* pd, const size_t gc=0);
};

#endif // _DATA_DFISV_H_
