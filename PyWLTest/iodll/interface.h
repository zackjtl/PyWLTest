//---------------------------------------------------------------------------
#ifndef interfaceH
#define interfaceH
//---------------------------------------------------------------------------
#include "mersenne.h"

#ifdef __cplusplus
extern "C"{
#endif

__declspec(dllexport) void* __stdcall file_open(const char* FilePath, const char* Flags);
__declspec(dllexport) unsigned int __stdcall file_write(const void* Buffer, unsigned int BlockSize, unsigned int Count, void* File);

#ifdef __cplusplus
}
#endif
//---------------------------------------------------------------------------
#endif
