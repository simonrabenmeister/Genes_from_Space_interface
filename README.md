# Genes_from_Space_interface
A user interface designed with streamlit pyhton package to create input forms for Bon in a Box which is a biodiversity monitoring Tool. It is designed to autofill the Inputs for the Genes from Space pipelines on Bon in a Box. 

Bon in a Box: https://github.com/GEO-BON/bon-in-a-box-pipelines/tree/main  <br /> 
Streamlit Documentation: https://docs.streamlit.io/  <br /> 
Genes from Space: https://teams.issibern.ch/genesfromspace/monitoring-tool-backup/  <br /> 

## Quick start:
-> create a conda environment with all dependencies (see requirements.txt)
-> run app with: streamlit run streamlit.py --server.port 8080

## FAQ:

### About genetic diversity (e.g. for non geneticists):

<details closed>
<summary>What is genetic diversity?</summary>
<br>
  
Genetic diversity is variation at the DNA level, the DNA sequence, which, together with the environment where an organism lives, determines its individual phenotype (appearance, traits, etc.) and its survival. There is variation within populations and among populations. More genetic diversity can increase a population or species’ chances of survival in a changing environment.
</details>

<details closed>
<summary>How do you study genetic diversity?</summary>
<br>
  
For more than 40 years scientists have used molecular genetic techniques that can assess variation at the DNA level. There are many techniques that study either the whole genome (all DNA of an individual) or selected parts of it. One needs to collect tissue from many individuals over the study region to get good knowledge of where genetically distinct populations are and how much variation occurs within populations as well as between populations. DNA is extracted from the tissue and then analyzed to quantify genetic variation. These molecular lab procedures are not available for all species because they can still be expensive and require accessing the organisms’ tissues, for many organisms in a species.
</details>

<details closed>
<summary>How can you study genetic diversity from space?</summary>
<br>
  
