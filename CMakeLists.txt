cmake_minimum_required(VERSION 3.17)
project(pygit2 LANGUAGES C)

find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)
find_package(libgit2 REQUIRED)

# Generate the CFFI C source for _libgit2 at configure time.
# Compile flags (include dirs, libraries) come from the CMake target below.
set(CFFI_GENERATED_C "${CMAKE_CURRENT_BINARY_DIR}/_libgit2.c")
execute_process(
    COMMAND ${Python3_EXECUTABLE} -c
        "import sys; sys.path.insert(0, '${CMAKE_CURRENT_SOURCE_DIR}/pygit2'); from _run import ffi; ffi.emit_c_code('${CFFI_GENERATED_C}')"
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    RESULT_VARIABLE CFFI_RESULT
)
if(NOT CFFI_RESULT EQUAL 0)
    message(FATAL_ERROR "CFFI source generation failed (exit code ${CFFI_RESULT})")
endif()

# _libgit2: CFFI Python→libgit2 bridge
# Apply stable ABI (abi3) only for regular CPython: SOABI matches "cpython-NNN-" or "cpNNN-"
# (no trailing 't' before the dash). Free-threaded CPython has 't' in the SOABI
# (cpython-314t-...); PyPy starts with "pypy". Both skip Py_LIMITED_API.
Python3_add_library(_libgit2 MODULE WITH_SOABI ${CFFI_GENERATED_C})
if(Python3_SOABI MATCHES "^(cpython|cp)[0-9]+-")
    target_compile_definitions(_libgit2 PRIVATE Py_LIMITED_API=0x03020000)
    if(WIN32)
        set_target_properties(_libgit2 PROPERTIES SUFFIX ".pyd")
    else()
        set_target_properties(_libgit2 PROPERTIES SUFFIX ".abi3.so")
    endif()
endif()
target_link_libraries(_libgit2 PRIVATE libgit2::libgit2)
install(TARGETS _libgit2 DESTINATION pygit2)

# _pygit2: handwritten C extension
file(GLOB PYGIT2_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/src/*.c")
Python3_add_library(_pygit2 MODULE WITH_SOABI ${PYGIT2_SOURCES})
target_compile_definitions(_pygit2 PRIVATE PY_SSIZE_T_CLEAN)
target_include_directories(_pygit2 PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/src")
target_link_libraries(_pygit2 PRIVATE libgit2::libgit2)
install(TARGETS _pygit2 DESTINATION pygit2)
