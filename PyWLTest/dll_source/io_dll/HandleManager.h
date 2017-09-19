//---------------------------------------------------------------------------
#ifndef HandleManagerH
#define HandleManagerH
//---------------------------------------------------------------------------
#include <stdio.h>
#include <windows.h>
//---------------------------------------------------------------------------
class CHandleManager
{
public:
  CHandleManager(HANDLE Handle)
    : _Handle(Handle),
      _File(NULL)
  {
  }
  CHandleManager(FILE* File)
    : _Handle(INVALID_HANDLE_VALUE),
      _File(File)
  {
  }
  ~CHandleManager() {
    if (_File != NULL) {
      fclose(_File);
    }
    else if (_Handle != INVALID_HANDLE_VALUE) {
      CloseHandle(_Handle);
    }
  }

private:
  HANDLE  _Handle;
  FILE*   _File;
};
//---------------------------------------------------------------------------
#endif