We cannot assess DNA variation from space, but it is possible to measure some of the processes that affect the maintenance of genetic diversity and, in some cases, observe parts of the phenotype. Very small populations will lose genetic diversity faster. Also, loss of populations results in a loss of genetic diversity. From space, we can estimate the size of particular habitats, and with knowledge on the density of individuals of species in such habitats, you can roughly estimate the size of populations. Also, we can measure the loss of populations as lost habitat (e.g., conversion of habitat to non-habitat). Finally, for some organisms like large dominant trees, we can directly observe some of their traits and how variable those are. (Trait or phenotype information is not yet used in the “Genes from Space” tool, but we aim to use it in the future.) For more information, please see our preprint [here](https://ecoevorxiv.org/repository/view/7274/).
</details>

<details closed>
<summary>What is the point of indicators/ why do we have indicators?</summary>
<br>
  
Indicators are needed to measure trends over time, for reporting and then directing action or decision-making. For genetic diversity, there are several metrics that measure genetic diversity within and between populations that we need to follow to see if we maintain genetic diversity or not. You can read more about the genetic indicators “Proportion of populations with Ne > 500” and “Populations maintained” [here](https://ccgenetics.github.io/guidelines-genetic-diversity-indicators/).
</details>

<details closed>
<summary>What is a population/ how are populations genetically defined?</summary>
<br>
  
A population is a group of organisms of a species that can interact with and mate with each other and which are separated in some way from other groups. This is important for genetic diversity because populations can evolve adaptations to their local environment over time. For more information on defining populations, please see this guidance material [here](https://ccgenetics.github.io/guidelines-genetic-diversity-indicators/docs/3_Howto_guides_examples/Howto_define_populations.html).
</details>

<details closed>
<summary>When do countries need to report on indicators under the CBD GBF?</summary>
<br>
  
The deadline for submitting the seventh national report is 28 February 2026, and the eighth national report is 30 June 2029 (see CBD website [here](https://www.cbd.int/reports)).
</details>

<details closed>
<summary>How many species do countries need to report on?</summary>
<br>

There is not a mandatory minimum, but scientists recommend reporting indicators for at least 100 species for the seventh national report, and more over time as capacity increases.
</details>

<details closed>
<summary>What species do countries need to report on?</summary>
<br>
  
All types of species (birds, mammals, plants, etc.), ideally in all types of environments. For more information on this, check [here](https://ccgenetics.github.io/guidelines-genetic-diversity-indicators/docs/4_Species_list/Species_list.html).
</details>

<details closed>
<summary>Which indicators for genetic diversity exist?</summary>
<br>
  
Two established indicators for genetic diversity under the CBD framework are the focus of the Genes from Space tool. These are the “Proportion of populations within species with an Ne > 500,” which is especially important (a headline indicator), and “Proportion of populations maintained within species.” They can be measured with DNA data but also with proxies in case DNA data is not available. A proxy for Ne is Nc, or in the case of this tool, habitat area combined with density estimates.

There are also indicators that can be measured with DNA-based techniques. DNA-based indicators are based on Essential Biodiversity Variables for genetic diversity ([EBVs](https://onlinelibrary.wiley.com/doi/10.1111/brv.12852)), such as genetic diversity, inbreeding levels, effective size, and genetic differentiation. Examples of such work include [fish](https://onlinelibrary.wiley.com/doi/full/10.1111/mec.16710) and [moose](https://www.nature.com/articles/s42003-023-05385-x).
</details>

<details closed>
<summary>What is Ne?</summary>
<br>
  
Ne is an abbreviation for the genetically effective population size. It is a standard metric in population genetics that quantifies the size of a demographically ideal population with the same rate of genetic diversity loss as the real population. It is important because it relates to the adaptive capacity and long-term viability of a population. It can be estimated with DNA-based methods or from demographic data (birth- and death rates, reproductive rates, etc). An Ne > 500 is recommended as a minimum limit for a population to maintain adaptive capacity. Ne is useful because it is a metric we can apply to all species.
</details>

<details closed>
<summary>What is Nc?</summary>
<br>
  
Nc is the census size, or the number of sexually mature individuals in a population.
</details>

<details closed>
<summary>Where can I read more about genetic diversity indicators?</summary>
<br>
  
Two major resources for learning more about the genetic indicators are:

- Background: *[Too simple, too complex, or just right? Advantages, challenges, and guidance for indicators of genetic diversity](https://academic.oup.com/bioscience/article/74/4/269/7625302)*
- Actually calculating genetic indicators using existing data on species: *[Guideline materials and documentation for the Genetic Diversity Indicators of the monitoring framework for the Kunming-Montreal Global Biodiversity Framework](https://ccgenetics.github.io/guidelines-genetic-diversity-indicators/)* 
  
</details>

---

### About the Tool

<details closed>
<summary>Where can I find the tool? Is there a manual for users?</summary>

The tool can be found here: [https://www.gfstool.com/]. This is a version for testing: Please note the disclaimers and other information on the tool website.  
There is no manual yet, but an introduction is provided [here](https://teams.issibern.ch/genesfromspace/monitoring-tool-pilot/), and the tool website will walk you step-by-step through the use of the tool and the assumptions the current version is based on.

</details>

<details closed>
<summary>Is it free to use? Can I use this now for other purposes? Is it copyrighted?</summary>

The tool is under development and its use for commercial purposes is prohibited. Participation in the workshop also means that you agree to not use the tool for your own scientific purposes until the results from the Genes from Space workshop are published (at least as a preprint). Please keep in mind that workshop participants are also invited to contribute as co-authors to this initial publication.

</details>

<details closed>
<summary>Can I use the tool for calculating indicators for reporting to the CBD?</summary>

No, not yet, because it is still under development. The tool has not been sufficiently tested or validated. However, we are in the process of improving this tool and getting it ready for future practical use, including for the CBD.

</details>

<details closed>
<summary>Where can I get help to use the tool if running into problems?</summary>

Contact information for the ISSI Genes from Space team can be found [here](https://teams.issibern.ch/genesfromspace/team-member/).

</details>

<details closed>
<summary>Can the tool be used for all species? Which species should the tool NOT be used for?</summary>

The tool will run for any species, but it might not be appropriate for all species. We have not yet defined which species the tool will work best for, but we are aware of the following limitations given the current implementation:  
- Species with inaccurate entries in GBIF will not be accurately represented in this tool if you rely on GBIF entries. This does not apply if you provide your own coordinates.  
- We do not currently implement definitions for aquatic habitats and are working on implementing this. However currently, the tool is limited to use for terrestrial species.  
- Accuracy of the results currently depend on realistic estimates of population density to retrieve an Nc accurate to at least the correct order of magnitude.

</details>

<details closed>
<summary>Has the tool been validated for genetic diversity measured with DNA methods?</summary>

Not yet, but we plan to do so in near future.

</details>

<details closed>
<summary>How do I refer to the tool if I use it?</summary>

Please wait until we have provided the initial publication of the tool, at least in preprint form [here](https://ecoevorxiv.org/repository/view/7274/). At that time the tool will be opened for use given that the terms of use and limitations are respected, and the (preprinted) publication should then be cited.

</details>

<details closed>
<summary>How do I pick the density and population buffer sizes?</summary>

The density should be an estimate of the number of sexually mature (capable of reproducing) individuals (Nc, census size) per square kilometer, in normal habitat.  
The population buffer size should be determined based on knowledge of the typical dispersal distance of the species. For species with larger dispersal distances, including the exchange of gametes (e.g. pollen, sperm), the buffer should be larger. The best reference will be literature documenting the mating and dispersal behavior of the species or, if available, documenting genetic differentiation for a set of representative study populations.

</details>

---

### Technical questions about running the tool

<details closed>
<summary>GBIF does not recognize my species name</summary>

- If you provide your own data, this does not matter, only if you need GBIF data.  
- Check the use of capital letters (usually Genus species).  
- Check spelling.

</details>

<details closed>
<summary>I can not import my .csv coordinate file.</summary>

The monitoring tool requires a .tsv file (tab separated).  
Quick fix: Export a .txt file and change the ending to .tsv.

</details>

<details closed>
<summary>My excel uses commas to export and not periods.</summary>

This happens if your Excel is set to use commas for the decimal separator.  
Either change the above settings or save as a .txt file, search and replace commas with periods.

</details>

<details closed>
<summary>How do I draw the bounding box?</summary>

Click on the square on the left and then drag to select the region of interest on the map.

</details>

<details closed>
<summary>My buffer/observation distance values are rather small and in [m] not [km].</summary>

If your observation distance is smaller than 1 km, please enter 1 km into the tool. Buffers smaller than 1 km are a functionality that we will consider adding in the future.

</details>

<details closed>
<summary>Should I use Landcover or Forest cover?</summary>

- Landcover gives you more options and a longer timeline: 23 classes, 300m, 1992-2021, select relevant class.  
- Forest cover provides better resolution, but only for species dependent on forest ecosystems: forests, 20m, 2000-2023.  
Forest cover is much slower: Use a smaller polygon (max. 40’000 km2, size of Switzerland).

</details>

<details closed>
<summary>I get the Error: 
Script "data > GBIF Observations < 100 000": ℹ In argument: `dplyr::all_of(c(lon, lat))`.
Caused by error in `dplyr::all_of()`:
! Can't subset elements that don't exist.
✖ Elements `decimal_longitude` and `decimal_latitude` don't exist.
What do I do?</summary>

No GBIF data found for you selected region/country. Select a larger/different polygon, earlier baseline year or a different species of interest.

</details>

---

### About the Project

<details closed>
<summary>Where can I find more information about the project and its background?</summary>

You can read about the project ISSI Genes from Space [here](https://teams.issibern.ch/genesfromspace/).

</details>

<details closed>
<summary>Can I join the project or contribute in some way?</summary>

Please contact the team leaders, whose webpages are linked [here](https://teams.issibern.ch/genesfromspace/team-member/).

</details>

<details closed>
<summary>What is the next step of the project?</summary>

Making technical improvements to the tool.  
Publishing a first demonstration of the tool.  
Validating the tool outputs in comparison to DNA-based indicator calculations to make it useful for research, reporting, and conservation.  
Adding capacities to the tool to include population boundaries based on genetic data and make use of more nuanced habitat and phenotype information available from Earth observation.

</details>

<details closed>
<summary>What are you going to do with the results that we collect?</summary>

Use these for the first demonstration publication, to which you are invited to contribute as a co-author.

</details>

<details closed>
<summary>Are there publications from the project?</summary>

There is a publication about the concept and workflows [here](https://doi.org/10.32942/X2RS58).

</details>
