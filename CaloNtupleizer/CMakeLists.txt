cmake_minimum_required(VERSION 3.15)
project(CaloNtupleizer LANGUAGES CXX)

# ----------------------------
# Dependencies
# ----------------------------
find_package(ROOT REQUIRED COMPONENTS
    RIO
    Tree
    Hist
    MathCore
    Physics
    ROOTDataFrame
)

find_package(podio REQUIRED)
find_package(EDM4HEP REQUIRED)
find_package(DD4hep REQUIRED)

# FastJet — no CMake config file shipped, use fastjet-config instead
find_program(FASTJET_CONFIG NAMES fastjet-config REQUIRED
    DOC "Path to fastjet-config script")
execute_process(
    COMMAND ${FASTJET_CONFIG} --cxxflags
    OUTPUT_VARIABLE FASTJET_CXX_FLAGS
    OUTPUT_STRIP_TRAILING_WHITESPACE)
execute_process(
    COMMAND ${FASTJET_CONFIG} --libs
    OUTPUT_VARIABLE FASTJET_LIBS
    OUTPUT_STRIP_TRAILING_WHITESPACE)
execute_process(
    COMMAND ${FASTJET_CONFIG} --prefix
    OUTPUT_VARIABLE FASTJET_PREFIX
    OUTPUT_STRIP_TRAILING_WHITESPACE)
message(STATUS "FastJet prefix   : ${FASTJET_PREFIX}")
message(STATUS "FastJet cxxflags : ${FASTJET_CXX_FLAGS}")
message(STATUS "FastJet libs     : ${FASTJET_LIBS}")

# Convert space-separated flags to a list for CMake
separate_arguments(FASTJET_CXX_FLAGS_LIST UNIX_COMMAND "${FASTJET_CXX_FLAGS}")
separate_arguments(FASTJET_LIBS_LIST      UNIX_COMMAND "${FASTJET_LIBS}")

# ----------------------------
# Compiler setup
# ----------------------------
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# ----------------------------
# Source and header files
# ----------------------------
file(GLOB sources src/*.cc)
file(GLOB headers RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} CaloNtupleizer/*.h)
list(FILTER headers EXCLUDE REGEX "LinkDef.h")

set(DICT_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/CaloNtupleizer/CaloNtupleizer.h)
set(LINKDEF      ${CMAKE_CURRENT_SOURCE_DIR}/CaloNtupleizer/LinkDef.h)

# ----------------------------
# Build shared library
# ----------------------------
add_library(CaloNtupleizer SHARED
    ${sources}
    ${CaloNtupleizerDict}
)

target_include_directories(CaloNtupleizer PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
    $<INSTALL_INTERFACE:include>
    ${VDT_INCLUDE_DIR}
    ${FASTJET_PREFIX}/include
)

target_compile_options(CaloNtupleizer PRIVATE
    ${FASTJET_CXX_FLAGS_LIST}
)

target_link_libraries(CaloNtupleizer PUBLIC
    ROOT::RIO
    ROOT::Tree
    ROOT::Hist
    ROOT::MathCore
    ROOT::Physics
    ROOT::ROOTDataFrame
    podio::podio
    podio::podioRootIO
    podio::podioDataSource
    EDM4HEP::edm4hep
    EDM4HEP::edm4hepDict
    DD4hep::DDCore
    ${FASTJET_LIBS_LIST}
)

message("${headers}")
ROOT_GENERATE_DICTIONARY(G__CaloNtupleizer
                         ${DICT_HEADERS}
                         LINKDEF CaloNtupleizer/LinkDef.h
                         MODULE CaloNtupleizer
)

# ----------------------------
# Installation
# ----------------------------
include(GNUInstallDirs)

set_target_properties(CaloNtupleizer PROPERTIES
    PUBLIC_HEADER "${headers}"
)

install(TARGETS CaloNtupleizer
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/CaloNtupleizer
)

# Install JetClustering.h alongside CaloNtupleizer headers
install(FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/CaloNtupleizer/JetClustering.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/CaloNtupleizer
)

# The rootmap file
install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/libCaloNtupleizer.rootmap"
    DESTINATION "${CMAKE_INSTALL_LIBDIR}" COMPONENT dev)

# The RDict PCM file (for modern ROOT)
if (${ROOT_VERSION} GREATER 6)
    install(FILES
        "${CMAKE_CURRENT_BINARY_DIR}/libCaloNtupleizer_rdict.pcm"
        DESTINATION "${CMAKE_INSTALL_LIBDIR}" COMPONENT dev)
endif()