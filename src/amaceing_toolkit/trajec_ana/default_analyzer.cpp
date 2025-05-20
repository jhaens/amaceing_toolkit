// Filename: default_analyzer.cpp
// Description: [Analysis of default functions in a given xyz file -> MSD, RDF, sMSD, AUTOCORR]
// Author: [Jonas Hänseroth]
// Date: [31.03.2025]

//How to run: ./analyzer_default coords.xyz pbc <timestep [fs]> <atom_types: MSD...H, RDF...H-H, sMSD...*H, AUTOCORR...@H-H>


#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
#include <string>
#include <cmath>
#include <chrono> // For high resolution clock
#include <tuple> 
#include <stack> // For stack data structure
#include <queue> // For queue data structure
#include <unordered_set> // For unordered_set
#include <algorithm> // For std::sort and std::find
#include <numeric> // For std::partial_sum
#include <omp.h>  // Include OpenMP header
#include <unordered_map> // for atom masses list
#include <cstdlib>  // For std::stoi (to parse strings to integers, for command line arguments)
#include "default_analyzer.h"

using namespace std;



//########################
//## IN/OUTPUT FUNCTION ##
//########################

// Function to create two arrays: one for coordinates and one for atom names
std::pair<std::vector<std::vector<float>>, std::vector<std::string>> create_arr(const int no_atoms) {
    // Struct for storing coordinates for each atom (no_atoms x 3)
    struct Coordinates_per_frame {
        std::vector<std::vector<float>> arr;
        
        Coordinates_per_frame(int size) {
            arr.resize(size, std::vector<float>(3, 0.000f));  // Initialize with 0.000f
        }
    };

    // Struct for storing atom names
    struct Atom {
        std::vector<std::string> arr;
        
        Atom(int size) {
            arr.resize(size, "");  // Initialize with empty strings
        }
    };

    Coordinates_per_frame coords(no_atoms);
    Atom atoms(no_atoms);

    // Return the pair of coordinates and atom names
    return std::make_pair(coords.arr, atoms.arr);
}


// Optimized function to read the XYZ file
pair<std::vector<std::vector<std::vector<float>>>, std::vector<std::string>> read_xyz(const string& filename) {
    ifstream inputFile(filename);

    if (!inputFile) {
        cerr << "Error opening XYZ file!" << endl;
        return {}; // Return empty pair in case of error
    }

    // Read the number of atoms (first line of the file)
    string firstLine;
    getline(inputFile, firstLine);
    int no_atoms = stoi(firstLine);

    // Create the 3D Coordinates arrays
    auto array_pair = create_arr(no_atoms);
    auto coords_per_frame = array_pair.first;
    auto atoms = array_pair.second;

    // Read the file's first no_atoms lines to store the atom names
    string skipLine;
    getline(inputFile, skipLine); // Skip comment line

    for (int i = 0; i < no_atoms; ++i) {
        string atomLine;
        getline(inputFile, atomLine);
        istringstream stream(atomLine);

        string atomElement;
        stream >> atomElement;  // Read atom name
        atoms[i] = atomElement;  // Store atom name
    }

    // Move the file pointer back to the beginning
    inputFile.seekg(0); // Move the file pointer back to the beginning

    // Now, let's read the entire file into memory
    vector<string> file_lines;
    string line;
    while (getline(inputFile, line)) {
        file_lines.push_back(line);
    }

    // Calculate number of frames
    long long num_frames = (file_lines.size()) / (no_atoms + 2);

    // Preallocate memory for all frames
    std::vector<std::vector<std::vector<float>>> all_frames(num_frames, std::vector<std::vector<float>>(no_atoms, std::vector<float>(3, 0.0f)));

    // Parallelize the processing of frames (we already read the file in memory)
    #pragma omp parallel for
    for (int frame_idx = 0; frame_idx < num_frames ; ++frame_idx) {
        int frame_start_line = 2 + (frame_idx * (no_atoms + 2));  // Skip the first 2 lines

        // Process the coordinates for this frame
        for (int i = 0; i < no_atoms; ++i) {
            string coordLine = file_lines[frame_start_line + i]; // Skip the comment line
            istringstream stream(coordLine);

            string atomElement;
            float x, y, z;
            stream >> atomElement >> x >> y >> z;

            // Store coordinates for the current atom in the frame
            all_frames[frame_idx][i][0] = x;
            all_frames[frame_idx][i][1] = y;
            all_frames[frame_idx][i][2] = z;
        }
    }

    inputFile.close();
    return make_pair(all_frames, atoms);
}

// Function to read the PBC file (3x3 matrix) which has the matrix as output
vector<vector<float>> read_pbc(const string& filename) {
    ifstream inputFile(filename);

    if (!inputFile) {
        cerr << "Error opening PBC file!" << endl;
        return {}; // Return empty vector in case of error
    }

    vector<vector<float>> pbc(3, vector<float>(3,0.00f));  // 3x3 matrix to store the PBC values
    string pbcLine;
    for (int i = 0; i < 3; ++i) {
        getline(inputFile, pbcLine);
        istringstream stream(pbcLine);
        for (int j = 0; j < 3; ++j) {
            stream >> pbc[i][j];
        }
    }

    inputFile.close();
    
    // Return the PBC matrix
    return pbc;
}

// Write a xyz file from a coordinates array
void write_xyz(const string& filename, const vector<vector<vector<float>>>& coords, const vector<string>& atoms, const int every_n_frame = 1) {
    ofstream outputFile(filename);

    if (!outputFile) {
        cerr << "Error opening output file!" << endl;
        return;
    }

    // Number of atoms
    int number_of_atoms =  coords[0].size();

    // Write the coordinates
    for (size_t i = 0; i < coords.size()-1; ++i) {
        if (every_n_frame == 1) {
                    outputFile << number_of_atoms << endl;
                    outputFile << "Comment line" << endl;
                }
                else {
                    if (i % every_n_frame == 0) {
                        outputFile << number_of_atoms << endl;
                        outputFile << "Comment line" << endl;
                    }
                }
        for (size_t j = 0; j < coords[i].size(); ++j) {
            if (every_n_frame == 1) {
                outputFile << atoms[j] << " " << coords[i][j][0] << " " << coords[i][j][1] << " " << coords[i][j][2] << endl;
            }
            else {
                if (i % every_n_frame == 0) {
                    outputFile << atoms[j] << " " << coords[i][j][0] << " " << coords[i][j][1] << " " << coords[i][j][2] << endl;
                }
            }
        }
    }

    outputFile.close();
}

// Function to parse atom types from command line arguments
void parse_atom_types(const std::vector<std::string>& args,
    std::vector<std::vector<std::string>>& rdf_pairs,
    std::vector<std::string>& msd_atoms,
    std::vector<std::string>& smsd_atoms,
    std::vector<std::vector<std::string>>& autocorr_pairs) {

    // Parse the command-line arguments to fill rdf_pairs and msd_atoms
    for (size_t i = 4; i < args.size(); ++i) {
        std::string arg = args[i];

        // Check if first character is a "*" -> sMSD
        if (arg[0] == '*') {
            std::string atom = arg.substr(1);
            smsd_atoms.push_back(atom);
        }

        // Check if first character is a "@" -> autocorr 
        else if (arg[0] == '@') {
            arg = arg.substr(1);
            if (arg.size() == 3 && isalpha(arg[0]) && arg[1] == '-' && isalpha(arg[2])) {
                std::string atom1 = arg.substr(0, 1);
                std::string atom2 = arg.substr(2, 1);;
                autocorr_pairs.push_back({atom1, atom2});
            }
            else if (arg.size() == 4 && isalpha(arg[0]) && isalpha(arg[1]) && arg[2] == '-' && isdigit(arg[3])) {          
                std::string atom1 = arg.substr(0, 2);
                std::string atom2 = arg.substr(3, 1);
                autocorr_pairs.push_back({atom1, atom2});
            }
            else if (arg.size() == 4 && isalpha(arg[0]) && arg[1] == '-' && isalpha(arg[2]) && isalpha(arg[3])) {
                std::string atom1 = arg.substr(0, 1);
                std::string atom2 = arg.substr(2, 2);
                autocorr_pairs.push_back({atom1, atom2});
            }
            else if (arg.size() == 5 && isalpha(arg[0]) && isalpha(arg[1]) && arg[2] == '-' && isdigit(arg[3]) && isdigit(arg[4])) {
                std::string atom1 = arg.substr(0, 2);
                std::string atom2 = arg.substr(3, 2);
                autocorr_pairs.push_back({atom1, atom2});
            }
            else {
            std::cerr << "Invalid atom type or pair: " << arg << std::endl;
            exit(1);  // Exit on error
            }
        }

        // Check if it's a pair of atoms including a - (3 to 5 digits) -> RDF
        else if (arg.size() == 3 && isalpha(arg[0]) && arg[1] == '-' && isalpha(arg[2])) {
            std::string atom1 = arg.substr(0, 1);
            std::string atom2 = arg.substr(2, 1);;
            rdf_pairs.push_back({atom1, atom2});
        }
        else if (arg.size() == 4 && isalpha(arg[0]) && isalpha(arg[1]) && arg[2] == '-' && isdigit(arg[3])) {          
            std::string atom1 = arg.substr(0, 2);
            std::string atom2 = arg.substr(3, 1);
            rdf_pairs.push_back({atom1, atom2});
        }
        else if (arg.size() == 4 && isalpha(arg[0]) && arg[1] == '-' && isalpha(arg[2]) && isalpha(arg[3])) {
            std::string atom1 = arg.substr(0, 1);
            std::string atom2 = arg.substr(2, 2);
            rdf_pairs.push_back({atom1, atom2});
        }
        else if (arg.size() == 5 && isalpha(arg[0]) && isalpha(arg[1]) && arg[2] == '-' && isdigit(arg[3]) && isdigit(arg[4])) {
            std::string atom1 = arg.substr(0, 2);
            std::string atom2 = arg.substr(3, 2);
            rdf_pairs.push_back({atom1, atom2});
        }
        // Check if it's a single atom (length 1 to 2) -> MSD
        else if (arg.size() == 2 && isalpha(arg[0]) && isalpha(arg[1])) {
            msd_atoms.push_back(arg);
        }
        else if (arg.size() == 1 && isalpha(arg[0])) {
            msd_atoms.push_back(arg);
        }

        else {
        std::cerr << "Invalid atom type or pair: " << arg << std::endl;
        exit(1);  // Exit on error
        }
    }
}


