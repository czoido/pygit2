import sys
import sysconfig

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout


class Pygit2Conan(ConanFile):
    name = "pygit2"
    settings = "os", "compiler", "build_type", "arch"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("libgit2/1.9.1")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["Python3_EXECUTABLE"] = sys.executable
        tc.cache_variables["Python3_INCLUDE_DIR"] = sysconfig.get_path("include")
        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
