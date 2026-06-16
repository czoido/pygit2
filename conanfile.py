from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout


class Pygit2Conan(ConanFile):
    name = "pygit2"
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("libgit2/1.9.1")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