//#######################
//## MATRIX OPERATIONS ##
//#######################

// Function to multiply two 3x3 matrices
std::vector<std::vector<float>> matrix_multiply(const std::vector<std::vector<float>>& a, const std::vector<std::vector<float>>& b) {
    std::vector<std::vector<float>> result(3, std::vector<float>(3, 0.0f));
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            for (int k = 0; k < 3; ++k) {
                result[i][j] += a[i][k] * b[k][j];
            }
        }
    }
    return result;
}

// Function to multiply a 3x3 matrix with a 3D vector
std::vector<float> matrix_vector_multiply(const std::vector<std::vector<float>>& matrix, const std::vector<float>& vec) {
    std::vector<float> result(3, 0.0f);
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            result[i] += matrix[i][j] * vec[j];
        }
    }
    return result;
}

// Function to calculate the determinant of a 3x3 matrix
float matrix_determinant(const std::vector<std::vector<float>>& matrix) {
    return matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]) -
           matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0]) +
           matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]);
}

// Function to calculate the inverse of a 3x3 matrix
std::vector<std::vector<float>> matrix_inverse(const std::vector<std::vector<float>>& matrix) {
    float det = matrix_determinant(matrix);
    if (det == 0.0f) {
        throw std::runtime_error("Matrix is singular and cannot be inverted.");
    }

    std::vector<std::vector<float>> inverse(3, std::vector<float>(3, 0.0f));
    inverse[0][0] = (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]) / det;
    inverse[0][1] = (matrix[0][2] * matrix[2][1] - matrix[0][1] * matrix[2][2]) / det;
    inverse[0][2] = (matrix[0][1] * matrix[1][2] - matrix[0][2] * matrix[1][1]) / det;
    inverse[1][0] = (matrix[1][2] * matrix[2][0] - matrix[1][0] * matrix[2][2]) / det;
    inverse[1][1] = (matrix[0][0] * matrix[2][2] - matrix[0][2] * matrix[2][0]) / det;
    inverse[1][2] = (matrix[0][2] * matrix[1][0] - matrix[0][0] * matrix[1][2]) / det;
    inverse[2][0] = (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]) / det;
    inverse[2][1] = (matrix[0][1] * matrix[2][0] - matrix[0][0] * matrix[2][1]) / det;
    inverse[2][2] = (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) / det;

    return inverse;
}

//#######################
//## PBC_DIST FUNCTION ##
//#######################

// Function to decide if the pbc is ortho or not
bool is_ortho(const std::vector<std::vector<float>>& pbc) {
    // Check if the PBC matrix is orthogonal by checking if the off-diagonal elements are zero
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            if (i != j && pbc[i][j] != 0.0f) {
                return false; // Not orthogonal
            }
        }
    }
    return true; // Orthogonal
}


// Function to calculate the distance between two atoms with PBC: ortho and non-ortho decision
std::vector<std::vector<float>> pbc_dist_norm(const std::vector<std::vector<float>>& coords1,
    const std::vector<std::vector<float>>& coords2,
    const std::vector<std::vector<float>>& pbc) {

    // Check if the PBC matrix is orthogonal
    bool is_ortho_pbc = is_ortho(pbc);

    // Initialize the 2D array to store the norm of the distances
    std::vector<std::vector<float>> norm_distance(coords1.size(), std::vector<float>(coords2.size(), 0.0f));

    if (is_ortho_pbc) {
        // Use the orthogonal PBC distance calculation (no relative coordinates, 10 percent faster)
        for (size_t j = 0; j < coords1.size(); ++j) {
            for (size_t k = 0; k < coords2.size(); ++k) {
                // Calculate the distance vector first
                std::vector<float> distance_vector(3, 0.0f);
                for (int dim = 0; dim < 3; ++dim) {
                    distance_vector[dim] = coords1[j][dim] - coords2[k][dim];

                    // Apply periodic boundary conditions using modulo
                    distance_vector[dim] = distance_vector[dim] - pbc[dim][dim] * round(distance_vector[dim] / pbc[dim][dim]);
                }

                // Calculate the norm of the distance
                norm_distance[j][k] = sqrt(pow(distance_vector[0], 2) + pow(distance_vector[1], 2) + pow(distance_vector[2], 2));
            }
        }


    }
    else {
        // Use the non-orthogonal PBC distance calculation (relative coordinates)
        // Calculate the inverse of the PBC matrix
        std::vector<std::vector<float>> inv_pbc = matrix_inverse(pbc);

        // Transform each coordinate using matrix-vector multiplication
        std::vector<std::vector<float>> transformed_coords1(coords1.size(), std::vector<float>(3, 0.0f));
        std::vector<std::vector<float>> transformed_coords2(coords2.size(), std::vector<float>(3, 0.0f));

        for (size_t i = 0; i < coords1.size(); ++i) {
            transformed_coords1[i] = matrix_vector_multiply(inv_pbc, coords1[i]);
        }
        for (size_t i = 0; i < coords2.size(); ++i) {
            transformed_coords2[i] = matrix_vector_multiply(inv_pbc, coords2[i]);
        }
        
        // Calculate the relative distance between coord1 and coord2
        for (size_t j = 0; j < transformed_coords1.size(); ++j) {
            for (size_t k = 0; k < transformed_coords2.size(); ++k) {
                std::vector<float> relative_coords(3, 0.0f);
                for (int dim = 0; dim < 3; ++dim) {
                    relative_coords[dim] = transformed_coords1[j][dim] - transformed_coords2[k][dim];
                    relative_coords[dim] -= round(relative_coords[dim]);
                    }

                // Transform the relative coordinates back to real space
                std::vector<float> real_coords = matrix_vector_multiply(pbc, relative_coords);
                
                // Calculate the norm of the distance
                norm_distance[j][k] = sqrt(pow(real_coords[0], 2) + pow(real_coords[1], 2) + pow(real_coords[2], 2));
            }
        }
    }

    return norm_distance;
}

//############################
//## NEXT NEIGHBOR FUNCTION ##
//############################

// Function to find nearest neighbors between two sets of atomic coordinates
std::tuple<std::vector<int>, std::vector<float>> next_neighbor(
    const std::vector<std::vector<float>>& atom_1,
    const std::vector<std::vector<float>>& atom_2,
    const std::vector<std::vector<float>>& pbc_mat) {
    
    // Calculate the distance matrix
    std::vector<std::vector<float>> dist_list = pbc_dist_norm(atom_1, atom_2, pbc_mat);
    
    std::vector<int> nearest_indices(atom_1.size());
    std::vector<float> min_distances(atom_1.size());
    
    // For each atom in atom_1, find closest atom in atom_2
    for (size_t i = 0; i < atom_1.size(); ++i) {
        float min_dist = std::numeric_limits<float>::max();
        int min_idx = -1;
        
        for (size_t j = 0; j < atom_2.size(); ++j) {
            if (dist_list[i][j] < min_dist) {
                min_dist = dist_list[i][j];
                min_idx = j;
            }
        }
        
        nearest_indices[i] = min_idx;
        min_distances[i] = min_dist;
    }
    
    return std::make_tuple(nearest_indices, min_distances);
}

//###################################
//## MOLECULE RECOGNITION FUNCTION ##
//###################################

