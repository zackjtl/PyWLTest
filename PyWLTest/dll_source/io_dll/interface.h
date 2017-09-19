//---------------------------------------------------------------------------
#ifndef interfaceH
#define interfaceH
//---------------------------------------------------------------------------
#include "mersenne.h"

#ifdef __cplusplus
extern "C"{
#endif

__declspec(dllexport) void* __stdcall fopen_4wr(const char* FilePath, const char* Flags);
__declspec(dllexport) unsigned int __stdcall file_write(unsigned char* Buffer, unsigned int BlockSize, unsigned int Count, void* File);

__declspec(dllexport) void* __stdcall fopen_4rd(const char* FilePath, const char* Flags);
__declspec(dllexport) unsigned long __stdcall file_read(unsigned char* Buffer, unsigned long Length, unsigned long* BytesRead, void* File);

__declspec(dllexport) int __stdcall fclose_4wr(void* File);
__declspec(dllexport) int __stdcall fclose_4rd(void* Handle);

#ifdef __cplusplus
}

#endif
//---------------------------------------------------------------------------
#endif
