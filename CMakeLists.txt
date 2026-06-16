cmake_minimum_required(VERSION 3.17)
project(pygit2 LANGUAGES C)

find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)
find_package(libgit2 REQUIRED)

# Generate the CFFI C source for _libgit2 at configure time.
# _run.py --emit-c-code only writes the wrapper; the actual compile flags
# (include dirs, libraries) come from the CMake target below.
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
# Use stable ABI (abi3) by default; free-threaded Python (GIL disabled) does not
# support Py_LIMITED_API so fall back to the version-specific suffix.
execute_process(
    COMMAND ${Python3_EXECUTABLE} -c
        "import sysconfig; print(sysconfig.get_config_var('Py_GIL_DISABLED') or 0)"
    OUTPUT_VARIABLE _PYTHON_GIL_DISABLED
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

Python3_add_library(_libgit2 MODULE WITH_SOABI ${CFFI_GENERATED_C})
if(NOT _PYTHON_GIL_DISABLED EQUAL 1)
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
target_include_directories(_pygit2 PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/src")
target_link_libraries(_pygit2 PRIVATE libgit2::libgit2)
install(TARGETS _pygit2 DESTINATION pygit2)