// Function to calculate the bond distances and find molecules via next-neighbor binning
std::unordered_map<std::string, int> find_molecules_nextneighborbinning(const std::vector<std::vector<float>>& norm_distance,
    const std::vector<std::string>& atoms) {
    
    // Get number of atoms
    size_t num_atoms = atoms.size();
    
    // Initialize the bond graph using adjacency list for better cache locality
    std::vector<std::vector<int>> bond_graph(num_atoms);
    
    // Identify unique atom pairs that appear in the system
    std::unordered_map<std::string, std::vector<float>> pair_distances;
    
    // Collect distances for each atom pair type
    for (size_t i = 0; i < num_atoms; ++i) {
        for (size_t j = i + 1; j < num_atoms; ++j) {
            std::string atom_pair = atoms[i] + "-" + atoms[j];
            // Also add the reverse pair for easier lookup later
            std::string reverse_pair = atoms[j] + "-" + atoms[i];
            
            // Add the distance to the appropriate pair list
            pair_distances[atom_pair].push_back(norm_distance[i][j]);
            pair_distances[reverse_pair].push_back(norm_distance[i][j]);
        }
    }
    
    // Determine cutoffs from distance distributions
    std::unordered_map<std::string, float> dynamic_cutoffs;
    std::vector<std::string> not_evaluated_bonds;
    
    // For each atom pair type, determine cutoff
    for (auto& pair : pair_distances) {
        const std::string& atom_pair = pair.first;
        std::vector<float>& distances = pair.second;
        
        // Sort distances for this atom pair
        std::sort(distances.begin(), distances.end());
        
        // Skip if too few data points
        if (distances.size() < 10) {
            not_evaluated_bonds.push_back(atom_pair);
            continue;
        }
        
        // Use histogram binning to find the gap between bonded and non-bonded
        const int num_bins = 50;
        const float min_dist = distances.front();
        const float max_dist = std::min(3.0f, distances.back()); // Limit to reasonable bond distance
        const float bin_width = (max_dist - min_dist) / num_bins;
        
        std::vector<int> histogram(num_bins, 0);
        
        // Fill histogram
        for (float dist : distances) {
            if (dist <= max_dist) {
                int bin = static_cast<int>((dist - min_dist) / bin_width);
                if (bin >= 0 && bin < num_bins) {
                    histogram[bin]++;
                }
            }
        }
        
        // Find first minimum in histogram (gap between first and second peak)
        float cutoff = 0.0f;
        bool found_first_peak = false;
        bool found_valley = false;
        
        for (int i = 1; i < num_bins - 1; ++i) {
            // Check if we found the first peak already
            if (!found_first_peak && histogram[i-1] < histogram[i] && histogram[i] > histogram[i+1] && histogram[i] > histogram[i+2]) {
                found_first_peak = true;
                continue;
            }

            
            // After finding first peak, look for a valley (local minimum)
            if (found_first_peak && !found_valley && 
                histogram[i-1] > histogram[i] && histogram[i] <= histogram[i+1] && histogram[i] <= histogram[i+2]) {
                cutoff = min_dist + (i * bin_width);
                cutoff += bin_width; // Add a buffer to the cutoff
                found_valley = true;
                break;
            }
        }
        
        // If no valley found or cutoff is too large, use a reasonable default, only override H-H cutoff if the found valley is larger than 1.0
        if (atom_pair == "H-H" && cutoff > 1.0f) {
            cutoff = 1.0f;
        }
        if (!found_valley || cutoff == 0.0f || cutoff > 2.1f) {
            not_evaluated_bonds.push_back(atom_pair);
            continue;
        }
        
        dynamic_cutoffs[atom_pair] = cutoff;
    }
    
    // Build the bond graph using the dynamic cutoffs
    #pragma omp parallel for schedule(dynamic)
    for (size_t i = 0; i < num_atoms; ++i) {
        std::vector<int> neighbors;
        
        for (size_t j = i + 1; j < num_atoms; ++j) {
            std::string pair_key = atoms[i] + "-" + atoms[j];
            
            // Skip if no cutoff determined for this pair
            if (dynamic_cutoffs.find(pair_key) == dynamic_cutoffs.end()) {
                continue;
            }
            
            float cutoff = dynamic_cutoffs[pair_key];
            
            // Skip if no bond can exist
            if (cutoff <= 0.0f) continue;
            
            // Check if atoms are bonded (distance is less than cutoff)
            if (norm_distance[i][j] <= cutoff) {
                neighbors.push_back(j);
                
                // Add symmetric bond (i to j already stored in neighbors)
                #pragma omp critical
                {
                    bond_graph[j].push_back(i);
                }
            }
        }
        
        // Store all neighbors found
        #pragma omp critical
        {
            bond_graph[i].insert(bond_graph[i].end(), neighbors.begin(), neighbors.end());
        }
    }
    
    // Find connected components (molecules) using BFS traversal
    std::vector<bool> visited(num_atoms, false);
    std::vector<std::vector<int>> molecules;
    
    for (size_t i = 0; i < num_atoms; ++i) {
        if (!visited[i]) {
            std::vector<int> molecule;
            std::queue<int> queue;
            
            queue.push(i);
            visited[i] = true;
            
            while (!queue.empty()) {
                int current = queue.front();
                queue.pop();
                molecule.push_back(current);
                
                // Add all unvisited neighbors to the queue
                for (int neighbor : bond_graph[current]) {
                    if (!visited[neighbor]) {
                        queue.push(neighbor);
                        visited[neighbor] = true;
                    }
                }
            }
            
            molecules.push_back(molecule);
        }
    }
    
    // Count atoms in each molecule and create chemical formulas
    std::unordered_map<std::string, int> molecular_formulas;
    
    for (const auto& molecule : molecules) {
        // Count atoms in this molecule
        std::unordered_map<std::string, int> atom_counts;
        
        for (int atom_idx : molecule) {
            atom_counts[atoms[atom_idx]]++;
        }
        
        // Generate molecular formula string (e.g., H2O)
        std::ostringstream formula;
        std::vector<std::string> sorted_atoms;
        
        // Get unique atom types and sort them
        for (const auto& [atom_type, _] : atom_counts) {
            sorted_atoms.push_back(atom_type);
        }
        
        // Custom sorting: C first, H second, then alphabetically
        std::sort(sorted_atoms.begin(), sorted_atoms.end(), [](const std::string& a, const std::string& b) {
            if (a == "C") return true;
            if (b == "C") return false;
            if (a == "H") return true;
            if (b == "H") return false;
            return a < b;
        });
        
        // Build the formula string
        for (const auto& atom_type : sorted_atoms) {
            formula << atom_type;
            if (atom_counts[atom_type] > 1) {
                formula << atom_counts[atom_type];
            }
        }
        
        // Increment count of this molecular formula
        molecular_formulas[formula.str()]++;
    }
    
    return molecular_formulas;
}


//##################
//## RDF FUNCTION ##
//##################

// Helper Function to compute cumulative sum (similar to np.cumsum)
std::vector<float> cumulative_sum(const std::vector<float>& data) {
    std::vector<float> result(data.size());
    std::partial_sum(data.begin(), data.end(), result.begin());
    return result;
}

// Helper averaged bins function
std::vector<float> averaged_bins(const std::vector<float>& bins) {
    std::vector<float> a_bins(bins.size() - 1);
    for (size_t i = 0; i < bins.size() - 1; ++i) {
        a_bins[i] = (bins[i] + bins[i + 1]) / 2;
    }
    return a_bins;
}

