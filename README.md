# Thin-Film-Model

A model I built to simulate light propagation through a thin film stack.

To use the script, build the film stack by creating a list with the material names, as they are given in the ./materials/ folder.
New materials can be added by adding new .csv files to ./materials. They should be formatted like the files at refractiveindex.info.
There should be N materials given, where the first is the environment materials ('Air' for many applications) and the last is the
substrate material. There should be N-2 thicknesses given, where each thickness corresponds to a layer in the stack (i.e. not the
environment or the substrate).

Once the stack is created, the wavelengths and angles of incidence should be given with the get_coeffs() method to compute the
reflection and transmission coefficients for the P- and S-polarization states, as well as unpolarized light, at each point on
the wavelength/angle-of-incidence grid. Absorption can be computed as 1-R-T for any of the polarization states.

<img width="607" height="314" alt="image" src="https://github.com/user-attachments/assets/85203e4a-a0b5-45e7-a0d2-6117a97ac1eb" />

Example transmission curve output for normal incidence.
<img width="400" height="300" alt="image" src="https://github.com/user-attachments/assets/067695d9-a0db-4cb3-b451-a8a143fbf9e4" />
