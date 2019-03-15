#!/usr/bin/env python3

import yaml
import pandas as pd
import argparse
import os
import in_place
import logging
import shutil
import sys
import re


logging.basicConfig(level=logging.INFO)


VALID_REPLACEMENTS = {"executable_name": "__EXECUTABLE_NAME__",
                      "software": "__SOFTWARE__",
                      "software_quay": "__SOFTWARE_QUAY__",
                      "version": "__VERSION__",
                      "version_quay": "__VERSION_QUAY__",
                      "clean_env": "__CLEAN_ENV__",
                      }

# Globals
subdirs = {"module_dir": "module",
           "shell_dir": "shell",
           "singularity_dir": "image",
           "binary_dir": "bin"}

args_list = ["module_template", "bash_template", "singularity_template"]

singularity_keys = ['runscript', 'run', 'labels', 'help', 'env', 'environment', 'post', 'install']


def get_args():
    parser = argparse.ArgumentParser(description="Import a yaml file and write out all of the "
                                                 "containers and modules you need. This doesn't"
                                                 "build the container but does:"
                                                 "1 Create a recipe for the container to be built"
                                                 "2 Creates bash scripts(s) to wrap around runscripts "
                                                 "in the container"
                                                 "3 Creates modules files that link to the container"
                                                 "4 Creates an installation file to also be built.")

    # Input and outputs
    parser.add_argument("--yaml", type=str, required=True, help="Path to yaml file")
    parser.add_argument("--output-dir", type=str, required=False, default=os.getcwd(),
                        help="Write scripts to stdout")

    # Specify template files
    parser.add_argument("--module-template", type=str, required=False, default=None,
                        help="Provide a module template")
    parser.add_argument("--bash-template", type=str, required=False, default=None,
                        help="Provide a bash template")
    parser.add_argument("--singularity-template", type=str, required=True, default=None,
                        help="Provide a singularity template")

    return parser.parse_args()


def check_args(args):
    # Make sure yaml exists
    if not os.path.isfile(args.yaml):
        logging.info("Error, yaml file must exists, cannot find %s" % args.yaml)
        sys.exit(1)

    # Make sure output-dir can be created
    if not os.path.isdir(os.path.dirname(os.path.abspath(args.output_dir))):
        logging.error("Error, cannot create dir %s, make sure its parent exists" % args.output_dir)
        sys.exit(1)

    # Create output
    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)

    # Check each file exists first
    for arg in args_list:
        if getattr(args, arg, None) is not None:
            if not os.path.isfile(getattr(args, arg)):
                logging.info("Error could not find file %s" % getattr(args, arg))


def create_subdirs(output_dir, args):
    software_subdirs = {}
    # Create folders based on templates available
    subdir_list = ["module_dir", "shell_dir", "singularity_dir"]
    # Create directories
    for subdir, arg in zip(subdir_list, args_list):
        if getattr(args, arg, None) is not None:
            software_subdirs[subdir] = os.path.join(output_dir, subdirs[subdir])
            if not os.path.isdir(software_subdirs[subdir]):
                os.makedirs(software_subdirs[subdir])
            # Also create binary dir if it doesn't exist
            if subdir == 'shell_dir':
                software_subdirs['binary_dir'] = os.path.join(output_dir, 'bin')
                if not os.path.isdir(software_subdirs['binary_dir']):
                    os.makedirs(software_subdirs['binary_dir'])

    return software_subdirs


def import_yaml(yaml_file):
    # Open file
    with open(yaml_file, 'r') as f:
        config_data = yaml.load(f)
    # Load as pandas dataframe
    return pd.io.json.json_normalize(config_data)


def modify_template(yaml_item, template_file, app=None):
    with in_place.InPlace(template_file) as file:
        for line in file:
            for key, value in VALID_REPLACEMENTS.items():
                line = line.replace(str(value), str(yaml_item[key]))

            # Manually add SOFTWARE_UPPER
            if "__SOFTWARE_UPPER__" in line:
                line = line.replace("__SOFTWARE_UPPER__", yaml_item["software"].upper())
            if "__BIND_PATHS_ARRAY__" in line:
                line = line.replace("__BIND_PATHS_ARRAY__", "(%s)" % ' '.join("%s" % array
                                                                              for array in yaml_item['bind_paths']))
            if "__BIND_PATHS__" in line:
                line = line.replace("__BIND_PATHS__", "(%s)" % ' '.join("%s" % array
                                                                         for array in yaml_item['bind_paths']))
            if '__APP__' in line:
                if app is None:
                    line = line.replace("__APP__", "")
                else:
                    line = line.replace("__APP__", app['name'])
            file.write(line)