// calculate the RDF
tuple <vector<float>, vector<float>, vector<float>, vector<float>> calc_rdf_core(const vector<string> coord_setup, const vector<vector<vector<float>>> coords, const vector<string> atoms, const vector<vector<float>> pbc_matrix, const vector<float> setup) {
    
    // Initialize the bins
    vector<float> bins;
 
    // Initialize the bins
    int n_bins = setup[0];
    float start_dist = setup[1];
    float end_dist = setup[2];
    
    // Calculate the bin width
    float bin_width = (end_dist - start_dist) / n_bins;

    // Create the bins vector
    for (int i = 0; i < n_bins; ++i) {
        float bin_val = start_dist + i * bin_width;
        bins.push_back(bin_val);
    }    

    // Get atom names
    string coorda_name = coord_setup[0];
    string coordb_name = coord_setup[1];

    // Get number of atoms:
    vector<vector<float>> coorda0;
    vector<vector<float>> coordb0;

    int no_a_atoms = 0;
    int no_b_atoms = 0;

    // Loop over all atoms
    for (size_t j = 0; j < coords[0].size(); ++j) {
        if (atoms[j] == coorda_name) {
            coorda0.push_back(coords[0][j]);
        }
    }
    no_a_atoms = coorda0.size();
    for (size_t j = 0; j < coords[0].size(); ++j) {
        if (atoms[j] == coordb_name) {
            coordb0.push_back(coords[0][j]);
        }
    }
    no_b_atoms = coordb0.size();

    cout << "Number of atoms in coorda: " << no_a_atoms << endl;
    cout << "Number of atoms in coordb: " << no_b_atoms << endl;


    // Calculate distance matrix in each frame and obtain a histogram each time to sum up in the end
    
    vector<float> hist(n_bins);

    vector<float> rdf(n_bins);
    vector<float> int_rdf_a(n_bins);
    vector<float> int_rdf_b(n_bins);
    
    #pragma omp parallel for schedule(dynamic)
    for (size_t i = 0; i < coords.size(); ++i) {

        // Get the coords for a and b for this step
        vector<vector<float>> coorda;
        vector<vector<float>> coordb;

        // Loop over all atoms
        for (size_t j = 0; j < coords[i].size(); ++j) {
            if (atoms[j] == coorda_name) {
                coorda.push_back(coords[i][j]);
            }
            if (atoms[j] == coordb_name) {
                coordb.push_back(coords[i][j]);
            }
        }

        // get the distance matrix n_of_coorda x n_of_coordb
        vector<vector<float>> dist_ab_frame = pbc_dist_norm(coorda, coordb, pbc_matrix);

        // flatten the 2D vector
        vector<float> dist_ab_frame_flat;
        for (size_t j = 0; j < dist_ab_frame.size(); ++j) {
            for (size_t k = 0; k < dist_ab_frame[j].size(); ++k) {
                dist_ab_frame_flat.push_back(dist_ab_frame[j][k]);
            }
        }

        // Calculate the histogram
        vector<int> hist_tmp(n_bins);

        for (size_t j = 0; j < dist_ab_frame_flat.size(); ++j) {
            int bin = (dist_ab_frame_flat[j] - start_dist) / bin_width;
            if (bin >= 0 && bin < n_bins) {
                hist_tmp[bin] += 1;
            }
        }

        //Sum up the histogram 
        for (size_t j = 0; j < hist_tmp.size(); ++j) {
            hist[j] += hist_tmp[j];
        }
    }

    // Normalize the histogram (divide by the number of frames)
    for (size_t i = 0; i < hist.size(); ++i) {
        hist[i] = hist[i] / coords.size();
    }

    // Normalize the RDF
    rdf.resize(hist.size());
    vector<float> r1(bins.begin(), bins.end() - 1);
    vector<float> r2(bins.begin() + 1, bins.end());
    vector<float> dv(r1.size());

    for (size_t i = 0; i < r1.size(); ++i) {
        dv[i] = (4.0 / 3.0) * M_PI * (pow(r2[i], 3) - pow(r1[i], 3));
    }

    // Number of atoms in the system
    int Nab = no_a_atoms * no_b_atoms; 

    // Determinant of the pbc matrix, needed because of the volume: V = det(pbc_matrix)
    float det_pbc = matrix_determinant(pbc_matrix);

    for (size_t i = 0; i < rdf.size(); ++i) {
        rdf[i] = (hist[i] / dv[i])  / (Nab) * det_pbc;
    }

    // Calculate the integral of the RDF
    float rho_a = no_a_atoms / det_pbc;
    float rho_b = no_b_atoms / det_pbc;

    // rdf times dv
    vector<float> rdf_dv(rdf.size());
    for (size_t i = 0; i < rdf.size(); ++i) {
        rdf_dv[i] = rdf[i] * dv[i];
    }

    vector<float> cumsum = cumulative_sum(rdf_dv);

    for (size_t i = 0; i < cumsum.size(); ++i) {
        int_rdf_a[i] = cumsum[i] * rho_a;
        int_rdf_b[i] = cumsum[i] * rho_b;
    }

    vector<float> bins_out(n_bins-1);
    vector<float> hist_out(n_bins-1);
    vector<float> rdf_out(n_bins-1);
    vector<float> int_rdf_a_out(n_bins-1);
    vector<float> int_rdf_b_out(n_bins-1);

    for (size_t i = 0; i < bins_out.size(); ++i) {
        bins_out[i] = bins[i];
        hist_out[i] = hist[i];
        rdf_out[i] = rdf[i];
        int_rdf_a_out[i] = int_rdf_a[i];
        int_rdf_b_out[i] = int_rdf_b[i];
    }

    return std::make_tuple(bins_out, rdf_out, int_rdf_a_out, int_rdf_b_out);
}   

// Function to generate the filename based on the atom types
std::string generate_rdf_filename(const std::vector<std::string>& atom_types) {
    std::stringstream filename;
    filename << "rdf_";
    for (size_t i = 0; i < atom_types.size(); ++i) {
        filename << atom_types[i];
    }
    filename << ".csv";
    return filename.str();
}

// Wrapper function for calc_rdf_core that calls it and saves the RDF data to a CSV file
void save_rdf_data(const std::vector<std::string>& atom_types,
    const std::vector<std::vector<std::vector<float>>>& coords,
    const std::vector<string>& atoms,
    const vector<vector<float>>& pbc_matrix,
    const std::vector<float>& setup2) {

    // Call calc_rdf_core with the same arguments passed to this function
    std::tuple<std::vector<float>, std::vector<float>, std::vector<float>, std::vector<float>> rdf_output = 
    calc_rdf_core(atom_types, coords, atoms, pbc_matrix, setup2);

    // Generate the output filename based on the atom types
    std::string output_filename = generate_rdf_filename(atom_types);

    // Open the output file for writing the RDF data
    std::ofstream output_file(output_filename);

    if (output_file.is_open()) {
        // Write the header to the CSV file
        output_file << "#r [A], rdf, int_rdf_a, int_rdf_b" << std::endl;

        // Get the vectors from the tuple
        const auto& bins = std::get<0>(rdf_output);
        const auto& rdf = std::get<1>(rdf_output);
        const auto& int_rdf_a = std::get<2>(rdf_output);
        const auto& int_rdf_b = std::get<3>(rdf_output);

        // Loop through the data and write each line to the file
        for (size_t i = 0; i < bins.size(); ++i) {
        output_file << bins[i] << ", " << rdf[i] << ", " 
                << int_rdf_a[i] << ", " << int_rdf_b[i] << std::endl;
        }

        // Close the file after writing
        output_file.close();
        std::cout << "Data saved to " << output_filename << std::endl;

    } else {
    // Handle error if the file cannot be opened
    std::cerr << "Error: Unable to open file for writing!" << std::endl;
    }
}


//##################
//## MSD FUNCTION ##
//##################

// Helper function: unwrap trajectory
vector<vector<vector<float>>> unwrap_trajectory(vector<vector<vector<float>>>& trajectory, const vector<vector<float>>& pbc_matrix) {
    // Calculate the number of time steps and atoms
    size_t time_steps = trajectory.size();
    size_t num_atoms = trajectory[0].size();
    size_t dimensions = trajectory[0][0].size();

    // Check for (non)-orthogonal PBC
    bool is_ortho_pbc = is_ortho(pbc_matrix);

    // Initialize wrap_matrix to store cumulative wrapping information
    vector<vector<vector<int>>> wrap_matrix(time_steps - 1, vector<vector<int>>(num_atoms, vector<int>(dimensions, 0)));

    if (is_ortho_pbc) {
        // Use the orthogonal method (no relative coordinates, faster)

        vector<float> pbc_ortho(3);
        for (int i = 0; i < 3; ++i) {
            pbc_ortho[i] = pbc_matrix[i][i];
        }


        // Compute differences between consecutive time steps (dist1)
        for (size_t t = 1; t < time_steps; ++t) {
            for (size_t atom = 0; atom < num_atoms; ++atom) {
                for (size_t dim = 0; dim < dimensions; ++dim) {
                    float dist = trajectory[t][atom][dim] - trajectory[t - 1][atom][dim];
                    if (dist > pbc_ortho[dim] / 2.0f) {
                        wrap_matrix[t - 1][atom][dim] = 1; // Wrap in the positive direction
                    } else if (dist < -pbc_ortho[dim] / 2.0f) {
                        wrap_matrix[t - 1][atom][dim] = -1; // Wrap in the negative direction
                    }
                }
            }
        }

        // Compute cumulative wrapping information
        for (size_t t = 1; t < time_steps - 1; ++t) {
            for (size_t atom = 0; atom < num_atoms; ++atom) {
                for (size_t dim = 0; dim < dimensions; ++dim) {
                    wrap_matrix[t][atom][dim] += wrap_matrix[t - 1][atom][dim];
                }
            }
        }

        // Adjust the trajectory by subtracting the wrapping offsets
        for (size_t t = 1; t < time_steps; ++t) {
            for (size_t atom = 0; atom < num_atoms; ++atom) {
                for (size_t dim = 0; dim < dimensions; ++dim) {
                    trajectory[t][atom][dim] -= wrap_matrix[t - 1][atom][dim] * pbc_ortho[dim];
                }
            }
        }

        return trajectory;

    }
    else { // Use the non-orthogonal method (relative coordinates)

        // Calculate the inverse of the PBC matrix for transformations to fractional coordinates
        vector<vector<float>> inv_pbc = matrix_inverse(pbc_matrix);

        // Convert all trajectory points to fractional coordinates
        vector<vector<vector<float>>> frac_trajectory(time_steps, vector<vector<float>>(num_atoms, vector<float>(dimensions, 0.0f)));
        for (size_t t = 0; t < time_steps; ++t) {
            for (size_t atom = 0; atom < num_atoms; ++atom) {
                frac_trajectory[t][atom] = matrix_vector_multiply(inv_pbc, trajectory[t][atom]);
            }
        }

        // Compute differences between consecutive time steps in fractional space
        for (size_t t = 1; t < time_steps; ++t) {
            for (size_t atom = 0; atom < num_atoms; ++atom) {
                for (size_t dim = 0; dim < dimensions; ++dim) {
                    float dist = frac_trajectory[t][atom][dim] - frac_trajectory[t-1][atom][dim];
                    if (dist > 0.5f) {
                        wrap_matrix[t-1][atom][dim] = 1; // Wrap in the positive direction
                    } else if (dist < -0.5f) {
                        wrap_matrix[t-1][atom][dim] = -1; // Wrap in the negative direction
                    }
                }
            }
        }

        // Compute cumulative wrapping information
        for (size_t t = 1; t < time_steps - 1; ++t) {
            for (size_t atom = 0; atom < num_atoms; ++atom) {
                for (size_t dim = 0; dim < dimensions; ++dim) {
                    wrap_matrix[t][atom][dim] += wrap_matrix[t-1][atom][dim];
                }
            }
        }

        // Create new unwrapped trajectory by adjusting the fractional coordinates and converting back to real space
        vector<vector<vector<float>>> unwrapped_trajectory = trajectory; // Make a copy
        
        for (size_t t = 1; t < time_steps; ++t) {
            for (size_t atom = 0; atom < num_atoms; ++atom) {
                // Adjust the fractional coordinates by subtracting the wrapping offsets
                vector<float> adjusted_frac = frac_trajectory[t][atom];
                for (size_t dim = 0; dim < dimensions; ++dim) {
                    adjusted_frac[dim] -= wrap_matrix[t-1][atom][dim];
                }
                
                // Transform back to real space
                unwrapped_trajectory[t][atom] = matrix_vector_multiply(pbc_matrix, adjusted_frac);
            }
        }

        return unwrapped_trajectory;
    }

}

