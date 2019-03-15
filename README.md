# Quay Containers
Installation of BioContainers through quay. Generate a module, bash wrapper recipe and singularity image ready for take-off on a HPC cluster

[Overall Tutorial](https://alexiswl.github.io/presentations/HPC_and_Singularity/HPC_and_Singularity.html)  
[Presentation](https://alexiswl.github.io/presentations/HPC_and_Singularity/HPC_Singularity_Presentation.html)

# Troubleshooting

## I get a warning complaining that /var/tmp is already mounted
This is likely due to /var/tmp existing during the installation of the job.
`/var/tmp` links to `/tmp` at run-time so likely your `/var/tmp` during installation is also just a link to `/tmp`
Append `rm /var/tmp` to the end of your %post script.
**DO NOT** delete /tmp during post, do not use `rm -rf /var/tmp` as this will likely delete the contents inside `/tmp`.
Since `/tmp` is mounted to `/tmp` to build time
This is the entire host's /tmp directory.

## I get an error about locales not being able to be set.
If your container has been created with busybox, you're out of luck.
Your best bet is too use the miniconda3 base and install the locales, then install through bioconda.
See the picard example below.


```
%files
# Move to final spot during %post
locale.gen /etc/locale.gen.tmp
locale.alias /etc/locale.alias.tmp

%post
export PATH=/opt/conda/bin:$PATH
# Install locales
apt-get update
apt-get install debconf locales -y
dpkg-reconfigure locales
# Move added files
mv /etc/locale.gen.tmp /etc/locale.gen
mv /etc/locale.alias.tmp /etc/locale.alias
# Link to /usr/share/locale
mkdir -p /usr/share/locale
ln -sf /etc/locale.alias /usr/share/locale/locale.alias
# Reset locales
locale-gen
# install picard
conda install -c bioconda picard=2.18.27
```