def modify_singularity_template(yaml_item, template_file, app=None, app_name=None):
    """
    For appending apps to singularity file and initialising singularity file
    :param yaml_item:
    :param template_file:
    :return:
    """
    with open(template_file, 'a') as recipe_h:
        if app is None:
            # Work with series data
            for key in singularity_keys:
                value = getattr(yaml_item, key, None)
                if value is not None:
                    recipe_h.write("%%%s\n" % key)
                    recipe_h.write("%s\n" % value)
        # Work with app data
        else:
            for key in singularity_keys:
                if key in app.keys():
                    recipe_h.write("%%app%s %s\n" % (key, app_name))
                    recipe_h.write("%s\n" % app[key])


def main():
    # Get args
    args = get_args()

    # Check files/directories exist
    check_args(args)

    # Import yaml
    config_df = import_yaml(args.yaml)

    # Break by name into list of dfs
    items = list(set([col.rsplit('.', 1)[0] for col in config_df.columns]))
    config_dfs = [config_df.filter(axis='columns', regex='^%s' % software_version).\
                  rename(columns=lambda x: re.sub("%s." % software_version, "", x)).\
                  dropna(axis='rows').\
                  reset_index().\
                  transpose()[0]
                  for software_version in items]

    # Iterate through each config and generate module, bash and singularity file
    for item in config_dfs:
        # Create subdirs for module, image and shell
        software_subdirs = create_subdirs(os.path.join(args.output_dir, item.software, item.version), args)
        # Copy and modify over module template
        if args.module_template is not None:
            # Set names
            module_file = os.path.join(software_subdirs['module_dir'], 'module')
            # Copy file
            shutil.copy(args.module_template, module_file)
            # Modify module file
            modify_template(item, module_file)

        # Copy over bash template, link to binary and edit
        if args.bash_template is not None:
            # Set names
            bash_file = os.path.join(software_subdirs['shell_dir'], item.executable_name + ".sh")
            binary_file = os.path.join(software_subdirs['binary_dir'], item.executable_name)
            # Copy file
            shutil.copy(args.bash_template, bash_file)
            # Modify bash
            modify_template(item, bash_file)
            # Link to binary
            if os.path.islink(binary_file):
                os.unlink(binary_file)
            os.symlink(os.path.relpath(bash_file, os.path.dirname(binary_file)),
                       binary_file)

        # Copy over singularity template, and modify
        if args.singularity_template is not None:
            # Set names
            singularity_recipe = os.path.join(software_subdirs['singularity_dir'],
                                              '_'.join([item.software, str(item.version)]) + ".recipe")
            singularity_image = os.path.join(software_subdirs['singularity_dir'],
                                             '_'.join([item.software, str(item.version)]) + ".simg")
            # Copy template
            shutil.copy(args.singularity_template, singularity_recipe)
            # Modify template
            modify_template(item, singularity_recipe)
            modify_singularity_template(item, singularity_recipe, app=None)
            # Log executable
            logging.info("Now run 'sudo singularity build %s %s" % (singularity_image, singularity_recipe))

        # Iterate through apps
        if getattr(item, 'apps', None) is None:
            continue

        for app_item in item.apps:
            for app_name, app in app_item.items():
                # Create new executable
                # Copy over bash template, link to binary and edit
                if args.bash_template is not None:
                    # Set names
                    bash_file = os.path.join(software_subdirs['shell_dir'], app['executable_name'] + ".sh")
                    binary_file = os.path.join(software_subdirs['binary_dir'], app['executable_name'])
                    # Copy file
                    shutil.copy(args.bash_template, bash_file)
                    # Modify bash
                    modify_template(item, bash_file, app=app)
                    # Link to binary
                    if os.path.islink(binary_file):
                        os.unlink(binary_file)
                    os.symlink(os.path.relpath(bash_file, os.path.dirname(binary_file)),
                               binary_file)
                # Write to end of recipe
                # Copy over singularity template, and modify
                if args.singularity_template is not None:
                    # Set names
                    singularity_recipe = os.path.join(software_subdirs['singularity_dir'],
                                                      '_'.join([item.software, str(item.version)]) + ".recipe")
                    # Modify template
                    modify_singularity_template(item, singularity_recipe, app=app, app_name=app_name)


if __name__=="__main__":
    main()