// Helper Data: atom mass dictionary
std::unordered_map<std::string, float> atom_mass_dict = {
    {"H", 1.008f},
    {"O", 15.999f},
    {"C", 12.011f},
    {"N", 14.007f},
    {"S", 32.06f},
    {"F", 18.998f},
    {"Cl", 35.453f},
    {"Br", 79.904f},
    {"I", 126.904f},
    {"P", 30.974f},
    {"Na", 22.989f},
    {"K", 39.098f},
    {"Mg", 24.305f},
    {"Ca", 40.078f},
    {"Fe", 55.845f},
    {"Zn", 65.38f},
    {"Cu", 63.546f},
    {"Ag", 107.868f},
    {"Au", 196.967f},
    {"Pt", 195.084f},
    {"Pd", 106.42f},
    {"Ni", 58.693f},
    {"Co", 58.933f},
    {"Mn", 54.938f},
    {"Cr", 51.996f},
    {"V", 50.942f},
    {"Ti", 47.867f},
    {"Sc", 44.956f},
    {"Ca", 40.078f},
    {"K", 39.098f},
    {"Na", 22.989f},
    {"Mg", 24.305f},
    {"Li", 6.941f},
    {"Be", 9.012f},
    {"B", 10.81f},
    {"Al", 26.982f},
    {"Si", 28.086f},
    {"As", 74.922f},
    {"Se", 78.971f},
    {"Te", 127.6f},
    {"He", 4.0026f},
    {"Ne", 20.180f},
    {"Ar", 39.948f},
    {"Kr", 83.798f},
    {"Xe", 131.293f},
    {"Rn", 222.018f},
    {"Ra", 226.025f},
    {"Fr", 223.020f},
    {"At", 210.000f},
    {"Po", 209.000f},
    {"Bi", 208.980f},
    {"Pb", 207.200f},
    {"Tl", 204.383f},
    {"Hg", 200.590f},
    {"Cd", 112.411f},
    {"In", 114.818f},
    {"Sn", 118.710f},
    {"Sb", 121.760f},
    {"W", 183.840f},
    {"Ta", 180.948f},
    {"Hf", 178.490f},
    {"Lu", 174.967f},
    {"Yb", 173.045f},
    {"Tm", 168.934f},
    {"Er", 167.259f},
    {"Ho", 164.930f},
    {"Dy", 162.500f},
    {"Tb", 158.925f},
    {"Gd", 157.250f},
    {"Eu", 151.964f},
    {"Sm", 150.360f},
    {"Pm", 145.000f},
    {"Nd", 144.240f},
    {"Pr", 140.908f},
    {"Ce", 140.116f},
    {"La", 138.905f},
    {"Ba", 137.327f},
    {"Cs", 132.905f},
    {"Rb", 85.468f},
    {"Sr", 87.620f}
};

// Helper function: calculate the center of mass 
vector<vector<float>> get_com(const vector<vector<vector<float>>> coord, const vector<string> atoms) {
    size_t num_atoms = atoms.size();
    size_t num_frames = coord.size();
    vector<float> mass_list(num_atoms, 0.0);

    // Get the mass of each atom
    for (size_t i = 0; i < num_atoms; ++i) {
        mass_list[i] = atom_mass_dict[atoms[i]];
        if (mass_list[i] == 0.0f) {
            std::cerr << "Error: Unknown atom type: " << atoms[i] << std::endl;
            return {};
        }
    }

    float total_mass = std::accumulate(mass_list.begin(), mass_list.end(), 0.0f);

    vector<float> mass_weights(num_atoms);
    for (size_t i = 0; i < num_atoms; ++i) {
        mass_weights[i] = mass_list[i] / total_mass;
    }

    // Calculate the center of mass
    vector<vector<float>> com(num_frames, vector<float>(3, 0.0f));
    for (size_t frame = 0; frame < num_frames; ++frame) {
        for (size_t atom = 0; atom < num_atoms; ++atom) {
            for (size_t dim = 0; dim < 3; ++dim) {
                com[frame][dim] += coord[frame][atom][dim] * mass_weights[atom];
            }
        }
    }
    return com;
}

// Helper function: remove the center of mass motion
vector<vector<vector<float>>> remove_com_motion(vector<vector<vector<float>>>& trajectory, const vector<string>& atoms, bool zero = true) {
    // Calculate the number of time steps and atoms
    size_t time_steps = trajectory.size();
    size_t num_atoms = trajectory[0].size();
    size_t dimensions = trajectory[0][0].size();

    // Calculate the center of mass for each time step
    vector<vector<float>> com = get_com(trajectory, atoms);

    // Set initial COM based on `zero` flag
    vector<float> com_init(3, 0.0f);
    if (!zero) {
        com_init = com[0]; // Keep initial COM
    }

    // Remove the center of mass motion
    for (size_t t = 0; t < time_steps; ++t) {
        for (size_t atom = 0; atom < num_atoms; ++atom) {
            for (size_t dim = 0; dim < dimensions; ++dim) {
                trajectory[t][atom][dim] -= com[t][dim];
                trajectory[t][atom][dim] += com_init[dim]; // Add back initial COM if needed
            }
        }
    }
    return trajectory;
}


// Function to calculate the mean square displacement (MSD) for a given atom type
std::tuple<std::vector<float>, std::vector<float>> msd_for_unwrap(
    const vector<vector<vector<float>>> &coords,     // 3D vector for coordinates
    const vector<string> &atoms,                      // Vector of atom types
    const string &atom_type,                          // Atom type to filter
    const float timestep_md,                        // MD timestep
    const int tau_steps,                            // Step size for tau
    const int verbosity = 25000,                        // Verbosity level
    const int max_length = 10000000 // Maximum length (optional)
) {
    vector<float> msd;
    vector<float> tau;

    // Set atom type 
    string coorda_name = atom_type;

    // Extract the coords of the specific atom type
    vector<vector<vector<float>>> coorda;
    
    vector<int> relevant_indices;
    for (size_t j = 0; j < atoms.size(); ++j) {
        if (atoms[j] == coorda_name) {
            relevant_indices.push_back(j);
        }
    }
    for (const auto &frame : coords) {                                                
        vector<vector<float>> coorda_timestep;
        for (size_t j = 0; j < relevant_indices.size(); ++j) {
            coorda_timestep.push_back(frame[relevant_indices[j]]);
        }
        coorda.push_back(coorda_timestep);
    }

    // Ensure coorda is not empty before proceeding
    if (coorda.empty() || coorda[0].empty() || coorda[0][0].size() < 3) {
        std::cerr << "Error: coorda is empty or does not have proper structure (3D coordinates missing)." << std::endl;
        return {tau, msd}; // Return default results to avoid crash
    }

    // Determine the limit
    int limit = std::min(max_length, static_cast<int>(coorda.size()/2));

    int num_steps = limit / tau_steps;  // Number of iterations for i
    msd.resize(num_steps, 0.0f);  // Preallocate with zero
    tau.resize(num_steps, 0.0f);  // Preallocate with zero

    // Main loop for MSD calculation
    #pragma omp parallel for schedule(dynamic)
    for (int step = 0; step < num_steps; ++step) {   
        int i = step * tau_steps;
        tau[step] = i * timestep_md;

        if (i % verbosity == 0) {
            std::cerr << "Processing step: " << i << std::endl;
        }

        // Calculate displacement squared
        float total_displacement = 0.0f;
        int total_windows = 0;

        #pragma omp parallel for reduction(+:total_displacement, total_windows)
        for (size_t frame_idx = 0; frame_idx < coorda.size() - i; ++frame_idx) {        
            if (coorda[frame_idx].empty() || coorda[frame_idx + i].empty()) continue;

            float squared_displacement_summed_in_this_window = 0.0f;
            int atom_count = 0;

            for (size_t atom_idx = 0; atom_idx < coorda[frame_idx].size(); ++atom_idx) {                
                if (atom_idx >= coorda[frame_idx + i].size()) continue;
                if (coorda[frame_idx][atom_idx].size() < 3 || coorda[frame_idx + i][atom_idx].size() < 3) continue;

                float dx = coorda[frame_idx + i][atom_idx][0] - coorda[frame_idx][atom_idx][0];
                float dy = coorda[frame_idx + i][atom_idx][1] - coorda[frame_idx][atom_idx][1];
                float dz = coorda[frame_idx + i][atom_idx][2] - coorda[frame_idx][atom_idx][2];

                squared_displacement_summed_in_this_window += dx * dx + dy * dy + dz * dz;
                atom_count++;
            }

            if (atom_count > 0) {
                total_displacement += squared_displacement_summed_in_this_window / atom_count;
                total_windows++;
            }
            else {
                cout << "Warning: No atoms found in MSD Calculation!" << endl;
            }
        }

        // Compute final MSD value correctly
        msd[step] = (total_windows > 0) ? total_displacement / total_windows : 0.0f;
    }

    return {tau, msd};
}

