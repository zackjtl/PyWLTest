//---------------------------------------------------------------------------
#pragma hdrstop
#include "interface.h"
#include "random.h"
#include <stdio.h>
#include <iostream>
#include <windows.h>
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

