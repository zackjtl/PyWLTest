//---------------------------------------------------------------------------
#ifndef interfaceH
#define interfaceH
//---------------------------------------------------------------------------
#include "mersenne.h"

#ifdef __cplusplus
extern "C"{
#endif

__declspec(dllexport) void __stdcall Generate(unsigned char* InBuf, unsigned int Size, unsigned int Seed);

#ifdef __cplusplus
}
#endif
//---------------------------------------------------------------------------
#endif