// Function to generate the filename based on the atom type
std::string generate_msd_filename(const std::string& atom_type) {
    return "msd_" + atom_type + ".csv";
}

// Wrapper function for msd_for_unwrap that calls it and saves the MSD data to a CSV file
void save_msd_data(const std::vector<std::vector<std::vector<float>>>& unwrapped_coords,
                   const std::vector<string>& atoms,
                   const std::string& atom_type,
                   float timestep_md,
                   int tau_steps_dyn) {

    // Call msd_for_unwrap with the same arguments passed to this function
    std::tuple<std::vector<float>, std::vector<float>> msd_output = 
        msd_for_unwrap(unwrapped_coords, atoms, atom_type, timestep_md / 1000, tau_steps_dyn);

    // Generate the output filename based on the atom type
    std::string output_filename = generate_msd_filename(atom_type);

    // Open the output file for writing the MSD data
    std::ofstream output_file(output_filename);

    if (output_file.is_open()) {
        // Write the header to the CSV file
        output_file << "#tau [ps], msd [A**2]" << std::endl;

        // Get the vectors from the tuple
        const auto& tau = std::get<0>(msd_output);
        const auto& msd = std::get<1>(msd_output);

        // Loop through the data and write each line to the file
        for (size_t i = 0; i < tau.size(); ++i) {
            output_file << tau[i] << ", " << msd[i] << std::endl;
        }

        // Close the file after writing
        output_file.close();
        std::cout << "Data saved to " << output_filename << std::endl;
    } else {
        // Handle error if the file cannot be opened
        std::cerr << "Error: Unable to open file for writing!" << std::endl;
    }
}

//###################
//## sMSD FUNCTION ##
//###################

// Function to calculate the single atom mean square displacement (sMSD) for a given atom type
std::tuple<std::vector<float>, std::vector<std::vector<float>>> smsd_for_unwrap(
    const vector<vector<vector<float>>> &coords,     // 3D vector for coordinates
    const vector<string> &atoms,                      // Vector of atom types
    const string &atom_type,                          // Atom type to filter
    const float timestep_md,                        // MD timestep
    const int tau_steps,                            // Step size for tau
    const int verbosity = 25000,                        // Verbosity level
    const int max_length = 10000000 // Maximum length (optional)
) {
    vector<vector<float>> msd;
    vector<float> tau;

    // Set atom type 
    string coorda_name = atom_type;

    // Extract the coords of the specific atom type
    vector<vector<vector<float>>> coorda;
    
    vector<int> relevant_indices;
    for (size_t j = 0; j < atoms.size(); ++j) {
        if (atoms[j] == coorda_name) {
            relevant_indices.push_back(j);
        }
    }
    for (const auto &frame : coords) {                                                
        vector<vector<float>> coorda_timestep;
        for (size_t j = 0; j < relevant_indices.size(); ++j) {
            coorda_timestep.push_back(frame[relevant_indices[j]]);
        }
        coorda.push_back(coorda_timestep);
    }


    // Ensure coorda is not empty before proceeding
    if (coorda.empty() || coorda[0].empty() || coorda[0][0].size() < 3) {
        std::cerr << "Error: coorda is empty or does not have proper structure (3D coordinates missing)." << std::endl;
        return {tau, msd}; // Return default results to avoid crash
    }

    // Determine the limit
    int limit = std::min(max_length, static_cast<int>(coorda.size()/2));
    size_t num_atoms = coorda[0].size();

    int num_steps = limit / tau_steps;  // Number of iterations for i
    msd.resize(num_steps, std::vector<float>(num_atoms, 0.0f));  // Preallocate with zero
    tau.resize(num_steps, 0.0f);  // Preallocate with zero

    // Main loop for MSD calculation
    #pragma omp parallel for schedule(dynamic)
    for (int step = 0; step < num_steps; ++step) {   
        int i = step * tau_steps;
        tau[step] = i * timestep_md;

        if (i % verbosity == 0) {
            std::cerr << "Processing step: " << i << std::endl;
        }

        // Calculate displacement squared
        vector<float> total_displacement = vector<float>(num_atoms, 0.0f);
        int total_windows = 0;

        // Parallelize the inner loop for frame_idx calculation
        #pragma omp parallel
        {
            // Each thread will have a local vector for displacement and window count
            vector<float> local_displacement(num_atoms, 0.0f);
            int local_windows = 0;

            #pragma omp for nowait
            for (size_t frame_idx = 0; frame_idx < coorda.size() - i; ++frame_idx) {        
                if (coorda[frame_idx].empty() || coorda[frame_idx + i].empty()) continue;

                vector<float> squared_displacement_summed_in_this_window(num_atoms, 0.0f);

                // Iterate through atoms and calculate displacement squared
                for (size_t atom_idx = 0; atom_idx < coorda[frame_idx].size(); ++atom_idx) {                
                    if (atom_idx >= coorda[frame_idx + i].size()) continue;
                    if (coorda[frame_idx][atom_idx].size() < 3 || coorda[frame_idx + i][atom_idx].size() < 3) continue;

                    float dx = coorda[frame_idx + i][atom_idx][0] - coorda[frame_idx][atom_idx][0];
                    float dy = coorda[frame_idx + i][atom_idx][1] - coorda[frame_idx][atom_idx][1];
                    float dz = coorda[frame_idx + i][atom_idx][2] - coorda[frame_idx][atom_idx][2];

                    squared_displacement_summed_in_this_window[atom_idx] = dx * dx + dy * dy + dz * dz;
                }
                if (squared_displacement_summed_in_this_window.size() > 0) {
                    for (size_t atom_idx = 0; atom_idx < num_atoms; ++atom_idx) {
                        local_displacement[atom_idx] += squared_displacement_summed_in_this_window[atom_idx];
                    }
                    local_windows++;
                }
                else {
                    cout << "Warning: No atoms found in MSD Calculation!" << endl;
                }
            }

            // Critical section to safely merge the local results into the global total_displacement
            #pragma omp critical
            {
                for (size_t atom_idx = 0; atom_idx < num_atoms; ++atom_idx) {
                    total_displacement[atom_idx] += local_displacement[atom_idx];
                }
                total_windows += local_windows;
            }
        }

        // Compute final MSD value correctly
        msd[step].resize(num_atoms);
        for (size_t atom_idx = 0; atom_idx < num_atoms; ++atom_idx) {
            msd[step][atom_idx] = (total_windows > 0) ? total_displacement[atom_idx] / total_windows : 0.0f;
        }
    }

    return {tau, msd};
}

// Function to generate the filename based on the atom type
std::string generate_msd_filename(const std::string& atom_type, const int & i) {
    std::stringstream filename;
    filename << "smsd_" << atom_type << "_" << i << ".csv";
    return filename.str();
}

