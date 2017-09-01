//---------------------------------------------------------------------------
#pragma hdrstop
#include "interface.h"
//---------------------------------------------------------------------------
void __stdcall Generate(unsigned char* InBuf, unsigned int Size, unsigned int Seed)
{
  TRandomMersenne random(Seed);
  random.Generate(InBuf, Size);
}
//---------------------------------------------------------------------------

