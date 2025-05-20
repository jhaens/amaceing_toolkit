#include <pybind11/pybind11.h>
#include <pybind11/stl.h>  // For STL containers like std::vector
#include "default_analyzer.h"  // Include your C++ implementation

namespace py = pybind11;

PYBIND11_MODULE(default_analyzer, m) {
    m.doc() = "Python bindings for the default analyzer C++ code";

    // Expose the `compute_analysis` function
    m.def("compute_analysis", &compute_analysis, 
          py::arg("coord_filename"),
          py::arg("pbc_filename"),
          py::arg("timestep_md"),
          py::arg("rdf_pairs"),
          py::arg("msd_atoms"),
          py::arg("smsd_atoms"),
          py::arg("autocorr_pairs"),
          "Run the analysis pipeline (RDF, MSD, sMSD, autocorrelation)");

    // Expose the `terminal_input` function (optional)
    m.def("terminal_input", &terminal_input, 
          py::arg("args"),
          "Run the analysis pipeline from terminal input");
}
