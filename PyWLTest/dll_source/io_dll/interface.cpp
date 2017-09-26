//---------------------------------------------------------------------------
#pragma hdrstop
#include "interface.h"
#include "random.h"
#include "mersenne.h"
#include "HandleManager.h"
#include <stdio.h>
#include <iostream>
#include <windows.h>
//---------------------------------------------------------------------------
unsigned char** buffer;
int chunkSize;
int maxChunk;
bool forcePatError = false;
bool pattern_created = false;
//---------------------------------------------------------------------------
void* __stdcall fopen_4wr(const char* FilePath, const char* Flags)
{
  return fopen(FilePath, Flags);
}
//---------------------------------------------------------------------------
unsigned int __stdcall file_write(unsigned char* Buffer, unsigned int BlockSize, unsigned int Count, void* File)
{
  uint written = fwrite(Buffer, BlockSize, Count, (FILE*)File);
  fflush((FILE*)File);
  return written;
}
//---------------------------------------------------------------------------
void* __stdcall fopen_4rd(const char* FilePath, const char* Flags)
{
  HANDLE fileHandle = CreateFile(FilePath,
                                 GENERIC_READ,
																 FILE_SHARE_READ,
																 NULL,
																 OPEN_EXISTING,
																 FILE_ATTRIBUTE_NORMAL | FILE_FLAG_NO_BUFFERING ,
																 NULL);

  return fileHandle;
}
//---------------------------------------------------------------------------
unsigned long __stdcall file_read(unsigned char* Buffer, unsigned long Length, unsigned long* BytesRead, void* File)
{
  BOOL result = ::ReadFile((HANDLE)File, Buffer, Length, BytesRead, NULL);
  return result;
}
//---------------------------------------------------------------------------
int __stdcall fclose_4wr(void* File)
{
  return fclose((FILE*)File);
}
//---------------------------------------------------------------------------
int __stdcall fclose_4rd(void* Handle)
{
  return CloseHandle((HANDLE)Handle);
}
//---------------------------------------------------------------------------
int __stdcall init_pattern(int chunk_size, int max_chunk, unsigned int seed)
{
  if (pattern_created) {
    free_buffer();
  }
  chunkSize = chunk_size;
  maxChunk = max_chunk;

  TRandomMersenne random(seed);

  buffer = new unsigned char*[max_chunk];

  for (int i = 0; i < max_chunk; ++i) {
    buffer[i] = new unsigned char[chunk_size * 512];
    random.Generate(buffer[i], chunk_size * 512);
    ////memset(buffer[i], i, chunk_size * 512);
  }
  forcePatError = false;
  pattern_created = true;
}
//---------------------------------------------------------------------------
int __stdcall free_buffer()
{
  if (!pattern_created) {
    return 0;
  }
  for (int i = 0; i < maxChunk; ++i) {
    delete [] buffer[i];
  } 
  delete[] buffer;

  pattern_created = false;
  return 1;
}
//---------------------------------------------------------------------------
TFIO_Res __stdcall file_write_auto_pattern(const char* FilePath, int SectorCount, unsigned int Seed)
{
  FILE* f = fopen(FilePath, "ab");

  CHandleManager handleMan(f);

  TFIO_Res res;

  unsigned int written = 0;
  unsigned int total_written = 0;

  int remain = SectorCount;
  int write_cnt = chunkSize;
  int pat_idx = Seed % maxChunk;
  int total_elapsed = 0;

  int start_tick, chunk_time;

  if (f == NULL) {
    // TODO: handle error
    res.io_count = 0;
    res.spend_time = 0;
    res.error_code = 1;
    goto WRITE_ERROR;
  }

  while (remain > 0) {
    if (remain < chunkSize) {
      write_cnt = remain;
    }
    start_tick = clock();
    written = fwrite(buffer[pat_idx % maxChunk], 512, write_cnt, f);
    fflush(f);
    chunk_time = clock() - start_tick;
    total_elapsed += chunk_time;
    total_written += written;
    remain -= written;
    ++pat_idx;
  }

  res.io_count = total_written;
  res.spend_time = total_elapsed;
  res.error_code = 0;
  res.rsvd = 0;

  return res;

WRITE_ERROR:
  return res;
}
//---------------------------------------------------------------------------
TFIO_Res __stdcall file_read_auto_pattern(const char* FilePath, int SectorCount, unsigned int Seed)
{
  HANDLE fileHandle = CreateFile(FilePath,
                                 GENERIC_READ,
																 FILE_SHARE_READ,
																 NULL,
																 OPEN_EXISTING,
																 FILE_ATTRIBUTE_NORMAL | FILE_FLAG_NO_BUFFERING ,
																 NULL);

  CHandleManager handleMan(fileHandle);

  TFIO_Res res;

  unsigned long readed = 0;
  unsigned int total_readed = 0;

  int remain = SectorCount;
  int read_cnt = chunkSize;
  int pat_idx = Seed % maxChunk;
  int total_elapsed = 0;
  int readed_sectors;
  int start_tick, chunk_time;

  unsigned char* readBuff = new unsigned char[chunkSize * 512];

  if (fileHandle == INVALID_HANDLE_VALUE) {
    // TODO: handle error
    res.error_code = 1;
    goto READ_ERROR;
  }

  while (remain > 0) {
    if (remain < chunkSize) {
      read_cnt = remain;
    }
    start_tick = clock();

    BOOL result = ::ReadFile((HANDLE)fileHandle, readBuff, read_cnt * 512, &readed, NULL);

    chunk_time = clock() - start_tick;

    if (result == 0) {
      res.error_code = 2;
      goto READ_ERROR;
    }
    if (forcePatError) {
      readBuff[500] = ~readBuff[500];
      forcePatError  = false;
    }

    if (memcmp(readBuff, buffer[pat_idx % maxChunk], read_cnt * 512)) {
      res.error_code = 3;
      goto READ_ERROR;
    }

    readed_sectors = (readed / 512);
    total_elapsed += chunk_time;
    total_readed += readed_sectors;
    remain -= readed_sectors;
    ++pat_idx;
  }

  res.io_count = total_readed;
  res.spend_time = total_elapsed;
  res.error_code = 0;
  res.rsvd = 0;

  delete [] readBuff;

  return res;

READ_ERROR:
  delete [] readBuff;
  return res;
}
//---------------------------------------------------------------------------
void __stdcall test_force_pattern_error()
{
  forcePatError = true;
}
//---------------------------------------------------------------------------

