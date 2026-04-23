cmake_minimum_required(VERSION 3.10)
project(dab-radio)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -frtti -fexceptions")

find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBUSB REQUIRED libusb-1.0)

# Collect all source files
file(GLOB SOURCES "*.cpp")
file(GLOB FEC_SOURCES "fec/*.c")

# Main executables
set(MAINS dab_scan dab_mp2 dab_aac)

# Common objects (all sources except main files)
set(COMMON_SOURCES)
foreach(source ${SOURCES})
    get_filename_component(basename ${source} NAME_WE)
    if(NOT basename IN_LIST MAINS)
        list(APPEND COMMON_SOURCES ${source})
    endif()
endforeach()

# Include directories
include_directories(${LIBUSB_INCLUDE_DIRS})

# Build each main executable
foreach(main ${MAINS})
    add_executable(${main} ${COMMON_SOURCES} ${FEC_SOURCES} ${main}.cpp)
    target_link_libraries(${main} ${LIBUSB_LIBRARIES})
endforeach()
