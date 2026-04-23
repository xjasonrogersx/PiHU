cmake_minimum_required(VERSION 3.10)
project(dab-radio)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -frtti -fexceptions")

find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBUSB REQUIRED libusb-1.0)
pkg_check_modules(MOSQUITTO libmosquitto)

# Find nlohmann_json
find_package(nlohmann_json QUIET)
if(NOT nlohmann_json_FOUND)
  # Try to find it via pkg-config
  pkg_check_modules(NLOHMANN_JSON nlohmann_json)
  if(NOT NLOHMANN_JSON_FOUND)
    message(WARNING "nlohmann_json not found, dab_tuner_aac will not be built")
  endif()
endif()

# Collect all source files
file(GLOB SOURCES "*.cpp")
file(GLOB FEC_SOURCES "fec/*.c")

# Main executables
set(MAINS dab_scan dab_mp2 dab_aac)
if(MOSQUITTO_FOUND AND (nlohmann_json_FOUND OR NLOHMANN_JSON_FOUND))
  list(APPEND MAINS dab_tuner_aac)
endif()

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
if(MOSQUITTO_FOUND AND (nlohmann_json_FOUND OR NLOHMANN_JSON_FOUND))
  include_directories(${MOSQUITTO_INCLUDE_DIRS})
  if(NLOHMANN_JSON_FOUND)
    include_directories(${NLOHMANN_JSON_INCLUDE_DIRS})
  endif()
endif()

# Build each main executable
foreach(main ${MAINS})
    add_executable(${main} ${COMMON_SOURCES} ${FEC_SOURCES} ${main}.cpp)
    target_link_libraries(${main} ${LIBUSB_LIBRARIES})
    
    # Add MQTT and JSON libraries for dab_tuner_aac
    if(main STREQUAL "dab_tuner_aac" AND MOSQUITTO_FOUND)
      target_link_libraries(${main} ${MOSQUITTO_LIBRARIES})
      if(nlohmann_json_FOUND)
        target_link_libraries(${main} nlohmann_json::nlohmann_json)
      elseif(NLOHMANN_JSON_FOUND)
        # If found via pkg-config instead of find_package
        target_link_libraries(${main} ${NLOHMANN_JSON_LIBRARIES})
      endif()
    endif()
endforeach()

