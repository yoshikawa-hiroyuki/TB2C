//
// Data_DfiSv
//
#include "Data_DfiSv.h"

using namespace std;
using namespace CES;

/* constructors / destructor */

Data_DfiSv::Data_DfiSv()
  : p_refDataDfi(NULL), m_pData(NULL), m_dataLen(0)
{
}

Data_DfiSv::~Data_DfiSv() {
  if ( m_pData )
    delete [] m_pData;
}


/* methods */

bool Data_DfiSv::init(Data_Dfi* pddfi, const Vec3<size_t>* regionIdx) {
  int i, j;
  if ( ! pddfi ) return false;

  p_refDataDfi = pddfi;
  Vec3<size_t> gDiv = p_refDataDfi->m_globalDiv;
  if ( regionIdx ) {
    if ( regionIdx[0][0] >= gDiv[0] || regionIdx[1][0] >= gDiv[0] ||
	 regionIdx[0][1] >= gDiv[1] || regionIdx[1][1] >= gDiv[1] ||
	 regionIdx[0][2] >= gDiv[2] || regionIdx[1][2] >= gDiv[2] ) return false;
    if ( regionIdx[0][0] > regionIdx[1][0] ||
	 regionIdx[0][1] > regionIdx[1][1] ||
	 regionIdx[0][2] > regionIdx[1][2] ) return false;
    m_regionIdx[0] = regionIdx[0]; m_regionIdx[1] = regionIdx[1];
  } else {
    m_regionIdx[0] = Vec3<size_t>(0, 0, 0);
    m_regionIdx[1] = gDiv - Vec3<size_t>(1, 1, 1);
  }

  // setup stpList
  m_numStps = p_refDataDfi->m_timeSliceList.size();
  if ( m_numStps < 1 ) return false;
  m_stpList.resize(m_numStps);
  for ( i = 0; i < m_numStps; i++ ) {
    m_stpList[i].step = p_refDataDfi->m_timeSliceList[i].step;
    m_stpList[i].time = p_refDataDfi->m_timeSliceList[i].time;
  } // end of for(i)

  // component
  m_dataLen = p_refDataDfi->m_dataLen;
  if ( m_dataLen < 1 ) return false;

  // get total dims of region as m_dims
  m_dims[0] = m_dims[1] = m_dims[2] = 0;
  Vec3<size_t> en_max;
  for ( i = 0; i < p_refDataDfi->m_brickList.size(); i++ ) {
    Vec3<size_t> en = p_refDataDfi->m_brickList[i].headIdx
      + p_refDataDfi->m_brickList[i].voxelSize;
    if ( i == 0 ) {
      en_max = en;
      continue;
    }
    for ( j = 0; j < 3; j++ )
      if ( en_max[j] < en[j] ) en_max[j] = en[j];
  } // end of for(i)
  m_dims = en_max;

  if ( ! setCurrentStepIdx(0) ) return false;
  return true;
}

bool Data_DfiSv::setCurrentStepIdx(const size_t stpIdx) {
  if ( ! p_refDataDfi ) return false;
  size_t stp = stpIdx;
  if ( stp >= m_numStps ) return false;
  if ( p_refDataDfi->m_brickType == Data_Dfi::Brick_NONE ||
       p_refDataDfi->m_filePrefix.empty() ) return false;
  size_t dimSz = m_dims[0] * m_dims[1] * m_dims[2];
  size_t datSz = dimSz * m_dataLen;
  if ( datSz < 1 ) return false;
  m_pData = new float[datSz];
  if ( ! m_pData ) return false;

  // read in
  string base_dir = p_refDataDfi->getBaseDir();
  register size_t ii, jj, kk, ll, pi;
  register size_t i, j, k, idx;
  Vec3<size_t> index;
  Vec3<size_t> gDiv = p_refDataDfi->m_globalDiv;
  size_t gDivSz = gDiv[0] * gDiv[1] * gDiv[2];
  if ( gDivSz < 1 ) return false;
  idx = gDiv[0]*gDiv[1]*m_regionIdx[0][2] + gDiv[0]*m_regionIdx[0][1]
    + m_regionIdx[0][0];
  Data_Dfi::BrickInfo& bi0 = p_refDataDfi->m_brickList[idx];

  float* pfDat = NULL;
  for ( k = m_regionIdx[0][2]; k <= m_regionIdx[1][2]; k++ )
    for ( j = m_regionIdx[0][1]; j <= m_regionIdx[1][1]; j++ )
      for ( i = m_regionIdx[0][0]; i <= m_regionIdx[1][0]; i++ ) {
	idx = gDiv[0]*gDiv[1]*k + gDiv[0]*j + i;
	Data_Dfi::BrickInfo& bi = p_refDataDfi->m_brickList[idx];
	string path = base_dir;
	if ( ! path.empty() ) path += '/';
	path += p_refDataDfi->m_dirPath;
	if ( ! path.empty() ) path += '/';
	path += p_refDataDfi->m_filePrefix;
	char buff[32];
	size_t tstp = m_stpList[stp].step;
	if ( gDivSz == 1 ) {
	  sprintf(buff, "_%010lu", tstp);
	} else {
	  if ( p_refDataDfi->m_filenameStepRank )
	    sprintf(buff, "_%010lu_id%06lu", tstp, idx);
	  else
	    sprintf(buff, "_id%06lu_%010lu", idx, tstp);
	}
	path += string(buff);
	path += string(".sph");

	size_t brkSz = bi.voxelSize[0] * bi.voxelSize[1] * bi.voxelSize[2]
	  * m_dataLen;
	pfDat = new float[brkSz];
	if ( ! pfDat ) return false;

	bool rret = ReadinSph(path, pfDat, p_refDataDfi->m_numGc);
	if ( ! rret ) return false;

	for ( kk = 0; kk < bi.voxelSize[2]; kk++ )
	  for ( jj = 0; jj < bi.voxelSize[1]; jj++ )
	    for ( ii = 0; ii < bi.voxelSize[0]; ii++ ) {
	      index = bi.headIdx + Vec3<size_t>(ii, jj, kk);
	      index = index - bi0.headIdx;
	      pi = m_dims[0]*m_dims[1]*index[2] +m_dims[0]*index[1] +index[0];
	      idx = bi.voxelSize[0]*bi.voxelSize[1]*kk
		+ bi.voxelSize[0]*jj + ii;
	      for ( ll = 0; ll < m_dataLen; ll++ ) {
		m_pData[pi*m_dataLen + ll] = pfDat[idx*m_dataLen + ll];
	      } // end of for(ll)
	    } // end of for(ii)
      } // end of for(i)

  if ( pfDat ) {
    delete [] pfDat;
  }

  return true;
}

