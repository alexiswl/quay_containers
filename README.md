# Quay Containers
Installation of BioContainers through quay. Generate a module, bash wrapper recipe and singularity image ready for take-off on a HPC cluster

[Overall Tutorial](https://alexiswl.github.io/presentations/HPC_and_Singularity/HPC_and_Singularity.html)  
[Presentation](https://alexiswl.github.io/presentations/HPC_and_Singularity/HPC_Singularity_Presentation.html)

## Guide to getting the right values in the yaml.
1. Search for the software through [bioconda](https://bioconda.github.io/)
2. Ensure that the container is 'container ready' as denoted by a light green symbol under the package name.
3. Click on the 'tags' link that will direct you to the [quay.io](https://quay.io/repository/)
4. Use the name of the quay repository for the software_quay item.
5. Use the full name of the tag for the version_quay item

**Example:**  
I intend to install the star package.  
Searching star in bioconda leads me to [here](https://bioconda.github.io/recipes/star/README.html)  
I select [star/tags](https://quay.io/repository/biocontainers/star?tab=tags) to see the quay repo.  
I decide to install star version 2.7.0,   
so I specify `software_quay` as 'star' and `version_quay` as '2.7.0d--0'  
I then run the following
```
create_container_from_quay \
--yaml yamls/star.yaml \
--output-dir containers \
--module-template templates/module \
--bash-template templates/bash_wrapper.sh
--singularity-template templates/Singularity._quay_.File 
```

## Some extra goodies

### Adding all your files to the git repo
```
for file in `find -L containers -type f -not -name '*.simg'`; do 
git add $file;
done
```

### Building all recipes concurrently
```
for recipe in `find containers -name '*.recipe'`; do
# Get image
image=${recipe%.recipe}.simg
# Build image
sudo singularity build $image $recipe
done
```

### I've built all my containers
### I'm ready to move them to the specified container repo on my HPC
Chances are, your module files want to go to your  `MODULEPATH` 
so we'll leave them behind.
```
rsync --links --archive --prune-empty-dirs \
      --include='*/' --exclude='module' \
      --verbose
      containers/ /path/to/containers/
```

### Hard-code the CONTAINER_DIR environment variable for all my modules
In each module template, the __CONTAINER_DIR__ variable component remains unset.  
This way, modules are transferrable between HPC clusters and organisations.  
To customise this to your HPC the following code should suffice.  
You may wish to also fork this repo and change the module template.  

```
MY_CONTAINER_DIR=/path/to/containers
for module in `find containers -type f -name module`; do
sed -i "s%__CONTAINER_DIR__%${MY_CONTAINER_DIR}%g" ${module}
done
```

### Copy across all my modules
```
MY_MODULESPATH=/path/to/modules
for module in `find containers -type f -name module`; do
# Get software 
software=$(basename $(dirname $(dirname $(dirname ${module}))))
# Get version
version=$(basename $(dirname $(dirname ${module})))
# Create software directory if it doesn't exist
mkdir -p /path/to/modules/$software
# Copy module over to software 
cp $module ${MY_MODULESPATH}/$software/$version
done
```


## Troubleshooting

### I get a warning complaining that /var/tmp is already mounted
This is likely due to /var/tmp existing during the installation of the job.
`/var/tmp` links to `/tmp` at run-time so likely your `/var/tmp` during installation is also just a link to `/tmp`
#### Solution
Append `rm /var/tmp` to the end of your %post script.
#### Notes
**DO NOT** delete /tmp during post, do not use `rm -rf /var/tmp` as this will likely delete the contents inside `/tmp`.
Since `/tmp` is mounted to `/tmp` to build time
This is the entire host's /tmp directory.

### I get an error about locales not being able to be set.
If your container has been created with busybox, you're out of luck.
Your best bet is to use the bioconda singularity template.
You'll need to rename the version_quay item in the yaml to the version in bioconda 
and use the Singularity._bioconda_.File template rather than the quay template.

See the picard 2.18.27 recipe for as an example.

### Can I use a dry-run mode to see what's going on underneath.
Check out the help component of the module file.  
You should see by specifying DRY_RUN_\<SOFTWARE\> to '1', that you can enter dry-run mode for a given software.  
You can also see the environment that the software would be running in by setting the dry-run environment variable to 2.


```
# I want to see what STAR would run (but not actually run it)
module load star
export DRY_RUN_STAR=1
STAR --help
```
