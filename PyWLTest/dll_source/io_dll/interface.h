//---------------------------------------------------------------------------
#ifndef interfaceH
#define interfaceH
//---------------------------------------------------------------------------
#include "mersenne.h"

extern unsigned char** buffer;
extern int chunkSize;
extern int maxChunk;

extern bool forcePatError;
extern bool pattern_created;

struct TFIO_Res {
  int io_count;
  int spend_time;
  int error_code;
  int rsvd;
};

#ifdef __cplusplus
extern "C"{
#endif

__declspec(dllexport) void* __stdcall fopen_4wr(const char* FilePath, const char* Flags);
__declspec(dllexport) unsigned int __stdcall file_write(unsigned char* Buffer, unsigned int BlockSize, unsigned int Count, void* File);

__declspec(dllexport) void* __stdcall fopen_4rd(const char* FilePath, const char* Flags);
__declspec(dllexport) unsigned long __stdcall file_read(unsigned char* Buffer, unsigned long Length, unsigned long* BytesRead, void* File);

__declspec(dllexport) int __stdcall fclose_4wr(void* File);
__declspec(dllexport) int __stdcall fclose_4rd(void* Handle);

__declspec(dllexport) int __stdcall fclose_4rd(void* Handle);

__declspec(dllexport) int __stdcall init_pattern(int chunk_size, int max_chunk, unsigned int seed);
__declspec(dllexport) int __stdcall free_buffer();

__declspec(dllexport) TFIO_Res __stdcall file_write_auto_pattern(const char* FilePath, int SectorCount, unsigned int Seed);
__declspec(dllexport) TFIO_Res __stdcall file_read_auto_pattern(const char* FilePath, int SectorCount, unsigned int Seed);

__declspec(dllexport) void __stdcall test_force_pattern_error();

#ifdef __cplusplus
}

#endif
//---------------------------------------------------------------------------
#endif