// Wrapper function for msd_for_unwrap that calls it and saves the MSD data to a CSV file
void save_smsd_data(const std::vector<std::vector<std::vector<float>>>& unwrapped_coords,
                   const std::vector<string>& atoms,
                   const std::string& atom_type,
                   float timestep_md,
                   int tau_steps_dyn) {

    // Call msd_for_unwrap with the same arguments passed to this function
    std::tuple<std::vector<float>, std::vector<std::vector<float>>> smsd_output = 
        smsd_for_unwrap(unwrapped_coords, atoms, atom_type, timestep_md / 1000, tau_steps_dyn);

    // Get number of atoms
    int num_atoms = std::get<1>(smsd_output)[0].size();

    // Write output to multiple files: as many as the number of atoms
    for (int i = 0; i < num_atoms; ++i) {
        // Generate the output filename based on the atom type and index
        std::string output_filename = generate_msd_filename(atom_type, i);

        // Open the output file for writing the MSD data
        std::ofstream output_file(output_filename);

        if (output_file.is_open()) {
            // Write the header to the CSV file
            output_file << "#tau [ps], msd [A**2]" << std::endl;

            // Get the vectors from the tuple
            const auto& tau = std::get<0>(smsd_output);
            const auto& msd = std::get<1>(smsd_output);

            // Loop through the data and write each line to the file
            for (size_t j = 0; j < tau.size(); ++j) {
                output_file << tau[j] << ", " << msd[j][i] << std::endl;
            }

            // Close the file after writing
            output_file.close();
            //std::cout << "Data saved to " << output_filename << std::endl;
        } else {
            // Handle error if the file cannot be opened
            std::cerr << "Error: Unable to open file for writing!" << std::endl;
        }
    }
    
    int num_steps = std::get<0>(smsd_output).size();
    // Get mean of the single atom MSD (= normal MSD)
    std::vector<float> mean_msd (num_steps, 0.0f);
    // Loop through the atoms and calculate mean MSD
    for (int i = 0; i < num_steps; ++i) {
        float sum_msd = 0.0f;
        for (int j = 0; j < num_atoms; ++j) {
            sum_msd += std::get<1>(smsd_output)[i][j];
        }
        mean_msd[i] = sum_msd / num_atoms;
    }

    // Write mean MSD to a file
    std::string mean_output_filename = "mean_msd_" + atom_type + ".csv";
    std::ofstream mean_output_file(mean_output_filename);
    if (mean_output_file.is_open()) {
        // Write the header to the CSV file
        mean_output_file << "#tau [ps], msd [A**2]" << std::endl;

        // Get the vectors from the tuple
        const auto& tau = std::get<0>(smsd_output);

        // Loop through the data and write each line to the file
        for (size_t j = 0; j < tau.size(); ++j) {
            mean_output_file << tau[j] << ", " << mean_msd[j] << std::endl;
        }

        // Close the file after writing
        mean_output_file.close();
        //std::cout << "Data saved to " << mean_output_filename << std::endl;
    } else {
        // Handle error if the file cannot be opened
        std::cerr << "Error: Unable to open file for writing!" << std::endl;
    }
}


//##################################
//## X-Y AUTOCORRELATION FUNCTION ##
//##################################

// Calculate vector autocorrelation
std::tuple<std::vector<float>, std::vector<float>, std::vector<std::vector<float>>> vector_autocorr(
    std::vector<std::vector<std::vector<float>>>& vector_arr, 
    float timestep_md,
    int tau_steps, 
    int verbosity,
    int max_length = -1) {
    
    size_t num_frames = vector_arr.size();
    size_t num_atoms = vector_arr[0].size();
    
    // Normalize vectors
    #pragma omp parallel for collapse(2)
    for (size_t t = 0; t < num_frames; ++t) {
        for (size_t i = 0; i < num_atoms; ++i) {
            // Calculate norm of vector
            float norm = std::sqrt(
                vector_arr[t][i][0] * vector_arr[t][i][0] +
                vector_arr[t][i][1] * vector_arr[t][i][1] +
                vector_arr[t][i][2] * vector_arr[t][i][2]
            );
            
            // Normalize vector
            if (norm > 1e-10f) {
                vector_arr[t][i][0] /= norm;
                vector_arr[t][i][1] /= norm;
                vector_arr[t][i][2] /= norm;
            }
        }
    }
    
    // Set limit
    size_t limit = (max_length > 0) ? 
        std::min(static_cast<size_t>(max_length), num_frames) : num_frames;
    
    // Calculate number of time points
    size_t num_points = (limit + tau_steps - 1) / tau_steps;
    
    // Prepare output arrays
    std::vector<float> tau(num_points);
    std::vector<float> auto_corr(num_points);
    std::vector<std::vector<float>> auto_single(num_points, std::vector<float>(num_atoms));
    
    // Main autocorrelation calculation loop
    #pragma omp parallel for schedule(dynamic)
    for (size_t step = 0; step < num_points; ++step) {
        int i = step * tau_steps;
        if (i >= limit) continue;
        
        if (i % verbosity == 0) {
            std::cout << "Processing lag time: " << i << std::endl;
        }
        
        // Calculate dot products (equivalent to einsum operation)
        std::vector<float> sp_arr(num_atoms, 0.0f);
        
        if (i == 0) {
            // At lag 0, dot product of normalized vector with itself is 1
            for (size_t a = 0; a < num_atoms; ++a) {
                sp_arr[a] = 1.0f;
            }
        } else {
            for (size_t a = 0; a < num_atoms; ++a) {
                float dot_sum = 0.0f;
                int count = 0;
                
                for (size_t t = 0; t < num_frames - i; ++t) {
                    float dot = 
                        vector_arr[t+i][a][0] * vector_arr[t][a][0] +
                        vector_arr[t+i][a][1] * vector_arr[t][a][1] +
                        vector_arr[t+i][a][2] * vector_arr[t][a][2];
                    
                    dot_sum += dot;
                    count++;
                }
                
                sp_arr[a] = count > 0 ? dot_sum / count : 0.0f;
            }
        }
        
        // Calculate mean across atoms
        float mean_corr = 0.0f;
        for (size_t a = 0; a < num_atoms; ++a) {
            mean_corr += sp_arr[a];
        }
        mean_corr /= num_atoms;
        
        // Store results
        tau[step] = i * timestep_md;
        auto_corr[step] = mean_corr;
        auto_single[step] = sp_arr;
    }
    
    return std::make_tuple(tau, auto_corr, auto_single);
}

// Calculate autocorrelation between different atom types
std::tuple<std::vector<float>, std::vector<float>, std::vector<std::vector<float>>> calc_autocorr_xy(
    const std::vector<std::vector<std::vector<float>>>& trajectory,
    const std::vector<std::string>& atoms, 
    const std::string& atom_type1, 
    const std::string& atom_type2, 
    const std::vector<std::vector<float>>& pbc_mat,
    float timestep_md,
    int tau_steps, 
    int verbosity = 1,
    int max_length = -1) {
    
    // Extract coordinates for atoms of type1 and type2
    std::vector<int> indices1, indices2;
    
    // Find indices of each atom type
    for (size_t i = 0; i < atoms.size(); ++i) {
        if (atoms[i] == atom_type1) {
            indices1.push_back(i);
        }
        if (atoms[i] == atom_type2) {
            indices2.push_back(i);
        }
    }
    
    // Exit if no atoms found
    if (indices1.empty() || indices2.empty()) {
        std::cerr << "No atoms found of specified types" << std::endl;
        return std::make_tuple(std::vector<float>(), std::vector<float>(), std::vector<std::vector<float>>());
    }
    
    // Extract coordinates for the first frame
    std::vector<std::vector<float>> coord1_frame0(indices1.size());
    std::vector<std::vector<float>> coord2_frame0(indices2.size());
    
    for (size_t i = 0; i < indices1.size(); ++i) {
        coord1_frame0[i] = trajectory[0][indices1[i]];
    }
    
    for (size_t i = 0; i < indices2.size(); ++i) {
        coord2_frame0[i] = trajectory[0][indices2[i]];
    }
    
    // Find nearest neighbors
    auto [ind_list, min_dist] = next_neighbor(coord1_frame0, coord2_frame0, pbc_mat);
    
    // Create vector_arr as the difference between coord1 and nearest neighbors in coord2
    std::vector<std::vector<std::vector<float>>> vector_arr(trajectory.size(), 
        std::vector<std::vector<float>>(indices1.size(), std::vector<float>(3, 0.0f)));
    
    for (size_t t = 0; t < trajectory.size(); ++t) {
        for (size_t i = 0; i < indices1.size(); ++i) {
            // Get coordinates of atom i of type1 at frame t
            const auto& pos1 = trajectory[t][indices1[i]];
            
            // Get coordinates of nearest neighbor in type2
            int neigh_idx = indices2[ind_list[i]];
            const auto& pos2 = trajectory[t][neigh_idx];
            
            // Create minimum distance vector between the atoms using PBC
            std::vector<std::vector<float>> single_pos1 = {pos1};
            std::vector<std::vector<float>> single_pos2 = {pos2};
            
            // For orthogonal PBC, can directly calculate the vector
            if (is_ortho(pbc_mat)) {
                for (int d = 0; d < 3; ++d) {
                    vector_arr[t][i][d] = pos1[d] - pos2[d];
                    vector_arr[t][i][d] -= pbc_mat[d][d] * std::round(vector_arr[t][i][d] / pbc_mat[d][d]);
                }
            } 
            // For non-orthogonal, need to transform to fractional coordinates
            else {
                // Calculate the inverse of the PBC matrix
                std::vector<std::vector<float>> inv_pbc = matrix_inverse(pbc_mat);
                
                // Transform to fractional coordinates
                std::vector<float> frac1 = matrix_vector_multiply(inv_pbc, pos1);
                std::vector<float> frac2 = matrix_vector_multiply(inv_pbc, pos2);
                
                // Calculate minimum image in fractional coords
                std::vector<float> frac_diff(3);
                for (int d = 0; d < 3; ++d) {
                    frac_diff[d] = frac1[d] - frac2[d];
                    frac_diff[d] -= std::round(frac_diff[d]);
                }
                
                // Transform back to real space
                vector_arr[t][i] = matrix_vector_multiply(pbc_mat, frac_diff);
            }
        }
    }
    
    // Call vector_autocorr with the calculated vectors
    return vector_autocorr(vector_arr, timestep_md, tau_steps, verbosity, max_length);
}

