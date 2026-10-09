# CMake toolchain file - Arm GNU Toolchain (arm-none-eabi) for STM32F746 (Cortex-M7, FPv5-SP)
# Used by beta/stm32/CMakeLists.txt. Tested with Arm GNU Toolchain 14.2.Rel1 (see README.md).
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

# Allow overriding the toolchain location: -DTOOLCHAIN_PREFIX=/path/to/bin/arm-none-eabi-
if(NOT DEFINED TOOLCHAIN_PREFIX)
  find_program(_GCC arm-none-eabi-gcc
    PATHS /opt/homebrew/bin $ENV{HOME}/opt/arm-gnu-toolchain/bin /Applications/ArmGNUToolchain/*/arm-none-eabi/bin
    NO_CACHE)
  if(_GCC)
    get_filename_component(_BIN ${_GCC} DIRECTORY)
    set(TOOLCHAIN_PREFIX ${_BIN}/arm-none-eabi-)
  else()
    set(TOOLCHAIN_PREFIX arm-none-eabi-)
  endif()
endif()

set(CMAKE_C_COMPILER   ${TOOLCHAIN_PREFIX}gcc)
set(CMAKE_CXX_COMPILER ${TOOLCHAIN_PREFIX}g++)
set(CMAKE_ASM_COMPILER ${TOOLCHAIN_PREFIX}gcc)
set(CMAKE_OBJCOPY      ${TOOLCHAIN_PREFIX}objcopy CACHE FILEPATH "objcopy")
set(CMAKE_SIZE         ${TOOLCHAIN_PREFIX}size    CACHE FILEPATH "size")
set(CMAKE_OBJDUMP      ${TOOLCHAIN_PREFIX}objdump CACHE FILEPATH "objdump")

# Cross-compiling: do not try to run test executables
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
set(CMAKE_EXECUTABLE_SUFFIX_C   .elf)
set(CMAKE_EXECUTABLE_SUFFIX_CXX .elf)
set(CMAKE_EXECUTABLE_SUFFIX_ASM .elf)

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