// STATIC
bool Data_DfiSv::ReadinSph(const string& path, float* pd, const size_t gc) {
  unsigned char buff[32];
  int* pib = (int*)(&buff[4]);
  long long* plb = (long long*)(&buff[4]);
  float* pfb = (float*)(&buff[4]);
  double* pdb = (double*)(&buff[4]);
  Vec3<size_t> dims;
  size_t dataLen;
  if ( ! pd ) return false;

  // open the file
  FILE* fp = fopen(path.c_str(), "rb");
  if ( ! fp ) {
    return false;
  }

  // read headers
  if ( fread(buff, 1, 16, fp) < 16 ) {
    fclose(fp); return false;
  }
  switch ( pib[0] ) {
  case 1: // scalar
    dataLen = 1;
    break;
  case 2: // vector
    dataLen = 3;
    break;
  default:
    fclose(fp); return false;
  }
  
  bool dblPrec = false;
  switch ( pib[1] ) {
  case 1: break; // single precision
  case 2: dblPrec = true; break; // double precision
  default:
    fclose(fp); return false;
  }

  // read dims, org, pitch, time
  if ( dblPrec ) {
    if ( fread(buff, 1, 32, fp) < 32 ) {
      fclose(fp); return false;
    }
    dims[0] = (size_t)plb[0];
    dims[1] = (size_t)plb[1];
    dims[2] = (size_t)plb[2];
    if ( dims[0]*dims[1]*dims[2] < 1 ) {
      fclose(fp); return false;
    }
    if ( fseek(fp, 88 + 4, SEEK_CUR) != 0 ) {
      fclose(fp); return false;
    }
  } else {
    if ( fread(buff, 1, 20, fp) < 20 ) {
      fclose(fp); return false;
    }
    dims[0] = (size_t)pib[0];
    dims[1] = (size_t)pib[1];
    dims[2] = (size_t)pib[2];
    if ( dims[0]*dims[1]*dims[2] < 1 ) {
      fclose(fp); return false;
    }
    if ( fseek(fp, 56 + 4, SEEK_CUR) != 0 ) {
      fclose(fp); return false;
    }
  }

  // alloc data
  if ( dims[0] <= 2*gc || dims[1] <= 2*gc || dims[2] <= 2*gc ) {
    fclose(fp); return false;
  }
  size_t dimSz = dims[0] * dims[1] * dims[2] * dataLen;
  float* pfData = new float[dimSz];
  if ( ! pfData ) {
    fclose(fp); return false;
  }

  // read data
  if ( dblPrec ) {
    register size_t k = dims[0] * dataLen;
    double* pDblData = new double[k];
    if ( ! pDblData ) {
      fclose(fp); return false;
    }
    register size_t dimSzJK = dims[1] * dims[2];
    register size_t i, j, idx = 0;
    for ( i = 0; i < dimSzJK; i++ ) {
      if ( fread(pDblData, sizeof(double), k, fp) != k ) {
        delete [] pDblData;
        fclose(fp); return false;
      }
      for ( j = 0; j < k; j++ ) {
        pfData[idx++] = (float)pDblData[j];
      } // end of for(j)
    } // end of for(i)
    delete [] pDblData;
  }
  else {
    if ( fread(pfData, 4, dimSz, fp) < dimSz ) {
      fclose(fp); return false;
    }
  }
  fclose(fp);

  if ( gc == 0 ) {
    memcpy(pd, pfData, 4 * dimSz);
    delete [] pfData;
    return true;
  }

  // omit gc
  Vec3<size_t> xdims = dims - Vec3<size_t>(2*gc, 2*gc, 2*gc);
  size_t xdimSz = xdims[0] * xdims[1] * xdims[2] * dataLen;
  float* xpfData = pd;

  register size_t i, j, k, l, idx0, idx = 0;
  for ( k = gc; k < dims[2] - gc; k++ )
    for ( j = gc; j < dims[1] - gc; j++ )
      for ( i = gc; i < dims[0] - gc; i++ ) {
	idx0 = dims[0]*dims[1]*k + dims[0]*j + i;
	for ( l = 0; l < dataLen; l++, idx++ )
	  xpfData[idx] = pfData[idx0*dataLen + l];
      } // end of for(i)

  delete [] pfData;
  return true;
}