// Wrapper function to save autocorrelation data to file
void save_autocorr_data(
    const std::vector<std::vector<std::vector<float>>>& trajectory,
    const std::vector<std::string>& atoms,
    const std::vector<std::vector<float>>& pbc_mat,
    const std::string& atom_type1,
    const std::string& atom_type2,
    float timestep_md,
    int tau_steps,
    int max_length = -1,
    int verbosity = 100) {
    
    std::cout << "Computing " << atom_type1 << "-" << atom_type2 << " vector autocorrelation..." << std::endl;
    
    auto [tau, auto_corr, auto_single] = calc_autocorr_xy(
        trajectory, atoms, atom_type1, atom_type2, 
        pbc_mat, timestep_md/1000, tau_steps*10, verbosity, max_length);
    
    // Generate the output filename
    std::string output_filename = "autocorr_" + atom_type1 + atom_type2 + ".csv";
    
    // Save autocorrelation results to file
    std::ofstream outfile(output_filename);
    if (outfile.is_open()) {
        outfile << "#tau [ps], autocorrelation" << std::endl;
        for (size_t i = 0; i < tau.size(); ++i) {
            outfile << tau[i] << ", " << auto_corr[i] << std::endl;
        }
        outfile.close();
        std::cout << "Autocorrelation data saved to " << output_filename << std::endl;
    } else {
        std::cerr << "Error: Unable to open file for writing!" << std::endl;
    }
}

//##################################
//## COMPUTE FUNCTION FROM PYTHON ##
//##################################

// Function which gets called from pybind11: Python gives coord_filename, pbc_filename, rdf_pairs, msd_atoms, smsd_atoms, autocorr_pairs
void compute_analysis(
    const std::string& coord_filename,
    const std::string& pbc_filename,
    const float& timestep_md,
    // RDF pairs
    const std::vector<std::vector<std::string>>& rdf_pairs,
    // MSD atoms
    const std::vector<std::string>& msd_atoms,
    // sMSD atoms
    const std::vector<std::string>& smsd_atoms,
    // Autocorrelation pairs
    const std::vector<std::vector<std::string>>& autocorr_pairs)
{
    // Set the number of threads for OpenMP
    int no_cpus = 16; // Default number of CPUs
    omp_set_num_threads(no_cpus);  // Set number of threads

    // Print the analysis plan: DEBUGGER
    std::cout << "Planned analysis:" << "\n";
    if (rdf_pairs.empty()) {
        std::cout << "No RDF pairs provided." << "\n";
    } else {
        std::cout << "RDF pairs: ";
        for (const auto& pair : rdf_pairs) {
            std::cout << pair[0] << "-" << pair[1] << " ";
        }
        std::cout << "\n";
    }
    if (msd_atoms.empty()) {
        std::cout << "No MSD atoms provided." << "\n";
    } else {
        std::cout << "MSD atoms: ";
        for (const auto& atom : msd_atoms) {
            std::cout << atom << " ";
        }
        std::cout << "\n";
    }
    if (smsd_atoms.empty()) {
        std::cout << "No single MSD atoms provided." << "\n";
    } else {
        std::cout << "Single MSD atoms: ";
        for (const auto& atom : smsd_atoms) {
            std::cout << atom << " ";
        }
        std::cout << "\n";
    }
    if (autocorr_pairs.empty()) {
        std::cout << "No autocorrelation pairs provided." << "\n";
    } else {
        std::cout << "Autocorrelation pairs: ";
        for (const auto& pair : autocorr_pairs) {
            std::cout << pair[0] << "-" << pair[1] << " ";
        }
        std::cout << "\n";
    }

    // Read the coordinates and PBC data
    cout << "Reading trajectory and PBC data..." << endl;
    auto start_time = std::chrono::high_resolution_clock::now();
    auto array_pair = read_xyz(coord_filename);
    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed_seconds = end_time - start_time;
    std::cout << "Time taken to read trajectory: " << elapsed_seconds.count() << " s." << std::endl;
    auto coords = array_pair.first;
    auto atoms = array_pair.second;
    auto pbc = read_pbc(pbc_filename);

    // Do com removal and unwrap
    vector<vector<vector<float>>> unwrapped_coords = remove_com_motion(coords, atoms);
    unwrapped_coords = unwrap_trajectory(unwrapped_coords, pbc);

    // Loop over RDF pairs and calculate the RDF
    for (const auto& atom_pair : rdf_pairs) {
        // Check if in atom_pair is H
        if (atom_pair[0] == "H" || atom_pair[1] == "H") {
            // Call the function with setup for short range
            save_rdf_data(atom_pair, coords, atoms, pbc, {100, 0.5, 4.5});
        }
        else {
            // Call the function with setup for long range
            save_rdf_data(atom_pair, coords, atoms, pbc, {125, 2.0, 7.0});
        }
    }

    // Set the tau_steps for MSD, sMSD and autocorrelation
    int tau_steps_dyn = 1; // Default value
    if (timestep_md <= 50) {
        tau_steps_dyn = static_cast<int>(50.0 / timestep_md);
    }
    else if (timestep_md > 50) {
        tau_steps_dyn = 1;
    }

    // Loop over MSD atoms and calculate the MSD
    for (const auto& atom : msd_atoms) {
        save_msd_data(unwrapped_coords, atoms, atom, timestep_md, tau_steps_dyn);
    }

    // Loop over sMSD atoms and calculate the sMSD
    for (const auto& atom : smsd_atoms) {
        save_smsd_data(unwrapped_coords, atoms, atom, timestep_md, tau_steps_dyn);
    }

    // Loop over autocorrelation pairs and calculate the autocorrelation
    for (const auto& pair : autocorr_pairs) {
        save_autocorr_data(unwrapped_coords, atoms, pbc, pair[0], pair[1], timestep_md, tau_steps_dyn);
    }
}

//#################################
//## MAIN FUNCTION FROM TERMINAL ##
//#################################

int terminal_input(const std::vector<std::string>& args) {
    int no_cpus = 16; // Default number of CPUs
    omp_set_num_threads(no_cpus);  // Set number of threads
    std::cout << "Analysis script starts on " << no_cpus << " cores." << "\n";

    // Check if the correct number of arguments are provided
    if (args.size() < 4) {
        std::cerr << "Usage: " << " <xyzFilename> <pbcFilename> <timestep in fs> <atom_types> \n";
        return 1; // Exit with error code
    }

    // Parse the command-line arguments
    std::string xyzFilename = args[0];           // First argument: XYZ file name
    std::string pbcFilename = args[1];           // Second argument: PBC file name
    float timestep_md = std::stof(args[2]);      // Third argument: Timestep in fs (convert to float)

    // Additional arguments will be parsed as atom types
    std::vector<std::vector<std::string>> rdf_pairs;  // To store atom pairs for RDF
    std::vector<std::string> msd_atoms;               // To store atoms for MSD
    std::vector<std::string> smsd_atoms;              // To store atoms for single MSD
    std::vector<std::vector<std::string>> autocorr_pairs; // To store atom pairs for autocorrelation

    parse_atom_types(args, rdf_pairs, msd_atoms, smsd_atoms, autocorr_pairs);

    // Print the planned analysis
    std::cout << "Planned analysis:" << "\n";
    if (rdf_pairs.empty()) {
        std::cout << "No RDF pairs provided." << "\n";
    } else {
        std::cout << "RDF pairs: ";
        for (const auto& pair : rdf_pairs) {
            std::cout << pair[0] << "-" << pair[1] << " ";
        }
        std::cout << "\n";
    }
    if (msd_atoms.empty()) {
        std::cout << "No MSD atoms provided." << "\n";
    } else {
        std::cout << "MSD atoms: ";
        for (const auto& atom : msd_atoms) {
            std::cout << atom << " ";
        }
        std::cout << "\n";
    }
    if (smsd_atoms.empty()) {
        std::cout << "No single MSD atoms provided." << "\n";
    } else {
        std::cout << "Single MSD atoms: ";
        for (const auto& atom : smsd_atoms) {
            std::cout << atom << " ";
        }
        std::cout << "\n";
    }
    if (autocorr_pairs.empty()) {
        std::cout << "No autocorrelation pairs provided." << "\n";
    } else {
        std::cout << "Autocorrelation pairs: ";
        for (const auto& pair : autocorr_pairs) {
            std::cout << pair[0] << "-" << pair[1] << " ";
        }
        std::cout << "\n";
    }


    // Output the parsed values for verification
    std::cout << "XYZ Filename: " << xyzFilename << "\n";
    std::cout << "PBC Filename: " << pbcFilename << "\n";
    std::cout << "Timestep in fs: " << timestep_md << "\n";
    
    // Call the compute_analysis function
    compute_analysis(xyzFilename, pbcFilename, timestep_md, rdf_pairs, msd_atoms, smsd_atoms, autocorr_pairs);

    return 0;
}

