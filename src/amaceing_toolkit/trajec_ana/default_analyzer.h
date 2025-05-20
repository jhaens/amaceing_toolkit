#ifndef DEFAULT_ANALYZER_H
#define DEFAULT_ANALYZER_H

#include <vector>
#include <string>

void compute_analysis(
    const std::string& coord_filename,
    const std::string& pbc_filename,
    const float& timestep_md,
    const std::vector<std::vector<std::string>>& rdf_pairs,
    const std::vector<std::string>& msd_atoms,
    const std::vector<std::string>& smsd_atoms,
    const std::vector<std::vector<std::string>>& autocorr_pairs);

int terminal_input(const std::vector<std::string>& args);

#endif // DEFAULT_ANALYZER_H