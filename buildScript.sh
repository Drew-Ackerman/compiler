#!/bin/bash
./nasm.exe  -f win32 basicsExample.asm
./link.exe /OUT:basicsExample.exe msvcrtd.lib basicsExample.obj
./basicsExample.exe
sleep 12