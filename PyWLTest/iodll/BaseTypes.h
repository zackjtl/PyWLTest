#ifndef BaseTypesH
#define BaseTypesH

#ifdef __BORLANDC__
//---------------------------------------------------------------------------
typedef __int64           int64;
//---------------------------------------------------------------------------
typedef unsigned char      byte;
typedef unsigned short     word;
typedef unsigned long     dword;
typedef unsigned __int64  qword;
//---------------------------------------------------------------------------
typedef unsigned char     uchar;
typedef unsigned int      uint;
typedef unsigned long     ulong;
typedef unsigned __int64  uint64;
typedef unsigned __int64  UHYPER;
//---------------------------------------------------------------------------
#elif  __GNUC__

#include <stdint.h>
//---------------------------------------------------------------------------
typedef int64_t 	           int64;
typedef int64_t 	           __int64;
//---------------------------------------------------------------------------
typedef uint8_t           byte;
typedef uint16_t          word;
typedef uint32_t          dword;
typedef uint64_t          qword;
//---------------------------------------------------------------------------
typedef byte     uchar;
typedef unsigned int      uint;
//typedef uint32_t     ulong;
typedef uint64_t     uint64;
//---------------------------------------------------------------------------
typedef byte    BYTE;
typedef uint    UINT;
typedef uchar   UCHAR;
typedef long		LONG;
typedef dword   ULONG;
////typedef ulong	DWORD;
typedef char    CHAR;
typedef CHAR*   PCHAR;
typedef void		VOID;
typedef VOID*		PVOID;
typedef PVOID		LPVOID;
typedef unsigned short USHORT;
////typedef ULONG* ULONG_PTR;
////typedef ULONG* PULONG;
typedef bool		BOOL;
typedef BOOL 		BOOLEAN;
typedef wchar_t WCHAR;
//---------------------------------------------------------------------------
#else
typedef signed long long int 	           int64;
typedef signed long long int 	           __int64;
//---------------------------------------------------------------------------
typedef unsigned char      byte;
typedef unsigned short     word;
typedef unsigned long     dword;
typedef unsigned long long int  qword;
//---------------------------------------------------------------------------
typedef unsigned char     uchar;
typedef unsigned int      uint;
typedef unsigned long     ulong;
typedef unsigned long long int 	  uint64;
//---------------------------------------------------------------------------
typedef byte    BYTE;
typedef uint    UINT;
typedef uchar   UCHAR;
typedef long	LONG;
typedef ulong   ULONG;
typedef ulong	DWORD;
typedef char    CHAR;
typedef CHAR*   PCHAR;
typedef void	VOID;
typedef VOID*	PVOID;
typedef PVOID	LPVOID;
typedef unsigned short USHORT;
typedef ULONG* ULONG_PTR;
typedef ULONG* PULONG;
typedef bool	BOOL;
typedef BOOL BOOLEAN;
typedef wchar_t WCHAR;
#endif

typedef union {
    word ui;
    byte uc[2];
} UN_INT;

typedef union {
  dword ul;
  byte  uc[4];
} UN_UL;
//---------------------------------------------------------------------------
typedef byte uint8;
typedef word uint16;
typedef dword uint32;
//---------------------------------------------------------------------------



#endif
