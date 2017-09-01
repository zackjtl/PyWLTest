//---------------------------------------------------------------------------
#pragma hdrstop
#include "interface.h"
#include <stdio.h>
//---------------------------------------------------------------------------
void* __stdcall file_open(const char* FilePath, const char* Flags)
{
  return (void*)fopen(FilePath, Flags);
}
//---------------------------------------------------------------------------
unsigned int __stdcall file_write(const void* Buffer, unsigned int BlockSize, unsigned int Count, void* File)
{
  uint written = fwrite(Buffer, BlockSize, Count, (FILE*)File);
  fflush((FILE*)File);

  return written;
}
//---------------------------------------------------------------------------

