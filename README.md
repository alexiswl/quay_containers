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
--bash-template templates/bash_wrapper.sh \
--singularity-template templates/Singularity._quay_.File 
```

## Git Help
### Adding all your files to the git repo
```
for file in `find -L containers -type f -not -name '*.simg'`; do 
git add $file;
done
```

### Adding just one of your software packages to the git repo
```
package_name='my_package'
for file in `find -L containers/${package_name} -type f -not -name '*.simg'`; do 
git add $file;
done
```

### Check what has been staged (added to git but not committed)
```
git diff --name-only --cached
```

### Check what has **not** been staged (not added to the git repo)
```
git diff --name-only
```

## Some extra goodies

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
HPC_CONTAINER_PATH=/path/to/containers
rsync --links --archive --prune-empty-dirs \
      --include='*/' --exclude='module' \
      --verbose \
      containers/ ${HPC_CONTAINER_PATH}/
```

### Hard-code the CONTAINER_DIR environment variable for all my modules
In each module template, the __CONTAINER_DIR__ variable component remains unset.  
This way, modules are transferrable between HPC clusters and organisations.  
To customise this to your HPC the following code should suffice.  
You may wish to also fork this repo and change the module template.  

```
HPC_CONTAINER_PATH=/path/to/containers
for module in `find containers -type f -name module`; do
sed -i "s%__CONTAINER_DIR__%${HPC_CONTAINER_PATH}%g" ${module}
done
```

### Copy across all my modules
```
HPC_MODULEPATH=/path/to/modules
for module in `find containers -type f -name module`; do
# Get software 
software=$(basename $(dirname $(dirname $(dirname ${module}))))
# Get version
version=$(basename $(dirname $(dirname ${module})))
# Create software directory if it doesn't exist
mkdir -p ${HPC_MODULEPATH}/$software
# Copy module over to software 
rsync --checksum $module ${HPC_MODULEPATH}/$software/$version
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
#### Example Case
fgbio/0.8.0

### I get an error about locales not being able to be set.
If your container has been created with busybox, you're out of luck.

#### Solution
Your best bet is to use the bioconda singularity template.
You'll need to rename the version_quay item in the yaml to the version in bioconda 
and use the Singularity._bioconda_.File template rather than the quay template.

#### Example Case
See the picard 2.18.27 recipe for as an example.

### Can I use a dry-run mode to see what's going on underneath.
Check out the help component of the module file.  
You should see by specifying DRY_RUN_\<SOFTWARE\> to '1', that you can enter dry-run mode for a given software.  
You can also see the environment that the software would be running in by setting the dry-run environment variable to 2.

### I get this Java error complaining about an UnknownHostException

#### Solution 
The quay container has a rogue link to it's /etc/resolv.conf. By default Singularity will mount this at runtime from the host (so it doesn't need to exist). In this case you will need to remove the link during the %post script.

#### Example case
See the fgbio 0.8.0 recipe as an example.

```
# I want to see what STAR would run (but not actually run it)
module load star
export DRY_RUN_STAR=1
STAR --help
```
